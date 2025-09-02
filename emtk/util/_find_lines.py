import pandas as pd
import re


def _find_lines(aois: pd.DataFrame) -> pd.DataFrame:
    '''Return a dataframe of lines from a dataframe of AOIs.

    Parameters
    ----------
    aois : pandas.DataFrame
        Pandas dataframe of AOIs.

    Returns
    -------
    pandas.DataFrame
        Color of the background of the image. "Black" or "white".
    '''
    temp_rows = []
    for _, row in aois.iterrows():
        name, y, height = row["name"], row["y"], row["height"]
        line_num = re.search(r'\d+', name).group(0)
        
        temp_rows.append({
        "line_num": int(line_num),
        "line_y": y + height / 2,
        "line_height": height,
        })
    
    results = pd.DataFrame(temp_rows)
    results = results.drop_duplicates(subset="line_num")
    return results
