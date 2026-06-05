import cv2
import pytesseract
import json
import re
import pandas as pd
from pathlib import Path
import os

STIMULI_MODULE = "emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/stimuli"

def find_semantic_aoi(image_path, pattern_file):
    """
    Extract AOIs (Areas of Interest) from a code image based on configurable JSON regex patterns.

    Parameters
    ----------
    image_path : str | Path
        Path to the code image (e.g. 'vehicle_java2.jpg').
    pattern_file : str | Path
        Path to JSON file containing AOI patterns.

    Returns
    -------
    pandas.DataFrame
        Columns:
        ['aoi_type', 'aoi_name', 'aoi_content', 'x0', 'y0', 'width', 'height']
    """
    image_path = Path(image_path)
    full_image_path = Path(STIMULI_MODULE) / image_path

    pattern_file = Path(pattern_file)
    full_pattern_file = Path(STIMULI_MODULE +'/json') / pattern_file # Assuming patterns are in a 'json' subdirectory

    # Load AOI patterns
    try:
        with open(full_pattern_file, "r", encoding="utf-8") as f:
            patterns = json.load(f)
    except FileNotFoundError:
        print(f"Error: Pattern file not found at {full_pattern_file}")
        return pd.DataFrame() # Return empty DataFrame on error

    # Load image
    img = cv2.imread(str(full_image_path))
    if img is None:
        print(f"Error: Could not open image: {full_image_path}")
        return pd.DataFrame() # Return empty DataFrame on error


    # OCR with bounding boxes
    try:
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return pd.DataFrame() # Return empty DataFrame on error


    # Drop rows without text
    ocr_data = ocr_data.dropna(subset=['text'])
    ocr_data = ocr_data[ocr_data['text'].str.strip() != '']

    # Combine into full lines
    lines = []
    for line_num in sorted(ocr_data['line_num'].unique()):
        line_df = ocr_data[ocr_data['line_num'] == line_num]
        if line_df.empty:
            continue

        text = " ".join(line_df['text'])
        x0 = int(line_df['left'].min())
        y0 = int(line_df['top'].min())
        # Corrected calculation for x1 and y1
        x1 = int((line_df['left'] + line_df['width']).max())
        y1 = int((line_df['top'] + line_df['height']).max())

        lines.append({
            "text": text,
            "x0": x0,
            "y0": y0,
            "width": x1 - x0,
            "height": y1 - y0,
            "line_num": line_num # Keep line_num for accurate token mapping
        })

    aois_list = []
    for line in lines:
        line_text = line['text']
        line_num = line['line_num']
        # Apply patterns to each line
        for pattern_type, regex_patterns in patterns.items():
            for aoi_name, regex in regex_patterns.items():
                # Use re.finditer to find all matches and their positions
                for match in re.finditer(regex, line_text):
                    matched_text = match.group(0)
                    start_index = match.start()
                    end_index = match.end()

                    # Refined approach to find the bounding box for the matched text
                    # Find all words within the matched text and their bounding boxes in ocr_data for this line
                    match_words = matched_text.split()
                    if not match_words:
                        continue # Skip if the match is empty

                    # Find the bounding boxes of all words in the matched text within the original ocr_data for this line
                    word_bboxes = pd.DataFrame()
                    current_char_index = 0
                    for word in match_words:
                        # Find the word in the original line text starting from the current_char_index
                        word_start_in_line = line_text.find(word, current_char_index)
                        if word_start_in_line != -1:
                             # Find the corresponding bounding box in ocr_data based on text and approximate position
                             # This mapping can still be tricky and might need further refinement depending on OCR output
                             word_ocr_bbox = ocr_data[(ocr_data['line_num'] == line_num) &
                                                      (ocr_data['text'].str.contains(re.escape(word), na=False)) &
                                                      (ocr_data['left'] >= line['x0'] + word_start_in_line - 5) & # Approximate position check
                                                      (ocr_data['left'] <= line['x0'] + word_start_in_line + 5)
                                                     ].head(1) # Take the first match


                             if not word_ocr_bbox.empty:
                                 word_bboxes = pd.concat([word_bboxes, word_ocr_bbox])
                                 current_char_index = word_start_in_line + len(word)


                    if not word_bboxes.empty:
                         # Calculate the bounding box that encompasses all the words in the match
                         match_x0 = int(word_bboxes['left'].min())
                         match_y0 = int(word_bboxes['top'].min())
                         match_width = int((word_bboxes['left'] + word_bboxes['width']).max()) - match_x0
                         match_height = int((word_bboxes['top'] + word_bboxes['height']).max()) - match_y0

                         aois_list.append({
                             'aoi_type': pattern_type,
                             'aoi_name': aoi_name,
                             'aoi_content': matched_text,
                             'x0': match_x0,
                             'y0': match_y0,
                             'width': match_width,
                             'height': match_height
                         })

    return pd.DataFrame(aois_list)