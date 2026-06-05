import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageDraw

from emtk.util import _find_background_color, _get_meta_data, _get_stimuli
from emtk.aoi import find_aoi

# ----------------------------
# VISUAL CONFIGURATION
# ----------------------------

#RAW_COLOR = (30, 30, 30, 120)
#FIXATION_FILL = (0, 114, 178, 170)      # strong blue
#FIXATION_OUTLINE = (0, 0, 0, 220)
SACCADE_COLOR = (230, 159, 0, 255)      # orange

#RAW_COLOR = (0, 160, 160, 90)        # translucent teal

#FIXATION_FILL = (0, 90, 200, 200)    # strong blue
FIXATION_OUTLINE = (0, 0, 0, 220)
SCANPATH_COLOR = (0, 0, 0, 120)

RAW_COLOR = (255, 80, 80, 120) 
FIXATION_FILL = (0, 90, 200, 150) 

FIXATION_SCALE = 0.5 #0.8
RAW_DATA_SIZE = 2
MIN_FIX_RADIUS = 6



def __draw_aoi_new(draw: ImageDraw.Draw, aoi: pd.DataFrame, bg_color: str) -> None:
    """Draw areas of interest on stimuli image.

    Parameters
    ----------
    draw : PIL.ImageDraw.Draw
        Pillow Draw object imposed on stimuli image.

    aoi : pandas.DataFrame
        Pandas DataFrame of areas of interest.

    bg_color : str
        Background color of stimuli image.
    """

    outline = {'white': '#000000', 'black': '#ffffff'}

    for row in aoi[['x', 'y', 'width', 'height']].iterrows():
        y_coordinate = row[1]['y']
        x_coordinate = row[1]['x']
        height = row[1]['height']
        width = row[1]['width']
        draw.rectangle([(x_coordinate, y_coordinate),
                        (x_coordinate + width - 1, y_coordinate + height - 1)],
                       outline=outline[bg_color])

    return None


def __draw_fixation_new(draw: ImageDraw.Draw, fixations: pd.DataFrame, draw_number: bool = False,
                    x0_col: str = "x0", y0_col: str = "y0", duration_col: str = "duration", draw_scanpath=False) -> None:

    prev_x, prev_y = None, None

    for i, (_, fixation) in enumerate(fixations.iterrows()):

        duration = fixation[duration_col]
        r = max(MIN_FIX_RADIUS, np.sqrt(duration) * FIXATION_SCALE)

        x = fixation[x0_col]
        y = fixation[y0_col]

        bound = (x - r, y - r, x + r, y + r)

        # Draw fixation
        draw.ellipse(bound,
                     fill=FIXATION_FILL,
                     outline=FIXATION_OUTLINE,
                     width=2)

        # Draw scanpath line
        if draw_scanpath and prev_x is not None:
            draw.line((prev_x, prev_y, x, y),
                      fill=SCANPATH_COLOR,
                      width=2)

        # Optional numbering
        if draw_number:
            draw.text((x + r, y - r),
                      str(i + 1),
                      fill=(0, 0, 0, 255))

        prev_x, prev_y = x, y


def __draw_saccade_new(draw: ImageDraw.Draw, saccades: pd.DataFrame, draw_number: bool = False,
                   x0_col: str = "x0", y0_col: str = "y0",
                   x1_col: str = "x1", y1_col: str = "y1") -> None:
    """Draw saccades with their respective orders of appearance.

    Parameters
    ----------
    draw : PIL.ImageDraw.Draw
        Draw object imposed on stimuli image.

    saccades: pandas.DataFrame
        Pandas dataframe of saccades.

    draw_number : bool
        Indicate whether user wants to draw the orders of appearance of saccades.

    x0_col : str, optional (default to "x0")
        Name of the column in the saccades dataframe that contains the starting x-coordinates of saccades.

    y0_col : str, optional (default to "y0")
        Name of the column in the saccades dataframe that contains the starting y-coordinates of saccades.

    x1_col : str, optional (default to "x1")
        Name of the column in the saccades dataframe that contains the ending x-coordinates of saccades.

    y1_col : str, optional (default to "y1")
        Name of the column in the saccades dataframe that contains the ending y-coordinates of saccades.
    """
    for _, saccade in saccades.iterrows():
        draw.line((saccade[x0_col], saccade[y0_col],
                   saccade[x1_col], saccade[y1_col]),
                  fill=SACCADE_COLOR,
                  width=3)


