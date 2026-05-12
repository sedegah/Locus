import numpy as np
from sympy import lambdify, latex

from graphing.scaling import autoscale_limits
from math_engine.parser import parse_user_equation
from symbolic.derivatives import derivative


def _eval_expr(expr, x_vals):
    fn = lambdify("x", expr, "numpy")
    return fn(x_vals)


def sample_and_plot(ax, equation: str, x_min: float = -10, x_max: float = 10, points: int = 1200) -> None:
    ax.clear()
    ax.grid(True, alpha=0.3)

    try:
        # First check if this is a circle equation before any parsing
        equation_lower = equation.lower()
        is_circle = _is_circle_equation(equation_lower)
        
        print(f"DEBUG: equation={equation}, is_circle={is_circle}")
        
        if is_circle:
            print("DEBUG: Plotting circle...")
            _plot_circle(ax, equation)  # Use original equation string
            ax.legend(loc="upper left")
            ax.set_title(f"${equation}$")
            return
        
        # If not a circle, proceed with normal function parsing
        try:
            expr = parse_user_equation(equation)
        except Exception as e:
            print(f"DEBUG: Parse error: {e}")
            ax.text(0.5, 0.5, f"Parse error:\n{e}", ha="center", va="center", transform=ax.transAxes)
            return
        
        # Check function type and domain
        expr_str = str(expr).lower()
        is_trig = any(func in expr_str for func in ['sin', 'cos', 'tan', 'csc', 'sec', 'cot'])
        has_sqrt = 'sqrt' in expr_str
        
        # First, evaluate the function on a standard range to check quadrants
        test_x_vals = np.linspace(-10, 10, 1000)
        test_y_vals = _eval_expr(expr, test_x_vals)
        test_y_vals = np.where(np.isfinite(test_y_vals), test_y_vals, np.nan)
        
        # Check which quadrants the function exists in
        quadrants_with_function = set()
        for i, (x, y) in enumerate(zip(test_x_vals, test_y_vals)):
            if np.isfinite(y):
                if x >= 0 and y >= 0:
                    quadrants_with_function.add("I")
                elif x < 0 and y >= 0:
                    quadrants_with_function.add("II")
                elif x < 0 and y < 0:
                    quadrants_with_function.add("III")
                elif x >= 0 and y < 0:
                    quadrants_with_function.add("IV")
        
        # Show all quadrants if function exists in multiple quadrants
        show_all_quadrants = len(quadrants_with_function) > 1 or is_trig or has_sqrt
        
        if show_all_quadrants:
            if is_trig:
                # For trig functions, show multiple periods
                x_min, x_max = -4 * np.pi, 4 * np.pi
            else:
                # For other functions, show standard range
                x_min, x_max = -10, 10
            
            points = 2400  # More points for smooth curves
            ax.axhline(y=0, color='k', linewidth=0.5)  # x-axis
            ax.axvline(x=0, color='k', linewidth=0.5)  # y-axis
            
            # Add important markers for trig functions
            if is_trig:
                for multiple in range(-4, 5):
                    # Mark π multiples
                    x_val = multiple * np.pi
                    if abs(multiple) == 1:
                        label = 'π' if multiple == 1 else '-π'
                    else:
                        label = f'{multiple}π' if multiple != 0 else '0'
                    ax.axvline(x=x_val, color='gray', linewidth=0.3, alpha=0.5)
                    if multiple % 2 == 0:  # Only label even multiples to avoid clutter
                        ax.text(x_val, 10, label, 
                               ha='center', va='top', fontsize=8)
        
        x_vals = np.linspace(x_min, x_max, points)
        y_vals = _eval_expr(expr, x_vals)
        
        # Handle undefined values and discontinuities
        if is_trig and any(func in expr_str for func in ['tan', 'cot', 'sec', 'csc']):
            # Find and handle vertical asymptotes
            y_vals = np.where(np.abs(y_vals) > 100, np.nan, y_vals)
        else:
            # Handle functions with restricted domains (like sqrt, log, etc.)
            y_vals = np.where(np.isfinite(y_vals), y_vals, np.nan)
        
        ax.plot(x_vals, y_vals, linewidth=2, label="f(x)")
        
        if show_all_quadrants:
            if is_trig:
                # Set appropriate y-limits for trig functions
                ax.set_ylim(-3, 3)
            else:
                # For other multi-quadrant functions, set reasonable y-limits
                valid_y_vals = y_vals[np.isfinite(y_vals)]
                if len(valid_y_vals) > 0:
                    y_min, y_max = min(valid_y_vals), max(valid_y_vals)
                    y_range = y_max - y_min
                    ax.set_ylim(y_min - y_range * 0.2, y_max + y_range * 0.2)
                else:
                    ax.set_ylim(-10, 10)
            ax.set_xlim(x_min, x_max)
            
            # Add quadrant labels
            ax.text(0.02, 0.98, f"Quadrants: {', '.join(sorted(quadrants_with_function))}", 
                   transform=ax.transAxes, fontsize=10, 
                   verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.7))
        else:
            # Single quadrant functions - use autoscale
            xlim, ylim = autoscale_limits(x_vals, y_vals)
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
            
            # Add quadrant labels for single quadrant functions
            x_min_plot, x_max_plot = xlim
            y_min_plot, y_max_plot = ylim
            
            # Determine which quadrants are visible
            quadrants_visible = []
            if x_min_plot < 0 and x_max_plot > 0 and y_min_plot < 0 and y_max_plot > 0:
                quadrants_visible.extend(["I", "II", "III", "IV"])
            elif x_min_plot >= 0 and y_min_plot >= 0:
                quadrants_visible.append("I")
            elif x_min_plot < 0 and y_min_plot >= 0:
                quadrants_visible.append("II")
            elif x_min_plot < 0 and y_max_plot <= 0:
                quadrants_visible.append("III")
            elif x_min_plot >= 0 and y_max_plot <= 0:
                quadrants_visible.append("IV")
            elif x_min_plot < 0 and x_max_plot > 0 and y_min_plot >= 0:
                quadrants_visible.extend(["I", "II"])
            elif x_min_plot < 0 and x_max_plot > 0 and y_max_plot <= 0:
                quadrants_visible.extend(["III", "IV"])
            elif x_min_plot >= 0 and y_min_plot < 0 and y_max_plot > 0:
                quadrants_visible.extend(["I", "IV"])
            elif x_min_plot < 0 and y_min_plot < 0 and y_max_plot > 0:
                quadrants_visible.extend(["II", "III"])
            
            # Add quadrant labels
            if quadrants_visible:
                ax.text(0.02, 0.98, f"Quadrants: {', '.join(quadrants_visible)}", 
                       transform=ax.transAxes, fontsize=10, 
                       verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.7))
            
        ax.legend(loc="upper left")
        ax.set_title(f"$y = {latex(expr)}$")
        
    except Exception as exc:  # noqa: BLE001
        ax.text(0.5, 0.5, f"Plot error:\n{exc}", ha="center", va="center", transform=ax.transAxes)


