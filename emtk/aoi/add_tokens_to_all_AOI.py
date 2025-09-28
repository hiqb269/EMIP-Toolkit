import pandas as pd
def add_tokens_to_all_AOIs(file_path: str, aois_raw: pd.DataFrame) -> pd.DataFrame:
    all_results = []

    for image_name in aois_raw["image"].unique():
        aois_subset = aois_raw[(aois_raw["image"] == image_name) & (aois_raw["kind"] == "sub-line")].copy()

        # Map image name to code file
        image_to_file = {
            "rectangle_java.jpg": "Rectangle.java",
            "rectangle_java2.jpg": "Rectangle.java",
            "rectangle_python.jpg": "Rectangle.py",
            "rectangle_scala.jpg": "Rectangle.scala",
            "vehicle_java.jpg": "Vehicle.java",
            "vehicle_java2.jpg": "Vehicle.java",
            "vehicle_python.jpg": "vehicle.py",
            "vehicle_scala.jpg": "Vehicle.scala"
        }

        file_name = image_to_file.get(image_name)
        if not file_name:
            print(f"Unknown image: {image_name}")
            continue

        with open(file_path + file_name) as code_file:
            code_lines = code_file.read().replace('\t', '').replace('    ', '').split('\n')
            filtered_lines = [line.split() for line in code_lines if line.strip()]

        tokens = []
        for location in aois_subset["name"]:
            line_part = location.split(' ')
            line_num = int(line_part[1])
            part_num = int(line_part[3])
            try:
                token = filtered_lines[line_num - 1][part_num - 1]
            except IndexError:
                token = ''
                print(f"Missing token at line {line_num}, part {part_num} in {image_name}")
            tokens.append(token)

        aois_subset["token"] = tokens
        all_results.append(aois_subset)

    return pd.concat(all_results, ignore_index=True)