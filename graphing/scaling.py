import numpy as np


def autoscale_limits(x_vals, y_vals, pad: float = 0.08):
    """
    Smart axis limiter that keeps the interesting part of the curve in view.

    Strategy:
      1. Filter NaN / Inf values.
      2. Compute Q1, Q3, IQR of y — this is robust to extreme tails.
      3. Clip display window to [Q1 - 1.5*IQR, Q3 + 1.5*IQR] (Tukey fences).
      4. Additionally cap the y-window to ±2× the x-span so steep curves
         (cubics, exponentials) don't squish the plot into a thin vertical line.
      5. If IQR is zero (constant function), fall back to full range ±1 unit.
    """
    valid_mask = np.isfinite(y_vals)
    if not np.any(valid_mask):
        return (-10.0, 10.0), (-10.0, 10.0)

    valid_y = y_vals[valid_mask]
    xmin, xmax = float(np.min(x_vals)), float(np.max(x_vals))
    x_span = xmax - xmin if xmax != xmin else 1.0

    # --- IQR-based y window ---
    q1, q3 = float(np.percentile(valid_y, 25)), float(np.percentile(valid_y, 75))
    iqr = q3 - q1

    if iqr > 1e-10:
        # Tukey fences – shows outliers but clips extreme tails
        fence_lo = q1 - 1.5 * iqr
        fence_hi = q3 + 1.5 * iqr
    else:
        # Constant-ish function: use simple percentile range + 1 unit headroom
        fence_lo = float(np.percentile(valid_y, 2)) - 1.0
        fence_hi = float(np.percentile(valid_y, 98)) + 1.0

    # --- Cap y-window to ±2× x-span so steep curves stay visible ---
    max_half_y = 2.0 * x_span
    y_mid = (fence_lo + fence_hi) / 2.0
    half_range = min((fence_hi - fence_lo) / 2.0, max_half_y)
    ymin = y_mid - half_range
    ymax = y_mid + half_range

    # Normalise x limits
    xpad = x_span * pad
    ypad = (ymax - ymin) * pad

    xlim = (xmin - xpad, xmax + xpad)
    ylim = (ymin - ypad, ymax + ypad)

    if not np.all(np.isfinite(xlim + ylim)):
        return (-10.0, 10.0), (-10.0, 10.0)

    return xlim, ylim



def enforce_equal_aspect(ax, xlim, ylim):
    """Adjust axis limits to maintain 1:1 aspect ratio without squishing the canvas box."""
    ax.set_aspect('auto')
    x_len = abs(xlim[1] - xlim[0])
    y_len = abs(ylim[1] - ylim[0])
    max_len = max(x_len, y_len) / 2.0
    x_mid = (xlim[0] + xlim[1]) / 2.0
    y_mid = (ylim[0] + ylim[1]) / 2.0
    ax.set_xlim(x_mid - max_len, x_mid + max_len)
    ax.set_ylim(y_mid - max_len, y_mid + max_len)
    ax.set_aspect('equal', adjustable='datalim')