def __draw_raw_data_new(draw: ImageDraw.Draw, samples: pd.DataFrame, sample_x_col, sample_y_col, step:int = 1) -> None:
    for _, sample in samples.iloc[::step].iterrows():
        x = float(sample[sample_x_col])
        y = float(sample[sample_y_col])
        r = RAW_DATA_SIZE
        draw.ellipse((x-(r/2), y-(r/2), x+r, y+r), fill=RAW_COLOR)



def draw_trial_new(eye_events: pd.DataFrame = pd.DataFrame(), samples: pd.DataFrame = pd.DataFrame(),
               draw_raw_data: bool = False, draw_fixation: bool = True, draw_saccade: bool = False,
               draw_number: bool = False, draw_aoi: bool = False, save_image: str = None,
               eye_tracker_col: str = "eye_tracker",
               stimuli_module_col: str = "stimuli_module",
               stimuli_name_col: str = "stimuli_name",
               x0_col: str = "x0", y0_col: str = "y0",
               x1_col: str = "x1", y1_col: str = "y1", duration_col: str = "duration",
               eye_event_type_col: str = "eye_event_type",
               sample_x_col: int = "x", sample_y_col: str = "y") -> None:
    """Draw raw data samples, fixations, and saccades over simuli images image
    Circle size indicates fixation duration.

    Parameters
    ----------   
    eye_events : pd.DataFrame
        Pandas dataframe for eye events.

    samples : pd.DataFrame
        Pandas dataframe for samples.

    draw_raw_data : bool, optional (default False)
        whether user wants raw data drawn.

    draw_fixation : bool, optional (default True)
        whether user wants fixations drawn

    draw_saccade : bool, optional (default False)
        whether user wants saccades drawn

    draw_number : bool, optional (default False)
        whether user wants to draw eye movement number

    draw_aoi : bool, optional (default False)
        whether user wants to draw eye movement number

    save_image : str, optional (default None)
        path to save the image, image is saved to this path if it parameter exists
    """

    if eye_events.empty and samples.empty:
        raise Exception('Both eye_events and samples dataframes are empty')

    metadata_df = samples if eye_events.empty else eye_events
    eye_tracker, stimuli_module, \
        stimuli_name = _get_meta_data(metadata_df, eye_tracker_col,
                                      stimuli_module_col, stimuli_name_col)

    stimuli = _get_stimuli(stimuli_module, stimuli_name, eye_tracker)

    bg_color = _find_background_color(image=stimuli)
    draw = ImageDraw.Draw(stimuli, 'RGBA')

    # ----------------------------
    # DRAW ORDER (Hierarchy)
    # ----------------------------

    if draw_aoi:
        aoi = find_aoi(image=stimuli)
        __draw_aoi_new(draw, aoi, bg_color)

    if draw_raw_data and not samples.empty:
        __draw_raw_data_new(draw, samples, sample_x_col, sample_y_col)

    if draw_fixation and not eye_events.empty:
        fixations = eye_events.loc[
            eye_events[eye_event_type_col] == "fixation"
        ].sort_index()

        __draw_fixation_new(draw, fixations, draw_number,
                         x0_col, y0_col,
                         duration_col,
                         draw_scanpath=False)


    if draw_saccade and not eye_events.empty:
        saccades = eye_events.loc[
            eye_events[eye_event_type_col] == "saccade"
        ]
        __draw_saccade_new(draw, saccades,
                        x0_col, y0_col,
                        x1_col, y1_col)

    plt.figure(figsize=(25,20), dpi = 300)
    plt.imshow(np.asarray(stimuli), interpolation='nearest')
    plt.axis("off")

    # Legend
    #from matplotlib.patches import Patch
    #legend_elements = [
     #   Patch(facecolor=(0/255,160/255,90/255,0.6),
      #        edgecolor='black',
       #       label='Fixation (size ∝ duration)'),
        #Patch(facecolor=(120/255,120/255,120/255,0.3),
         #     label='Raw gaze samples'),
        
        #Patch(facecolor=(230/255,159/255,0/255,1),
        #      label='Saccade')
    #]

    #plt.legend(handles=legend_elements,
      #         loc="upper right",
       #        frameon=True)

    #plt.figure(figsize=(17, 15))

    if save_image is not None:
        plt.savefig(save_image, dpi=300, bbox_inches="tight")
        print(save_image, "saved!")
