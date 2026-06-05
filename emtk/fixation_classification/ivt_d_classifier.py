import math
import statistics


def ivt_d_classifier(raw_fixations, minimum_duration=50, sample_duration=4, velocity_threshold=1.5):
    """
    I-VT (Velocity Threshold Identification) fixation classifier.

    Parameters
    ----------
    raw_fixations : list
        List of tuples (timestamp, x_cord, y_cord).

    minimum_duration : int, optional
        Minimum fixation duration (ms). Default is 50 ms.

    sample_duration : int, optional
        Time between samples in milliseconds (default 4 ms).

    velocity_threshold : float, optional
        Maximum allowed point-to-point velocity (pixels/ms)
        to be considered part of a fixation. Default 100 px/sample-ms.

    Returns
    -------
    list
        Each fixation: [timestamp, duration, x_cord, y_cord]
    """

    if not raw_fixations or len(raw_fixations) < 2:
        return []

    velocities = []
    # Compute velocities between consecutive points
    for i in range(1, len(raw_fixations)):
        t1, x1, y1 = raw_fixations[i - 1]
        t2, x2, y2 = raw_fixations[i]
        dt = (t2 - t1)/1000 if (t2 - t1) > 0 else sample_duration
        dx = x2 - x1
        dy = y2 - y1
        #Euclidiean velocity = Distance/Time
        #Distance between two points calculated by
        #Pythgoras theorem - hypotenuse of y2,y1  and x2,x1
        velocity = math.sqrt(dx**2 + dy**2) / dt
        velocities.append(velocity)

    print("Sample velocities:", velocities[:25])

    fixations = []
    current_fix = []
    fixation_start_time = None

    # Label fixation vs saccade based on velocity threshold
    for i, (timestamp, x, y) in enumerate(raw_fixations[:-1]):
        v = velocities[i]
        if v < velocity_threshold:
            # fixation point
            if not current_fix:
                fixation_start_time = timestamp
            current_fix.append((timestamp, x, y))
        else:
            # saccade point; finalize current fixation
            if current_fix:
                duration = (len(current_fix) + 1) * sample_duration
                if duration >= minimum_duration:
                    mean_x = statistics.mean([p[1] for p in current_fix])
                    mean_y = statistics.mean([p[2] for p in current_fix])
                    fixations.append([fixation_start_time, duration, mean_x, mean_y])
                current_fix = []

    # Handle final fixation if one was open at end
    if current_fix:
        duration = len(current_fix) * sample_duration
        if duration >= minimum_duration:
            mean_x = statistics.mean([p[1] for p in current_fix])
            mean_y = statistics.mean([p[2] for p in current_fix])
            fixations.append([fixation_start_time, duration, mean_x, mean_y])

    return fixations
