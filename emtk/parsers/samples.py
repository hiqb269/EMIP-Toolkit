def get_samples_columns(token: list = []):
    '''Return a list of base line features for the samples dataframe.

    Returns
    -------
    list
        Base line features for the samples dataframe.
    '''
    base = [
        "eye_tracker",
        "experiment_id",
        "participant_id",
        "filename",
        "trial_id",
        "stimuli_module",
        "stimuli_name",
        "gender",
    ]

    base.extend(token)
    return base


def samples_list(eye_tracker: str, experiment_id: str,
                 participant_id: str, filename: str, trial_id: str, stimuli_module: str,
                 stimuli_name: str, token: list = [],gender: str = "male"):
    '''Store sample features in a list.

    Returns
    -------
    list
        List of sample features' values.
    '''
    base = [
        eye_tracker,
        experiment_id,
        participant_id,
        filename,
        trial_id,
        stimuli_module,
        stimuli_name,
        gender,
    ]

    base.extend(token)

    return base
