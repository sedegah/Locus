import numpy as np
from sympy import lambdify, latex, symbols, sympify, Expr
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from graphing.scaling import autoscale_limits, enforce_equal_aspect
from graphing.sampling import adaptive_sample, sanitize_eval_values, sample_range
from math_engine.parser import parse_user_equation
from symbolic.derivatives import derivative
from ui.themes import (
    COLOR_AMBER, COLOR_CYAN, COLOR_MAGENTA, COLOR_PURPLE, COLOR_GREEN, 
    COLOR_YELLOW, COLOR_ORANGE, apply_mpl_theme, BG_DARK, PANEL_BG
)

x_sym, y_sym, t_sym, theta_sym = symbols("x y t theta")


def _eval_1d(expr: Expr, x_vals: np.ndarray) -> np.ndarray:
    """Evaluate 1D sympy expression safely over a numpy array."""
    try:
        fn = lambdify(x_sym, expr, modules=["numpy", {"abs": np.abs}])
        res = fn(x_vals)
        if np.isscalar(res):
            res = np.full_like(x_vals, float(res))
        return res
    except Exception:
        # Fallback elementwise eval
        res = []
        for val in x_vals:
            try:
                res.append(float(expr.evalf(subs={x_sym: val})))
            except Exception:
                res.append(np.nan)
        return np.array(res)


def _eval_2d(expr: Expr, x_vals: np.ndarray, y_vals: np.ndarray) -> np.ndarray:
    """Evaluate 2D sympy expression safely over 2D numpy meshgrids."""
    try:
        fn = lambdify((x_sym, y_sym), expr, modules=["numpy", {"abs": np.abs}])
        res = fn(x_vals, y_vals)
        if np.isscalar(res):
            res = np.full_like(x_vals, float(res))
        elif isinstance(res, np.ndarray) and res.shape != x_vals.shape:
            res = np.broadcast_to(res, x_vals.shape)
        return res
    except Exception:
        # Elementwise fallback
        Z = np.zeros_like(x_vals, dtype=float)
        for i in range(x_vals.shape[0]):
            for j in range(x_vals.shape[1]):
                try:
                    Z[i, j] = float(expr.evalf(subs={x_sym: x_vals[i, j], y_sym: y_vals[i, j]}))
                except Exception:
                    Z[i, j] = np.nan
        return Z


