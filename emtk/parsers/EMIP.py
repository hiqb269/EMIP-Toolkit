import os
from types import NoneType
import pandas as pd

from .eye_events import eye_event_list, get_eye_event_columns
from .samples import get_samples_columns, samples_list
from .gender_mapping import gender_mapping

from emtk.fixation_classification import idt_classifier
from emtk.fixation_classification import ivt_classifier
from emtk.fixation_classification import idt_classifier_old

from .download import download

EYE_TRACKER = "SMIRed250"
FILE_TYPE = ".tsv"
RAWDATA_MODULE = "emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/rawdata"
STIMULI_MODULE = "emtk/datasets/EMIP/EMIP-Toolkit- replication package/emip_dataset/stimuli"

SAMPLE_BASE_COLUMNS = ['Time', 'Type', 'Trial', 'L Raw X [px]', 'L Raw Y [px]', 'R Raw X [px]',
                       'R Raw Y [px]', 'L Dia X [px]', 'L Dia Y [px]', 'L Mapped Diameter [mm]',
                       'R Dia X [px]', 'R Dia Y [px]', 'R Mapped Diameter [mm]', 'L CR1 X [px]',
                       'L CR1 Y [px]', 'L CR2 X [px]', 'L CR2 Y [px]', 'R CR1 X [px]', 'R CR1 Y [px]',
                       'R CR2 X [px]', 'R CR2 Y [px]', 'L POR X [px]', 'L POR Y [px]', 'R POR X [px]',
                       'R POR Y [px]', 'Timing', 'L Validity', 'R Validity', 'Pupil Confidence',
                       'L Plane', 'R Plane', 'L EPOS X', 'L EPOS Y', 'L EPOS Z', 'R EPOS X', 'R EPOS Y',
                       'R EPOS Z', 'L GVEC X', 'L GVEC Y', 'L GVEC Z', 'R GVEC X', 'R GVEC Y',
                       'R GVEC Z', 'Frame', 'Aux1']


def EMIP(sample_size: int = 216, start_index: int = 0, process_raw_samples: bool=True, use_minus_one_for_invalid_gaze: bool=True, classifier="idt", minimum_duration=50, sample_duration=4, maximum_dispersion=25):
    """Import the EMIP dataset.

    Parameters
    ----------
    sample_size : int, optional (default 216)
        Number of subjects to be processed.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe of eye events from every experiment in the dataset.
    """
    eye_events = []
    samples = []
    parsed_experiments = []
    all_stimulus_times = []

    if not os.path.isdir(RAWDATA_MODULE):
        download("EMIP") 


    # go over .tsv files in the rawdata directory add files and count them
    # r = root, d = directories, f = files


    gender_map = gender_mapping() # Load the gender from metadata
    #print(f"Processing {sample_size} participants starting at {start_index+1}")
    for r, _, f in os.walk(RAWDATA_MODULE):
        f = [name for name in f if name and name[0].isdigit() and '.tsv' in name]
        f.sort(key=lambda name: int(name.split('_')[0]))
        f = f[start_index:]  # Start from the given index
        for file in f:
            if '.tsv' in file:
                experiment_id = file.split('/')[-1].split('_')[0] #Experiment_id refers to participant ID

                if experiment_id not in parsed_experiments:

                    parsed_experiments.append(experiment_id)

                    #Get gender for this participant
                    participant_gender = gender_map.get(experiment_id, None)
                    if participant_gender is None:
                        print(f"Warning: No gender data found for participant {experiment_id}")
                        participant_gender = "male"
                    #else:
                    #   print(f"Gender for participant {experiment_id}: {participant_gender}")
                    
                    #print(f"Processing gaze data for participant number {experiment_id} - iteration number {sample_size}")
                    new_eye_events, new_samples, new_stimulus_times = read_SMIRed250(
                        root_dir=r,
                        filename=file,
                        experiment_id=experiment_id,
                        minimum_duration=minimum_duration, 
                        sample_duration= sample_duration, 
                        maximum_dispersion=maximum_dispersion,
                        gender = participant_gender,
                        raw_samples = process_raw_samples,
                        minus_one_invalid=use_minus_one_for_invalid_gaze,
                        fix_classifier = classifier
                    )

                    eye_events.extend(new_eye_events)
                    if process_raw_samples:
                      samples.extend(new_samples)
                    all_stimulus_times.extend(new_stimulus_times)

                else:
                    print("Error, experiment already in dictionary")
                sample_size -= 1
                if sample_size == 0:
                  break

            
    eye_events_df = pd.DataFrame(eye_events, columns=get_eye_event_columns())
    stimulus_times_df = pd.DataFrame(all_stimulus_times,columns=["participant_id", "gender", "trial", "stimulus_name", "start_timestamp", "end_timestamp", "time_spenton_stimuli"])

    print("Finished loading eye events for participants.")
    # Convert columns with numbers formatted as strings to dtype of numeric
    if process_raw_samples:
      samples_df = pd.DataFrame(
        samples, columns=get_samples_columns(SAMPLE_BASE_COLUMNS))
      id_dfs = samples_df[["experiment_id", "participant_id", "trial_id"]]
      #samples_df = samples_df.apply(pd.to_numeric, errors='ignore')
      for col in samples_df.columns:
        try:
          samples_df[col] = pd.to_numeric(samples_df[col])
        except (ValueError, TypeError):
          # Handle columns that cannot be converted to numeric, e.g., leave them as they are
          pass
      samples_df[id_dfs.columns] = id_dfs
      return eye_events_df, samples_df, stimulus_times_df 
    else:
      return eye_events_df, [], stimulus_times_df


