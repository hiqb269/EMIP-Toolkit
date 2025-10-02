import os
import pandas as pd
from collections import Counter

METADATA_MODULE = "emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset"
# Load metadata
#METADATA_FILE = '/emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/emip_metadata.csv'
METADATA_FILE = os.path.join(METADATA_MODULE, 'emip_metadata.csv')

def gender_mapping():
    try:
        metadata_df = pd.read_csv(METADATA_FILE)
        print(f"Loaded metadata for {len(metadata_df)} participants")

        # Create a mapping from participant ID to gender
        # Assuming'id' column in metadata corresponds to experiment_id/participant_id
        gender_map = dict(zip(metadata_df['id'].astype(str), metadata_df['gender']))
        print(f"Gender mapping created for {len(gender_map)} participants")
        #print(gender_map)
        gender_counts = Counter(gender_map.values())
        print(f"Males: {gender_counts.get('male', 0)}")
        print(f"Females: {gender_counts.get('female', 0)}")


    except FileNotFoundError:
        print(f"Warning: Metadata file '{METADATA_FILE}' not found. Gender will be set to Male.")
        gender_map = {}
    except Exception as e:
        print(f"Error loading metadata: {e}. Gender will be set to Male.")
        gender_map = {}

    return gender_map