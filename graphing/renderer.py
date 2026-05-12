import numpy as np
from sympy import lambdify

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
        expr = parse_user_equation(equation)
        x_vals = np.linspace(x_min, x_max, points)
        y_vals = _eval_expr(expr, x_vals)
        ax.plot(x_vals, y_vals, linewidth=2, label="f(x)")
        xlim, ylim = autoscale_limits(x_vals, y_vals)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.legend(loc="upper left")
        ax.set_title(f"y = {expr}")
    except Exception as exc:  # noqa: BLE001
        ax.text(0.5, 0.5, f"Plot error:\n{exc}", ha="center", va="center", transform=ax.transAxes)


def plot_derivative(ax, equation: str) -> None:
    expr = parse_user_equation(equation)
    sample_and_plot(ax, equation)
    x_vals = np.linspace(-10, 10, 1200)
    dydx = _eval_expr(derivative(expr), x_vals)
    ax.plot(x_vals, dydx, linewidth=1.8, linestyle="--", label="f'(x)")
    ax.legend(loc="upper left")


def plot_integral_area(ax, equation: str, a: float = -2, b: float = 2) -> None:
    expr = parse_user_equation(equation)
    sample_and_plot(ax, equation)
    x_vals = np.linspace(a, b, 400)
    y_vals = _eval_expr(expr, x_vals)
    ax.fill_between(x_vals, y_vals, alpha=0.25, label=f"Area [{a}, {b}]")
    ax.legend(loc="upper left")
