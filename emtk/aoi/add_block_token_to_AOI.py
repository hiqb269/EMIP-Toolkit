import os
import pandas as pd

def add_block_token_to_AOI(file_path, aois_raw):
    """
    For line AOIs, assign block numbers and group into block-level AOIs.
    
    Args:
        file_path (str): Directory containing code files.
        aois_raw (pd.DataFrame): DataFrame with AOI definitions from find_aoi().
        block_definitions (dict): Maps block names to line ranges.
                                  Format: {"Block name": [start_line, end_line]}
    
    Returns:
        pd.DataFrame: Block-level AOI DataFrame with columns:
                     ['aoi_type', 'aoi_name', 'aoi_content', 'x0', 'y0', 'width', 'height']
    """
    # Map image filename to code filename
    image_to_code = {
        'rectangle_java.jpg': 'Rectangle.java',
        'vehicle_java.jpg': 'Vehicle.java',
        'vehicle_java2.jpg': 'Vehicle.java',
        'rectangle_java2.jpg': 'Rectangle.java',
    }

    vehicle_blocks = {
        "Class declaration": [1, 1],
        "Field declarations": [2, 3],
        "Constructor block": [4, 9],
        "Accelerate method header": [10, 10],
        "Accelerate method body": [11, 17],
        "Main method header": [18, 18],
        "Object creation": [19, 19],
        "Method call": [20, 20]
        #"Main block":[18,21]
        #"Class end": [22,22]
    }

    rectangle_blocks = {
        "Class declaration": [1, 1],
        "Field declarations": [2, 2],
        "Constructor block": [3, 8],
        "Utility methods (width, height, area)": [9, 11],
        "Main method block": [12, 16]
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
    line_aois = aois_raw[aois_raw['kind'] == 'block'].copy()
    
    # Add line numbers and tokens
    line_aois['line_num'] = line_aois['name'].apply(lambda x: int(x.split(' ')[-1]))
    tokens = []
    for idx, row in line_aois.iterrows():
        line_num = row['line_num'] - 1  # 1-based to 0-based
        token = code_lines[line_num].strip() if 0 <= line_num < len(code_lines) else ''
        tokens.append(token)
    line_aois['token'] = tokens

    if code_filename == "Vehicle.java":
        block_definitions = vehicle_blocks
    elif code_filename == "Rectangle.java":
        block_definitions = rectangle_blocks

    
    # Assign block numbers based on block_definitions
    line_aois['block_name'] = ''
    for block_name, (start_line, end_line) in block_definitions.items():
        mask = (line_aois['line_num'] >= start_line) & (line_aois['line_num'] <= end_line)
        line_aois.loc[mask, 'block_name'] = block_name
    
    # Group lines into blocks
    block_aois = []
    for block_name in line_aois[line_aois['block_name'] != '']['block_name'].unique():
        block_lines = line_aois[line_aois['block_name'] == block_name]
        
        # Calculate bounding box
        x0 = block_lines['x'].min()
        y0 = block_lines['y'].min()
        x1 = (block_lines['x'] + block_lines['width']).max()
        y1 = (block_lines['y'] + block_lines['height']).max()
        
        # Combine tokens
        content = '\n'.join(block_lines['token'].tolist())
        
        block_aois.append({
            'aoi_type': 'block',
            'aoi_name': block_name,
            'aoi_content': content,
            'x0': x0,
            'y0': y0,
            'width': x1 - x0,
            'height': y1 - y0
        })
    
    return pd.DataFrame(block_aois)