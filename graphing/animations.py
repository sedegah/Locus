import numpy as np
import matplotlib.pyplot as plt
from sympy import lambdify, symbols, sympify

from graphing.renderer import _eval_1d, _is_circle_or_implicit, parse_user_equation
from graphing.sampling import sanitize_eval_values
from symbolic.derivatives import derivative
from ui.themes import (
    COLOR_AMBER, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_ORANGE, COLOR_PURPLE, COLOR_YELLOW,
    PANEL_BG, apply_mpl_theme
)

x_sym = symbols("x")


class AnimationEngine:
    def __init__(self, canvas_update_cb=None) -> None:
        self.canvas_update_cb = canvas_update_cb
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 100
        self.speed = 1.0  # Speed multiplier
        self.mode = "Trace Draw"
        self._timer_id = None
        self.tk_root = None

    def set_root(self, root) -> None:
        self.tk_root = root

    def play(self) -> None:
        if not self.is_playing:
            self.is_playing = True
            self._schedule_next_frame()

    def pause(self) -> None:
        self.is_playing = False
        if self._timer_id and self.tk_root:
            try:
                self.tk_root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

    def toggle_play(self) -> bool:
        if self.is_playing:
            self.pause()
        else:
            self.play()
        return self.is_playing

    def reset(self) -> None:
        self.pause()
        self.current_frame = 0
        self._notify_update()

    def step_forward(self) -> None:
        self.pause()
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self._notify_update()

    def step_backward(self) -> None:
        self.pause()
        self.current_frame = (self.current_frame - 1) % self.total_frames
        self._notify_update()

    def set_frame(self, frame: int) -> None:
        self.current_frame = max(0, min(int(frame), self.total_frames - 1))
        self._notify_update()

    def set_speed(self, speed: float) -> None:
        self.speed = max(0.1, min(float(speed), 5.0))

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.reset()

    def _schedule_next_frame(self) -> None:
        if not self.is_playing or not self.tk_root:
            return
        
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self._notify_update()

        interval_ms = int(35 / self.speed)
        self._timer_id = self.tk_root.after(interval_ms, self._schedule_next_frame)

    def _notify_update(self) -> None:
        if self.canvas_update_cb:
            try:
                self.canvas_update_cb(self.current_frame, self.mode)
            except Exception as e:
                print(f"Animation update callback error: {e}")


def render_animation_frame(ax, fig, equation: str, frame: int, total_frames: int = 100, mode: str = "Trace Draw", current_graph_mode: str = "2D") -> None:
    """Render a single frame for the selected animation mode onto the Matplotlib axes."""
    
    if current_graph_mode == "3D":
        _render_3d_orbit_frame(ax, fig, equation, frame, total_frames)
        return

    try:
        expr = parse_user_equation(equation)
    except Exception:
        return

    if mode == "Trace Draw":
        _render_trace_draw_frame(ax, expr, frame, total_frames)
    elif mode == "Tangent Glide":
        _render_tangent_glide_frame(ax, expr, frame, total_frames)
    elif mode == "Riemann Accumulator":
        _render_riemann_accumulator_frame(ax, expr, frame, total_frames)
    elif mode == "Parameter Sweep":
        _render_parameter_sweep_frame(ax, expr, frame, total_frames)


def _render_trace_draw_frame(ax, expr, frame: int, total_frames: int) -> None:
    """Animates progressive curve tracing from left to right."""
    x_min, x_max = -10.0, 10.0
    progress_ratio = (frame + 1) / float(total_frames)
    x_curr_max = x_min + (x_max - x_min) * progress_ratio

    full_x = np.linspace(x_min, x_max, 1200)
    full_y = sanitize_eval_values(full_x, _eval_1d(expr, full_x))

    trace_x = np.linspace(x_min, x_curr_max, max(10, int(1200 * progress_ratio)))
    trace_y = sanitize_eval_values(trace_x, _eval_1d(expr, trace_x))

    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    # Ghost full path
    ax.plot(full_x, full_y, color="#2A2F4C", linestyle="--", linewidth=1.5, alpha=0.5)

    # Animated active path
    ax.plot(trace_x, trace_y, color=COLOR_AMBER, linewidth=4, alpha=0.3)
    ax.plot(trace_x, trace_y, color=COLOR_AMBER, linewidth=2.5, label=f"Trace Draw ({int(progress_ratio*100)}%)")

    # Animated glowing tip dot
    if len(trace_x) > 0 and np.isfinite(trace_y[-1]):
        tip_x, tip_y = trace_x[-1], trace_y[-1]
        ax.plot(tip_x, tip_y, 'o', color=COLOR_AMBER, markersize=10, alpha=0.4)
        ax.plot(tip_x, tip_y, 'o', color="#FFFFFF", markersize=6)

    ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.set_xlim(x_min, x_max)
    
    valid_y = full_y[np.isfinite(full_y)]
    if len(valid_y) > 0:
        ax.set_ylim(np.percentile(valid_y, 1) - 1, np.percentile(valid_y, 99) + 1)

    ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")