def plot_derivative(ax, equation: str) -> None:
    expr = parse_user_equation(equation)
    sample_and_plot(ax, equation)
    
    # Check if this is a trigonometric function
    expr_str = str(expr).lower()
    is_trig = any(func in expr_str for func in ['sin', 'cos', 'tan', 'csc', 'sec', 'cot'])
    
    if is_trig:
        x_vals = np.linspace(-4 * np.pi, 4 * np.pi, 2400)
    else:
        x_vals = np.linspace(-10, 10, 1200)
    
    dydx = _eval_expr(derivative(expr), x_vals)
    
    # Handle discontinuities for derivatives of trig functions
    if is_trig and any(func in expr_str for func in ['tan', 'cot', 'sec', 'csc']):
        dydx = np.where(np.abs(dydx) > 100, np.nan, dydx)
    
    ax.plot(x_vals, dydx, linewidth=1.8, linestyle="--", label="f'(x)")
    ax.legend(loc="upper left")


def plot_integral_area(ax, equation: str, a: float = -2, b: float = 2) -> None:
    expr = parse_user_equation(equation)
    
    # Check if this is a trigonometric function and adjust default range
    expr_str = str(expr).lower()
    is_trig = any(func in expr_str for func in ['sin', 'cos', 'tan', 'csc', 'sec', 'cot'])
    
    if is_trig and a == -2 and b == 2:  # Only change defaults
        a, b = -np.pi, np.pi  # Show one period for trig functions
    
    sample_and_plot(ax, equation)


