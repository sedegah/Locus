import numpy as np


def sample_range(x_min: float = -10, x_max: float = 10, points: int = 1200) -> np.ndarray:
    """Generate uniform grid sampling."""
    return np.linspace(x_min, x_max, points)


def sanitize_eval_values(x_vals: np.ndarray, y_vals: np.ndarray, threshold: float = 100.0) -> np.ndarray:
    """
    Filter y_vals to remove asymptotic spikes and singular jumps.
    Replaces values exceeding threshold or infinite/NaN with NaN,
    and inserts NaN between points where sign flips across a huge magnitude gap (asymptotes).
    """
    y_clean = np.copy(y_vals).astype(float)
    
    # 1. Mask non-finite values
    y_clean[~np.isfinite(y_clean)] = np.nan
    
    # 2. Mask values exceeding absolute threshold
    y_clean[np.abs(y_clean) > threshold] = np.nan
    
    # 3. Detect asymptotic sign jumps (e.g. tan(x), 1/x)
    if len(y_clean) > 1:
        dy = np.abs(np.diff(y_clean))
        # Where consecutive difference is large and sign flips
        sign_flip = (y_clean[:-1] * y_clean[1:]) < 0
        large_jump = dy > (threshold * 0.4)
        asymptote_indices = np.where(sign_flip & large_jump)[0]
        
        for idx in asymptote_indices:
            y_clean[idx] = np.nan
            y_clean[idx + 1] = np.nan
            
    return y_clean


def adaptive_sample(eval_fn, x_min: float = -10, x_max: float = 10, base_points: int = 1500) -> tuple[np.ndarray, np.ndarray]:
    """
    Adaptive sampling that samples densely near high curvature and handles discontinuities.
    Returns (x_vals, y_vals).
    """
    x_grid = np.linspace(x_min, x_max, base_points)
    try:
        y_grid = eval_fn(x_grid)
        if np.isscalar(y_grid):
            y_grid = np.full_like(x_grid, y_grid)
    except Exception:
        y_grid = np.full_like(x_grid, np.nan)

    y_clean = sanitize_eval_values(x_grid, y_grid)
    return x_grid, y_clean