def _render_tangent_glide_frame(ax, expr, frame: int, total_frames: int) -> None:
    """Animates tangent line gliding along f(x) with slope readout."""
    x_min, x_max = -8.0, 8.0
    t_ratio = frame / float(total_frames - 1)
    x_pos = x_min + (x_max - x_min) * t_ratio

    d_expr = derivative(expr)

    x_vals = np.linspace(x_min, x_max, 1200)
    y_vals = sanitize_eval_values(x_vals, _eval_1d(expr, x_vals))

    y_pos = float(_eval_1d(expr, np.array([x_pos]))[0])
    slope = float(_eval_1d(d_expr, np.array([x_pos]))[0])

    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    # Plot main curve
    ax.plot(x_vals, y_vals, color=COLOR_CYAN, linewidth=2, label="f(x)")

    if np.isfinite(y_pos) and np.isfinite(slope):
        # Tangent line equation: y_tan = slope * (x - x_pos) + y_pos
        x_tan = np.linspace(x_pos - 3.5, x_pos + 3.5, 200)
        y_tan = slope * (x_tan - x_pos) + y_pos
        ax.plot(x_tan, y_tan, color=COLOR_MAGENTA, linewidth=2.5, linestyle="-", label=f"Tangent (Slope = {slope:.2f})")

        # Contact point
        ax.plot(x_pos, y_pos, 'o', color=COLOR_YELLOW, markersize=8, label=f"P({x_pos:.2f}, {y_pos:.2f})")

        # Floating annotation box
        ax.text(0.98, 0.05, f"Point: ({x_pos:.2f}, {y_pos:.2f})\nSlope f'(x): {slope:.3f}", 
                transform=ax.transAxes, fontsize=10, color="#FFFFFF", ha="right", va="bottom",
                bbox=dict(boxstyle="round,pad=0.5", facecolor=PANEL_BG, edgecolor=COLOR_MAGENTA, alpha=0.85))

    ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.set_xlim(x_min, x_max)

    valid_y = y_vals[np.isfinite(y_vals)]
    if len(valid_y) > 0:
        ax.set_ylim(np.percentile(valid_y, 1) - 2, np.percentile(valid_y, 99) + 2)

    ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")


def _render_riemann_accumulator_frame(ax, expr, frame: int, total_frames: int) -> None:
    """Animates sub-intervals N increasing from 1 to 40."""
    n = max(1, int(1 + (frame / float(total_frames)) * 39))
    a, b = -3.0, 3.0
    dx = (b - a) / n

    x_vals = np.linspace(a - 2, b + 2, 1000)
    y_vals = sanitize_eval_values(x_vals, _eval_1d(expr, x_vals))

    x_mid = np.linspace(a + dx/2, b - dx/2, n)
    y_mid = _eval_1d(expr, x_mid)
    approx_area = np.sum(y_mid * dx)

    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    ax.plot(x_vals, y_vals, color=COLOR_CYAN, linewidth=2.5, label="f(x)")

    x_lefts = np.linspace(a, b - dx, n)
    for x_l, height in zip(x_lefts, y_mid):
        if np.isfinite(height):
            ax.add_patch(plt.Rectangle(
                (x_l, 0 if height >= 0 else height), 
                dx, 
                abs(height),
                facecolor=COLOR_PURPLE,
                edgecolor=COLOR_GREEN,
                alpha=0.45,
                linewidth=1.2
            ))

    ax.set_title(f"Riemann Area Convergence (N={n} Rectangles) $\\approx {approx_area:.4f}$", color="#FFFFFF", fontsize=11)
    ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.set_xlim(a - 1.5, b + 1.5)
    
    valid_y = y_vals[np.isfinite(y_vals)]
    if len(valid_y) > 0:
        ax.set_ylim(np.percentile(valid_y, 1) - 1, np.percentile(valid_y, 99) + 1)


def _render_parameter_sweep_frame(ax, expr, frame: int, total_frames: int) -> None:
    """Animates parameter 'a' morphing in f(x) e.g., a * sin(a * x)."""
    t_ratio = frame / float(total_frames - 1)
    param_a = 0.5 + 3.0 * (0.5 + 0.5 * np.sin(2 * np.pi * t_ratio))  # Smooth oscillation

    x_vals = np.linspace(-8, 8, 1200)
    # Evaluate with param substitution
    try:
        fn = lambdify((x_sym, symbols("a")), expr, "numpy")
        y_vals = fn(x_vals, param_a)
    except Exception:
        y_vals = _eval_1d(expr, x_vals) * param_a

    y_clean = sanitize_eval_values(x_vals, y_vals)

    ax.clear()
    apply_mpl_theme(ax.figure, ax)

    ax.plot(x_vals, y_clean, color=COLOR_YELLOW, linewidth=3, alpha=0.3)
    ax.plot(x_vals, y_clean, color=COLOR_YELLOW, linewidth=2, label=f"Parameter $a = {param_a:.2f}$")

    ax.axhline(y=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.axvline(x=0, color="#4A5568", linewidth=0.8, linestyle="--")
    ax.set_xlim(-8, 8)
    ax.legend(loc="upper left", facecolor=PANEL_BG, edgecolor="#2A2F4C", labelcolor="#FFFFFF")


def _render_3d_orbit_frame(ax, fig, equation: str, frame: int, total_frames: int) -> None:
    """Rotates azimuth and elevation angles for 3D surface rendering."""
    azim = (frame * 3.6) % 360
    elev = 25.0 + 15.0 * np.sin(frame * (2 * np.pi / total_frames))

    ax.view_init(elev=elev, azim=azim)
