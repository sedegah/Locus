def autoscale_limits(x_vals, y_vals, pad=0.05):
    xmin, xmax = min(x_vals), max(x_vals)
    ymin, ymax = min(y_vals), max(y_vals)
    xpad = (xmax - xmin) * pad if xmax != xmin else 1
    ypad = (ymax - ymin) * pad if ymax != ymin else 1
    return (xmin - xpad, xmax + xpad), (ymin - ypad, ymax + ypad)