def _is_circle_equation(expr_str: str) -> bool:
    """Check if equation represents a circle"""
    # Look for patterns like (x-h)^2 + (y-k)^2 = r^2
    # Check if it contains both x^2 and y^2 terms
    has_x2 = 'x**2' in expr_str or 'x^2' in expr_str
    has_y2 = 'y**2' in expr_str or 'y^2' in expr_str
    
    return has_x2 and has_y2


def _plot_circle(ax, expr_str: str) -> None:
    """Plot a circle from its equation using general circle formula"""
    try:
        # Parse circle equation to extract center and radius
        # General circle formula: (x-h)² + (y-k)² = r²
        
        # Default values
        h, k, r = 0, 0, 1
        
        # Clean up the equation string
        eq = expr_str.replace(' ', '').replace('^', '**')
        
        # Extract parameters using regex
        import re
        
        # Look for (x-h)**2 or (x+h)**2 pattern
        x_match = re.search(r'\(x([+-]\d+(?:\.\d+)?)\)\*\*2', eq)
        if x_match:
            h = -float(x_match.group(1))
        
        # Look for (y-k)**2 or (y+k)**2 pattern  
        y_match = re.search(r'\(y([+-]\d+(?:\.\d+)?)\)\*\*2', eq)
        if y_match:
            k = -float(y_match.group(1))
        
        # Look for radius (right side of equation)
        radius_match = re.search(r'=\s*(\d+(?:\.\d+)?)', eq)
        if radius_match:
            r_squared = float(radius_match.group(1))
            r = np.sqrt(r_squared)
        elif '=' in eq:
            # If there's an equals sign, try to parse the right side
            right_side = eq.split('=')[-1].strip()
            try:
                r_squared = float(right_side)
                r = np.sqrt(r_squared)
            except:
                pass
        
        # Generate circle points using parametric equations
        # x = h + r*cos(θ), y = k + r*sin(θ)
        theta = np.linspace(0, 2*np.pi, 1000)
        x_circle = h + r * np.cos(theta)
        y_circle = k + r * np.sin(theta)
        
        # Plot the circle
        ax.plot(x_circle, y_circle, linewidth=2, label="Circle", color='blue')
        
        # Set equal aspect ratio and appropriate limits
        ax.set_aspect('equal', adjustable='box')
        margin = r + 1
        ax.set_xlim(h - margin, h + margin)
        ax.set_ylim(k - margin, k + margin)
        
        # Add center point
        ax.plot(h, k, 'ro', markersize=6, label=f"Center ({h}, {k})")
        
        # Add axes
        ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5, alpha=0.5)
        
        # Add quadrant labels
        ax.text(0.02, 0.98, "Quadrants: I, II, III, IV", 
               transform=ax.transAxes, fontsize=10, 
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.7))
        
        # Add equation annotation
        ax.text(0.98, 0.02, f"Center: ({h}, {k})\nRadius: {r:.2f}", 
               transform=ax.transAxes, fontsize=9, 
               horizontalalignment='right',
               verticalalignment='bottom',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
    except Exception as e:
        # Fallback to simple unit circle if parsing fails
        theta = np.linspace(0, 2*np.pi, 1000)
        x_circle = np.cos(theta)
        y_circle = np.sin(theta)
        ax.plot(x_circle, y_circle, linewidth=2, label="Circle", color='blue')
        ax.set_aspect('equal')
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