def sample_and_plot(ax, equation: str, x_min: float = -10, x_max: float = 10, points: int = 1500, color: str = COLOR_AMBER) -> None:
    """Main 2D Cartesian function renderer with adaptive asymptote handling."""
    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    try:
        # Check if circle equation or implicit equation
        if _is_circle_or_implicit(equation):
            _plot_implicit_conic(ax, equation)
            return

        expr = parse_user_equation(equation)
        x_vals = np.linspace(x_min, x_max, points)
        y_raw = _eval_1d(expr, x_vals)
        y_vals = sanitize_eval_values(x_vals, y_raw)

        # Plot glow line + main crisp line
        ax.plot(x_vals, y_vals, linewidth=4, color=color, alpha=0.3)
        ax.plot(x_vals, y_vals, linewidth=2, color=color, label=f"$y = {latex(expr)}$")

        # Zero axes lines
        ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")

        xlim, ylim = autoscale_limits(x_vals, y_vals)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)

        ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")
        ax.set_title(f"$y = {latex(expr)}$", fontsize=12)

    except Exception as exc:
        ax.text(0.5, 0.5, f"Plot Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)


def plot_derivative(ax, equation: str, x_min: float = -10, x_max: float = 10) -> None:
    """Plot base function f(x) and overlay derivative f'(x)."""
    sample_and_plot(ax, equation, x_min=x_min, x_max=x_max)

    try:
        expr = parse_user_equation(equation)
        d_expr = derivative(expr)

        x_vals = np.linspace(x_min, x_max, 1500)
        dy_raw = _eval_1d(d_expr, x_vals)
        dy_vals = sanitize_eval_values(x_vals, dy_raw)

        ax.plot(x_vals, dy_vals, linewidth=2.2, color=COLOR_MAGENTA, linestyle="--", label=f"$f'(x) = {latex(d_expr)}$")
        ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")

    except Exception as exc:
        print(f"Derivative Plot Error: {exc}")


def plot_integral_area(ax, equation: str, a: float = -2.0, b: float = 2.0) -> None:
    """Shade exact integral area between x=a and x=b."""
    sample_and_plot(ax, equation)

    try:
        expr = parse_user_equation(equation)
        x_fill = np.linspace(a, b, 500)
        y_fill = sanitize_eval_values(x_fill, _eval_1d(expr, x_fill))

        ax.fill_between(x_fill, 0, y_fill, color=COLOR_GREEN, alpha=0.35, label=f"Area [{a:.1f}, {b:.1f}]")
        ax.axvline(x=a, color=COLOR_GREEN, linestyle=":", linewidth=1.5)
        ax.axvline(x=b, color=COLOR_GREEN, linestyle=":", linewidth=1.5)
        ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")

    except Exception as exc:
        print(f"Integral Area Error: {exc}")


def plot_riemann_rectangles(ax, equation: str, a: float = -3.0, b: float = 3.0, n: int = 12, method: str = "midpoint") -> None:
    """Plot function with interactive translucent Riemann sum rectangles."""
    sample_and_plot(ax, equation, x_min=min(a - 2, -10), x_max=max(b + 2, 10))

    try:
        expr = parse_user_equation(equation)
        dx = (b - a) / n
        
        if method == "left":
            x_evals = np.linspace(a, b - dx, n)
        elif method == "right":
            x_evals = np.linspace(a + dx, b, n)
        else:  # midpoint
            x_evals = np.linspace(a + dx/2, b - dx/2, n)

        y_evals = _eval_1d(expr, x_evals)
        total_area = np.sum(y_evals * dx)

        x_lefts = np.linspace(a, b - dx, n)
        for x_l, height in zip(x_lefts, y_evals):
            if np.isfinite(height):
                ax.add_patch(plt.Rectangle(
                    (x_l, 0 if height >= 0 else height), 
                    dx, 
                    abs(height),
                    facecolor=COLOR_PURPLE,
                    edgecolor=COLOR_CYAN,
                    alpha=0.4,
                    linewidth=1.2
                ))

        ax.set_title(f"Riemann Sum ({method.title()}, N={n}) Area $\\approx {total_area:.4f}$", color="#FFFFFF", fontsize=11)

    except Exception as exc:
        print(f"Riemann Plot Error: {exc}")


def plot_parametric(ax, expr_x_str: str, expr_y_str: str, t_min: float = 0, t_max: float = 2 * np.pi, points: int = 1000) -> None:
    """Plot 2D Parametric curve (x(t), y(t))."""
    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    try:
        expr_x = sympify(expr_x_str.replace('^', '**'), locals={"t": t_sym})
        expr_y = sympify(expr_y_str.replace('^', '**'), locals={"t": t_sym})

        fn_x = lambdify(t_sym, expr_x, "numpy")
        fn_y = lambdify(t_sym, expr_y, "numpy")

        t_vals = np.linspace(t_min, t_max, points)
        x_vals = fn_x(t_vals)
        y_vals = fn_y(t_vals)

        ax.plot(x_vals, y_vals, linewidth=3, color=COLOR_MAGENTA, alpha=0.3)
        ax.plot(x_vals, y_vals, linewidth=2, color=COLOR_MAGENTA, label=f"$x(t)={latex(expr_x)}, y(t)={latex(expr_y)}$")

        ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")

        xlim, ylim = autoscale_limits(x_vals, y_vals)
        enforce_equal_aspect(ax, xlim, ylim)

        ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")
        ax.set_title(f"Parametric Curve: $t \\in [{t_min:.1f}, {t_max:.1f}]$", fontsize=11)

    except Exception as exc:
        ax.text(0.5, 0.5, f"Parametric Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)


def plot_polar(ax, expr_r_str: str, theta_min: float = 0, theta_max: float = 2 * np.pi, points: int = 1200) -> None:
    """Plot Polar equation r = f(theta)."""
    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    try:
        expr_r = sympify(expr_r_str.replace('^', '**'), locals={"theta": theta_sym, "th": theta_sym})
        fn_r = lambdify(theta_sym, expr_r, "numpy")

        theta_vals = np.linspace(theta_min, theta_max, points)
        r_vals = fn_r(theta_vals)

        # Convert polar to cartesian
        x_vals = r_vals * np.cos(theta_vals)
        y_vals = r_vals * np.sin(theta_vals)

        ax.plot(x_vals, y_vals, linewidth=3, color=COLOR_GREEN, alpha=0.3)
        ax.plot(x_vals, y_vals, linewidth=2, color=COLOR_GREEN, label=f"$r(\\theta) = {latex(expr_r)}$")

        ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")

        xlim, ylim = autoscale_limits(x_vals, y_vals)
        enforce_equal_aspect(ax, xlim, ylim)

        ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")
        ax.set_title(f"Polar Graph: $r(\\theta) = {latex(expr_r)}$", fontsize=11)

    except Exception as exc:
        ax.text(0.5, 0.5, f"Polar Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)


def plot_3d_surface(fig, ax, expr_z_str: str, x_min: float = -5, x_max: float = 5, y_min: float = -5, y_max: float = 5, cmap_name: str = "viridis") -> None:
    """Plot 3D Surface z = f(x, y)."""
    ax.clear()
    apply_mpl_theme(fig, ax, is_3d=True)

    try:
        clean_str = expr_z_str.replace('^', '**')
        if clean_str.startswith("z="):
            clean_str = clean_str[2:]

        expr_z = sympify(clean_str, locals={"x": x_sym, "y": y_sym})

        X = np.linspace(x_min, x_max, 80)
        Y = np.linspace(y_min, y_max, 80)
        X_mesh, Y_mesh = np.meshgrid(X, Y)
        Z_mesh = _eval_2d(expr_z, X_mesh, Y_mesh)

        surf = ax.plot_surface(X_mesh, Y_mesh, Z_mesh, cmap=cmap_name, edgecolor="none", alpha=0.9, antialiased=True)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"$z = {latex(expr_z)}$", fontsize=11, color="#FFFFFF")

    except Exception as exc:
        ax.text2D(0.5, 0.5, f"3D Surface Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)


def plot_vector_field(ax, dx_str: str = "1", dy_str: str = "x - y", x_min: float = -5, x_max: float = 5, y_min: float = -5, y_max: float = 5) -> None:
    """Plot 2D Vector / Slope Field."""
    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    try:
        expr_dx = sympify(dx_str.replace('^', '**'), locals={"x": x_sym, "y": y_sym})
        expr_dy = sympify(dy_str.replace('^', '**'), locals={"x": x_sym, "y": y_sym})

        X = np.linspace(x_min, x_max, 20)
        Y = np.linspace(y_min, y_max, 20)
        X_mesh, Y_mesh = np.meshgrid(X, Y)

        U = _eval_2d(expr_dx, X_mesh, Y_mesh)
        V = _eval_2d(expr_dy, X_mesh, Y_mesh)

        # Normalize vectors for slope field aesthetics
        speed = np.sqrt(U**2 + V**2)
        speed[speed == 0] = 1.0
        U_norm = U / speed
        V_norm = V / speed

        ax.quiver(X_mesh, Y_mesh, U_norm, V_norm, speed, cmap="plasma", alpha=0.85)
        ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_title(f"Vector Field: $dx/dt={latex(expr_dx)}, dy/dt={latex(expr_dy)}$", fontsize=11)

    except Exception as exc:
        ax.text(0.5, 0.5, f"Vector Field Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)


def _is_circle_or_implicit(eq_str: str) -> bool:
    """Check if equation string represents an implicit relation F(x, y) = 0."""
    try:
        expr = parse_user_equation(eq_str)
        return y_sym in expr.free_symbols
    except Exception:
        return False


def plot_implicit_conic(ax, eq_str: str) -> None:
    _plot_implicit_conic(ax, eq_str)


def _plot_implicit_conic(ax, eq_str: str) -> None:
    """Render implicit curves F(x, y) = 0 using contour plot."""
    try:
        expr = parse_user_equation(eq_str)

        X = np.linspace(-10, 10, 300)
        Y = np.linspace(-10, 10, 300)
        X_mesh, Y_mesh = np.meshgrid(X, Y)
        Z_mesh = _eval_2d(expr, X_mesh, Y_mesh)

        CS = ax.contour(X_mesh, Y_mesh, Z_mesh, levels=[0], colors=[COLOR_AMBER], linewidths=2.5)
        ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        ax.set_title(f"Implicit Curve: ${latex(expr)} = 0$", fontsize=11)

    except Exception as exc:
        ax.text(0.5, 0.5, f"Implicit Plot Error:\n{exc}", ha="center", va="center", color=COLOR_MAGENTA, transform=ax.transAxes)
