import numpy as np

from math_engine.parser import parse_user_equation


def sample_and_plot(ax, equation: str, x_min: float = -10, x_max: float = 10, points: int = 1200) -> None:
    ax.clear()
    ax.grid(True, alpha=0.3)

    try:
        expr = parse_user_equation(equation)
        x_vals = np.linspace(x_min, x_max, points)
        y_vals = [float(expr.subs("x", x)) for x in x_vals]

        ax.plot(x_vals, y_vals, linewidth=2)
        ax.set_title(f"y = {expr}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    except Exception as exc:  # noqa: BLE001
        ax.text(0.5, 0.5, f"Plot error:\n{exc}", ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Graph View")
