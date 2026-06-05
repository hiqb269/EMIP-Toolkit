import json
import os

STIMULI_MODULE = "emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/stimuli/json"

vehicle_patterns = {
    "Class declaration": r"^(public\s+class\s+Vehicle|class\s+Vehicle)",
    "Field declarations": r"(String\s+\w+\s*,\s*\w+|int\s+\w+\s*,\s*\w+)",
    "Constructor block": r"(public\s+Vehicle|def\s+__init__)",
    "Accelerate method header": r"(public\s+int\s+accelerate|def\s+accelerate)",
    "Accelerate method if-condition": r"^\s*if\s*\(",
    "Accelerate method else-branch": r"^\s*else\s*\{?",
    "Return statement": r"^\s*return\b",
    "Main method header": r"(public\s+static\s+void\s+main|def\s+main)",
    "Object creation": r"new\s+Vehicle\s*\(",
    "Method call": r"\.accelerate\s*\("
}

rectangle_patterns = {
    "Class declaration": r"^(public\s+class\s+Rectangle|class\s+Rectangle)",
    "Field declarations": r"(int\s+x1|self\.x1)",
    "Constructor block": r"(public\s+Rectangle|def\s+__init__)",
    "Width method header": r"(public\s+int\s+width|def\s+width)",
    "Height method header": r"(public\s+int\s+height|def\s+height)",
    "Area method header": r"(public\s+double\s+area|def\s+area)",
    "Main method header": r"(public\s+static\s+void\s+main|def\s+main)",
    "Object creation": r"new\s+Rectangle\s*\(",
    "Method call": r"\.area\s*\("
}

def _create_json_pattern():

  # Create the directory if it doesn't exist
  os.makedirs(STIMULI_MODULE, exist_ok=True)
  #print(f"Ensured directory exists: {STIMULI_MODULE}")

  try:
      # Save vehicle_patterns to JSON
      vehicle_patterns_path = os.path.join(STIMULI_MODULE, "vehicle_patterns.json")
      #print(vehicle_patterns_path)
      #print(vehicle_patterns)
      json.dump(vehicle_patterns, open(vehicle_patterns_path, "w"), indent=4)
      print(f"Saved vehicle_patterns.json to {vehicle_patterns_path}")

      # Save rectangle_patterns to JSON
      rectangle_patterns_path = os.path.join(STIMULI_MODULE, "rectangle_patterns.json")
      #print(rectangle_patterns_path)
      #print(rectangle_patterns)
      json.dump(rectangle_patterns, open(rectangle_patterns_path, "w"), indent=4)
      print(f"Saved rectangle_patterns.json to {rectangle_patterns_path}")

  except NameError as e:
      print(f"Error: {e}. Make sure 'vehicle_patterns' and 'rectangle_patterns' are defined.")
  except Exception as e:
      print(f"An error occurred while saving the files: {e}")