def read_SMIRed250(root_dir, filename, experiment_id,
                   minimum_duration=50, sample_duration=4, maximum_dispersion=25, gender = None, raw_samples: bool=True, minus_one_invalid: bool=True, fix_classifier ="idt", velocity_threshold=100) -> list:
    """Read tsv file from SMI Red 250 eye tracker

    Parameters
    ----------
    root_dir : str
        Path to directory that contains the asc file.

    filename : str
        Name of asc file.

    experiment_id : str
        Id of the experiment contained in the file.

    Returns
    -------
    list
        List of eye events. Each eye event is represented as a list of eye event features.
    """

    # Reads raw data and sets up
    tsv_file = open(os.path.join(root_dir, filename))
    #print("parsing file:", filename.split("/")[-1])
    text = tsv_file.read()
    text_lines = text.split('\n')

    trial_id = 0
    stimuli_name = ""
    raw_fixations = []
    active = False  # Indicates whether samples are being recorded in trials
    # The goal is to skip metadata in the file
    
    is_new_stimulus = False
    stimulus_times = []
    img_start_time = None
    img_end_time = None

    eye_events = []
    samples = []
    

    

    # Parses the data into dataframes
    for line in text_lines:
        token = line.split("\t")

        if len(token) < 3:
            continue

        if active:
            # Filter MSG samples if any exist, or R eye is inValid
            
            if token[1] == "SMP":
              if is_new_stimulus:
                img_start_time = int(token[0])
                is_new_stimulus = False
              img_end_time = int(token[0])  
              condition = True
              if minus_one_invalid: 
                condition = token[27] != "-1"
              else:
                condition = token[27] == "1"
                # Get x and y for each sample (right eye only)
                # [23] R POR X [px]	 '0.00',
                # [24] R POR Y [px]	 '0.00',
              if condition:
                  new_sample = samples_list(
                    eye_tracker=EYE_TRACKER,
                    experiment_id=experiment_id,
                    participant_id=experiment_id,
                    filename=filename,
                    trial_id=str(trial_id),
                    stimuli_module=STIMULI_MODULE,
                    stimuli_name=stimuli_name,
                    token=token, 
                    gender = gender
                  )

                  samples.append(new_sample)

                  raw_fixations.append(
                      [int(token[0]), float(token[23]), float(token[24])])

        if token[1] == "MSG" and token[3].find(".jpg") != -1:
            if img_start_time is not None:
              stimulus_times.append([experiment_id, 
                                 gender, 
                                 str(trial_id),
                                 stimuli_name,
                                 img_start_time,
                                 img_end_time,
                                 img_end_time - img_start_time
                                  ])

            if active:
                if fix_classifier == "idt":
                  filter_eye_events = idt_classifier(
                        raw_fixations=raw_fixations,
                        minimum_duration=minimum_duration,
                        sample_duration=sample_duration,
                        maximum_dispersion=maximum_dispersion
                    )
                elif fix_classifier == "ivt":
                  filter_eye_events = ivt_classifier(
                      raw_fixations=raw_fixations,
                      minimum_duration=minimum_duration,
                      velocity_threshold=velocity_threshold
                    )
                elif fix_classifier == "idt_old":
                  filter_eye_events = idt_classifier_old(
                        raw_fixations=raw_fixations,
                        minimum_duration=minimum_duration,
                        sample_duration=sample_duration,
                        maximum_dispersion=maximum_dispersion
                    )
                # TODO saccades

                for timestamp, duration, x_cord, y_cord in filter_eye_events:

                    new_eye_event = eye_event_list(eye_tracker=EYE_TRACKER,
                                                   experiment_id=experiment_id,
                                                   participant_id=experiment_id,
                                                   filename=filename,
                                                   trial_id=str(trial_id),
                                                   stimuli_module=STIMULI_MODULE,
                                                   stimuli_name=stimuli_name,
                                                   duration=duration,
                                                   timestamp=timestamp,
                                                   x0=x_cord,
                                                   y0=y_cord,
                                                   token=token,
                                                   pupil=0,
                                                   eye_event_type="fixation",
                                                   gender = gender)

                    eye_events.append(new_eye_event)

                trial_id += 1

            # Message: vehicle_java2.jpg
            stimuli_name = token[3].split(' ')[-1]
            raw_fixations = []
            is_new_stimulus = True
            img_start_time = None
            img_end_time = None
            active = True

    # Adds the last trial
    if fix_classifier == "idt":
                  filter_fixations = idt_classifier(
                        raw_fixations=raw_fixations,
                        minimum_duration=minimum_duration,
                        sample_duration=sample_duration,
                        maximum_dispersion=maximum_dispersion
                    )
    elif fix_classifier == "ivt":
                  filter_fixations = ivt_classifier(
                      raw_fixations=raw_fixations,
                      minimum_duration=minimum_duration,
                      velocity_threshold=velocity_threshold
                    )
    elif fix_classifier == "idt_old":
                  filter_fixations = idt_classifier_old(
                        raw_fixations=raw_fixations,
                        minimum_duration=minimum_duration,
                        sample_duration=sample_duration,
                        maximum_dispersion=maximum_dispersion
                    )

    if img_start_time is not None:
              stimulus_times.append([experiment_id, 
                                 gender, 
                                 str(trial_id),
                                 stimuli_name,
                                 img_start_time,
                                 img_end_time,
                                 img_end_time - img_start_time
                                  ])

    for timestamp, duration, x_cord, y_cord in filter_fixations:

        new_eye_event = eye_event_list(eye_tracker=EYE_TRACKER,
                                       experiment_id=experiment_id,
                                       participant_id=experiment_id,
                                       filename=filename,
                                       trial_id=str(trial_id),
                                       stimuli_module=STIMULI_MODULE,
                                       stimuli_name=stimuli_name,
                                       duration=duration,
                                       timestamp=timestamp,
                                       x0=x_cord,
                                       y0=y_cord,
                                       token=token,
                                       pupil=0,
                                       eye_event_type="fixation",
                                       gender=gender)

        eye_events.append(new_eye_event)
    #print(trial_id)
    if not raw_samples:
      samples = []

    return eye_events, samples, stimulus_times
    
