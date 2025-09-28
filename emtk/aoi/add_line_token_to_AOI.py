import os
import pandas as pd

def add_line_token_to_AOI(file_path, aois_raw):
    """
    For AOIs of kind 'line', append the entire corresponding line of code as the 'token'.
    Args:
        file_path (str): Directory containing code files.
        aois_raw (pd.DataFrame): DataFrame with AOI definitions, must include 'image', 'kind', and 'name'.
    Returns:
        pd.DataFrame: AOI DataFrame with a new 'token' column for 'line' AOIs.
    """
    # Map image filename to code filename (customize as needed)
    image_to_code = {
        'rectangle_java.jpg': 'Rectangle.java',
        'vehicle_java.jpg': 'Vehicle.java',
        'vehicle_java2.jpg': 'Vehicle.java',
        'rectangle_java2.jpg': 'Rectangle.java',
        # Add more mappings as needed
    }

    # Get the code filename from the first AOI image
    image_name = aois_raw['image'].iloc[0]
    code_filename = image_to_code.get(image_name)
    if not code_filename:
        raise ValueError(f"No code file mapping for image: {image_name}")
    code_file = os.path.join(file_path, code_filename)
    if not os.path.exists(code_file):
        raise FileNotFoundError(f"Code file not found: {code_file}")

    # Read code lines, skipping empty lines
    with open(code_file, 'r', encoding='utf-8') as f:
        code_lines = [line.rstrip('\n') for line in f if line.strip()]

    # Filter AOIs of kind 'line'
    line_aois = aois_raw[aois_raw['kind'] == 'line'].copy()
    tokens = []
    for idx, row in line_aois.iterrows():
        # Extract line number from AOI name (assumes format 'line_X' or similar)
        name = row['name']
        try:
            line_num = int(name.split(' ')[-1]) - 1  # AOI line numbers are 1-based
            token = code_lines[line_num].strip() if 0 <= line_num < len(code_lines) else ''
        except Exception:
            token = ''
        tokens.append(token)
    line_aois['token'] = tokens
    return line_aois
