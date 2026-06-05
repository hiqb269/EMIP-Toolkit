import math
import statistics
import numpy as np


def ivt_classifier(
    raw_fixations,
    minimum_duration=50,
    velocity_threshold=40,

):
    """
    I-VT (Velocity Threshold Identification) fixation classifier.

    Parameters
    ----------
    raw_fixations : list
        List of tuples (timestamp, x_cord, y_cord).

    minimum_duration : int, optional
        Minimum fixation duration (ms). Default is 50 ms.

    velocity_threshold : float, optional
        Maximum allowed point-to-point velocity (degrees/s)
        to be considered part of a fixation. Default 40 deg/s.


    Returns
    -------
    list
        Each fixation: [timestamp, duration, x_cord, y_cord]
    """

    if not raw_fixations or len(raw_fixations) < 2:
        return []
    
    #CONFIGURATION PARAMETERS
    screen_width_mm=344
    screen_res_x=1920
    distance_to_screen_mm=600

    px_size_mm = screen_width_mm / screen_res_x  # mm per pixel
    raw_fixations = np.array(raw_fixations)
    timestamps = raw_fixations[:, 0]    
    x_cords = raw_fixations[:, 1]
    y_cords = raw_fixations[:, 2]

    t_s = (timestamps - timestamps[0]) / 1_000_000 #time in seconds
    # -----------------------------
    # Compute absolute differences
    # -----------------------------
    dx_px = np.abs(np.diff(x_cords))
    dy_px = np.abs(np.diff(y_cords))
    dt_s = np.diff(t_s)

    # 2D displacement in mm
    dist_mm = np.sqrt(dx_px**2 + dy_px**2) * px_size_mm

    # Convert displacement to degrees of visual angle
    dtheta_deg = 2 * np.arctan2(dist_mm, 2 * distance_to_screen_mm) * (180 / math.pi)

    # Velocity in deg/s
    velocity_deg_s = np.abs(dtheta_deg / dt_s)
    

    fixations = []
    current_fix = []
    fixation_start_t = None

    # Iterate over all samples except last (vel array is len-1)
    for i in range(len(velocity_deg_s)):
        t = timestamps[i]
        x = x_cords[i]
        y = y_cords[i]
        v = velocity_deg_s[i]
        if v < velocity_threshold:
            # inside fixation
            if not current_fix:
                fixation_start_t = t
            current_fix.append((t, x, y))

        else:
            # saccade begins → close fixation if long enough
            if current_fix:
                duration_ms = (current_fix[-1][0] - fixation_start_t) / 1000.0
                if duration_ms >= minimum_duration:
                    mean_x = statistics.mean(p[1] for p in current_fix)
                    mean_y = statistics.mean(p[2] for p in current_fix)
                    fixations.append([fixation_start_t, duration_ms, mean_x, mean_y])
                current_fix = []

    # Handle fixation at end of trial
    if current_fix:
        duration_ms = (current_fix[-1][0] - fixation_start_t) / 1000.0
        if duration_ms >= minimum_duration:
            mean_x = statistics.mean(p[1] for p in current_fix)
            mean_y = statistics.mean(p[2] for p in current_fix)
            fixations.append([fixation_start_t, duration_ms, mean_x, mean_y])

    return fixations