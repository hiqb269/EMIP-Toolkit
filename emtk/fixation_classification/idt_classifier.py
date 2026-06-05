import math
import statistics


def idt_classifier(raw_fixations, minimum_duration=50, sample_duration=4, maximum_dispersion=25):
    """I-DT classifier based on page 296 of eye tracker manual:
        https://psychologie.unibas.ch/fileadmin/user_upload/psychologie/Forschung/N-Lab/SMI_iView_X_Manual.pdf

    Parameters
    ----------
    raw_fixations : list
        a list of fixations information containing timestamp, x_cord, and y_cord

    minimum_duration : int, optional
        minimum duration for a fixation in milliseconds, less than minimum is considered noise.
        set to 50 milliseconds by default

    sample_duration : int, optional
        Sample duration in milliseconds, this is 4 milliseconds based on this eye tracker

    maximum_dispersion : int, optional
        maximum distance from a group of samples to be considered a single fixation.
        Set to 25 pixels by default

    Returns
    -------
    list
        a list where each element is a list of timestamp, duration, x_cord, and y_cord
    """

    # Create moving window based on minimum_duration
    window_size = int(math.ceil(minimum_duration / sample_duration))

    window_x = []
    window_y = []

    filter_fixation = []
    #Test code
    #print(f"Length of raw fixations: {len(raw_fixations)}")
    
    #maximum_dispersion = 25
    #minimum_duration = 50
    #print(f"Using max dispersion: {maximum_dispersion} and minimum duration: {minimum_duration}")


    # Filter valid points first
    valid_points = []
    for timestamp, x_cord, y_cord in raw_fixations:
        # Filter (skip) coordinates outside of the screen 1920×1080 px
        if x_cord >= 0 and y_cord >= 0 and x_cord <= 1920 and y_cord <= 1080:
            valid_points.append([timestamp, x_cord, y_cord])

    #Test code
    #print(f"Length of valid points: {len(valid_points)}")

    #While there are still points in the valid points
    index = 0
    while index < len(valid_points):
      window_end = min(index + window_size, len(valid_points))
      window_x = [valid_points[j][1] for j in range(index, window_end)]
      window_y = [valid_points[j][2] for j in range(index, window_end)]

      # Need at least window_size points to form a valid fixation candidate
      if len(window_x) < window_size:
            break
        
      # Calculate dispersion = [max(x) - min(x)] + [max(y) - min(y)]
      dispersion = (max(window_x) - min(window_x)) + (max(window_y) - min(window_y))
      # If dispersion of window points <= threshold
      if dispersion <= maximum_dispersion:
          
          # Add additional points to the window until dispersion > threshold
          while window_end < len(valid_points):
            # Try adding next point
            next_x = valid_points[window_end][1]
            next_y = valid_points[window_end][2]
                
            # Calculate new dispersion with this point included
            test_dispersion = (max(window_x + [next_x]) - min(window_x + [next_x])) + \
                                 (max(window_y + [next_y]) - min(window_y + [next_y]))
                
            # If dispersion still acceptable, include the point
            if test_dispersion <= maximum_dispersion:
              window_x.append(next_x)
              window_y.append(next_y)
              window_end += 1
            else:
                    # Dispersion exceeded, stop expanding
              break
          
          xcord = statistics.mean(window_x)
          ycord = statistics.mean(window_y)
          duration = (valid_points[window_end-1][0] - valid_points[index][0])/1000
          timestamp = valid_points[index][0]
          filter_fixation.append(
                    [timestamp, duration, xcord , ycord])
          index= window_end # to hop after next_x and next_y
      else:
          index = index + 1

    return filter_fixation
