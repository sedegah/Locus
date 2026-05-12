import numpy as np

def autoscale_limits(x_vals, y_vals, pad=0.05):
    # Filter out NaN and infinite values
    valid_mask = np.isfinite(y_vals)
    if not np.any(valid_mask):
        # If no valid values, return default limits
        return (-10, 10), (-10, 10)
    
    valid_y_vals = y_vals[valid_mask]
    
    xmin, xmax = min(x_vals), max(x_vals)
    ymin, ymax = min(valid_y_vals), max(valid_y_vals)
    
    # Handle edge cases
    xpad = (xmax - xmin) * pad if xmax != xmin else 1
    ypad = (ymax - ymin) * pad if ymax != ymin else 1
    
    # Ensure finite limits
    xlim = (xmin - xpad, xmax + xpad)
    ylim = (ymin - ypad, ymax + ypad)
    
    # Final check for any remaining NaN or Inf
    if not np.all(np.isfinite(xlim + ylim)):
        return (-10, 10), (-10, 10)
    
    return xlim, ylim
