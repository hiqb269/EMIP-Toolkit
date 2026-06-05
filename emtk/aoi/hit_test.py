import pandas as pd


def hit_test(fixations: pd.DataFrame, aoi_df: pd.DataFrame, is_line_level: bool = False, radius: int = 25,
             eye_tracker_col="eye_tracker", experiment_id_col="experiment_id",
             participant_id_col="participant_id", gender_col="gender", filename_col="filename",
             trial_id_col="trial_id", stimuli_module_col="stimuli_module",
             stimuli_name_col="stimuli_name", timestamp_col="timestamp",
             duration_col="duration",
             fixation_x0_col: str = "x0", fixation_y0_col: str = "y0",
             aoi_kind_col: str = "kind", aoi_name_col: str = "name",
             aoi_x_col: str = "x", aoi_y_col: str = "y",
             aoi_width_col: str = "width", aoi_height_col: str = "height",
             aoi_token_col: str = "token", aoi_srcML_tag_col: str = "srcML_tag") -> pd.DataFrame:
    '''Match fixations with their respective AOI.
    A fixation is matched with an AOI if its coordinate is within a specified radius around
    the coordinate of the AOI.

    Parameters
    ----------
    fixations : pandas.DataFrame
        Pandas dataframe of fixations.

    aoi_df : pandas.DataFrame
        A pandas DataFrame of AOIs.

    radius : int, optional (default 25)
        Farthest distance from an AOI that a fixation belongs to it can be.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe that matches fixation with their respective AOI.
    '''

    _fixations = fixations.copy()[[
        eye_tracker_col,
        experiment_id_col,
        participant_id_col,
        gender_col,
        filename_col,
        trial_id_col,
        stimuli_module_col,
        stimuli_name_col,
        timestamp_col,
        duration_col,
        fixation_x0_col,
        fixation_y0_col,
    ]]

    aoi_cols = [aoi_kind_col, aoi_name_col, aoi_x_col,
                aoi_y_col, aoi_width_col, aoi_height_col]
    optional_cols = [aoi_token_col, aoi_srcML_tag_col]
    for c in optional_cols:
        if c in aoi_df.columns:
            aoi_cols.append(c)
            
    _aoi_df = aoi_df.copy()[aoi_cols]

    if is_line_level:
      _fixations['_name'] = \
        _fixations.apply(
          lambda row: _hit_test_nearest_line(
          fixation_row=row,
          aoi_df=_aoi_df,
          fixation_x_col=fixation_x0_col,
          fixation_y_col=fixation_y0_col,
          aoi_x_col=aoi_x_col,
          aoi_y_col=aoi_y_col,
          aoi_width_col=aoi_width_col,
          aoi_height_col=aoi_height_col,
          aoi_name_col=aoi_name_col,
        ),
      axis=1)
    else:
      _fixations['_name'] = \
        _fixations.apply(lambda _fixation_row: _hit_test(_fixation_row,
                                                         _aoi_df,
                                                         radius,
                                                         fixation_x0_col,
                                                         fixation_y0_col,
                                                         aoi_x_col,
                                                         aoi_y_col,
                                                         aoi_width_col,
                                                         aoi_height_col,
                                                         aoi_name_col),
                         axis=1)

    return _fixations.merge(_aoi_df.add_prefix("aoi_"), left_on="_name",
                            right_on="aoi_name", how="inner").drop("_name", axis=1)


def _hit_test_nearest_line(
    fixation_row: pd.Series,
    aoi_df: pd.DataFrame,
    fixation_x_col: str = "x0",
    fixation_y_col: str = "y0",
    aoi_x_col: str = "x",
    aoi_y_col: str = "y",
    aoi_width_col: str = "width",
    aoi_height_col: str = "height",
    aoi_name_col: str = "name",
    x_margin_px: float = 20,
    max_distance_px: float | None = None,
    max_distance_multiplier: float = 1.5,
):
    fx = fixation_row[fixation_x_col]
    fy = fixation_row[fixation_y_col]

    # 1) Horizontal gate: must be within the code block (plus margin)
    x_left = float(aoi_df[aoi_x_col].min()) - x_margin_px
    x_right = float((aoi_df[aoi_x_col] + aoi_df[aoi_width_col]).max()) + x_margin_px
    if not (x_left <= fx <= x_right):
        return None

    # 2) Nearest line by vertical center
    centers = aoi_df[aoi_y_col] + (aoi_df[aoi_height_col] / 2)
    distances = (centers - fy).abs()
    min_dist = float(distances.min())

    # 3) Vertical sanity threshold
    if max_distance_px is None:
        line_h = float(aoi_df[aoi_height_col].median())
        max_distance_px = max_distance_multiplier * line_h
    if min_dist > max_distance_px:
        return None

    closest_idx = distances.idxmin()
    return aoi_df.loc[closest_idx, aoi_name_col]



def _hit_test(_fixation_row: pd.DataFrame, aoi_df: pd.DataFrame, radius: int = 25,
              fixation_x0_col: str = "x0", fixation_y0_col: str = "y0",
              aoi_x_col: str = "x", aoi_y_col: str = "y",
              aoi_width_col: str = "width", aoi_height_col: str = "height",
              aoi_name_col: str = "name") -> pd.DataFrame:
    '''Matches a fixation with its respective AOI.

    Parameters
    ----------
    _fixation_row : pandas.DataFrame
        One-row pandas dataframe corresponding to one fixation.

    aoi_df : pandas.DataFrame
        A pandas dataframe of AOIs.

    radius : int, optional (default 25)
        Farthest distance from an AOI that a fixation belongs to it can be.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe that matches fixation with their respective AOI.
    '''

    for _, aoi_row in aoi_df.iterrows():
        box_x = aoi_row[aoi_x_col] - (radius / 2)
        box_y = aoi_row[aoi_y_col] - (radius / 2)
        box_w = aoi_row[aoi_width_col] + radius
        box_h = aoi_row[aoi_height_col] + radius

        if box_x <= _fixation_row[fixation_x0_col] <= box_x + box_w and \
                box_y <= _fixation_row[fixation_y0_col] <= box_y + box_h:
            return aoi_row[aoi_name_col]
