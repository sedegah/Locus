import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from graphing.animations import AnimationEngine, render_animation_frame
from graphing.renderer import (
    plot_3d_surface, plot_derivative, plot_implicit_conic, plot_integral_area,
    plot_parametric, plot_polar, plot_riemann_rectangles, plot_vector_field, sample_and_plot
)
from ui.controls import AnimationToolbar
from ui.themes import BG_DARK, COLOR_AMBER, COLOR_CYAN, COLOR_MAGENTA, PANEL_BG, apply_mpl_theme


class GraphPanel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master, fg_color=BG_DARK, corner_radius=12)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Matplotlib Figure Setup
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor(BG_DARK)
        self.ax = self.figure.add_subplot(111)
        apply_mpl_theme(self.figure, self.ax)

        # 2. Canvas & Embed
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # 3. Footer Control Bar (Animation Toolbar)
        footer_frame = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=8)
        footer_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        footer_frame.grid_columnconfigure(0, weight=1)

        # Animation Engine
        self.anim_engine = AnimationEngine(canvas_update_cb=self._on_animation_frame_tick)

        # Animation Toolbar
        self.anim_toolbar = AnimationToolbar(
            footer_frame,
            on_play_toggle=self.anim_engine.toggle_play,
            on_step_fw=self.anim_engine.step_forward,
            on_step_bw=self.anim_engine.step_backward,
            on_reset=self.anim_engine.reset,
            on_scrub=self._on_scrub,
            on_speed_change=self._on_speed_change,
            on_mode_change=self._on_anim_mode_change,
        )
        self.anim_toolbar.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        # Cursor and plot state tracking
        self.current_equation = "y = x^3 - 3x + 1"
        self.graph_mode = "2D"  # "2D", "3D", "Polar", "Parametric", "Vector"
        self.cursor_dot = None
        self.cursor_line_v = None
        self.cursor_line_h = None
        self.coord_text = None

        # Connect mouse motion event
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.canvas.mpl_connect("axes_leave_event", self._on_mouse_leave)

        # Initial default plot
        self.plot_equation(self.current_equation)

    def set_root(self, root) -> None:
        self.anim_engine.set_root(root)

    def _ensure_axes(self, is_3d: bool = False) -> None:
        """Switch between 2D standard axes and 3D projection axes."""
        if is_3d and not hasattr(self.ax, 'plot_surface'):
            self.figure.clear()
            self.ax = self.figure.add_subplot(111, projection='3d')
            apply_mpl_theme(self.figure, self.ax, is_3d=True)
            self.graph_mode = "3D"
        elif not is_3d and hasattr(self.ax, 'plot_surface'):
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            apply_mpl_theme(self.figure, self.ax, is_3d=False)
            self.graph_mode = "2D"

    def plot_equation(self, equation: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = equation
        self.anim_engine.pause()
        sample_and_plot(self.ax, equation)
        self.canvas.draw_idle()

    def plot_derivative(self, equation: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = equation
        self.anim_engine.pause()
        plot_derivative(self.ax, equation)
        self.canvas.draw_idle()

    def plot_integral_area(self, equation: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = equation
        self.anim_engine.pause()
        plot_integral_area(self.ax, equation)
        self.canvas.draw_idle()

    def plot_riemann_sum(self, equation: str, n: int = 12, method: str = "midpoint") -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = equation
        self.anim_engine.pause()
        plot_riemann_rectangles(self.ax, equation, n=n, method=method)
        self.canvas.draw_idle()

    def plot_parametric(self, expr_x: str, expr_y: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = f"x={expr_x};y={expr_y}"
        self.anim_engine.pause()
        plot_parametric(self.ax, expr_x, expr_y)
        self.canvas.draw_idle()

    def plot_polar(self, expr_r: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = expr_r
        self.anim_engine.pause()
        plot_polar(self.ax, expr_r)
        self.canvas.draw_idle()

    def plot_3d(self, expr_z: str, colormap: str = "viridis") -> None:
        self._ensure_axes(is_3d=True)
        self.current_equation = expr_z
        self.anim_engine.pause()
        plot_3d_surface(self.figure, self.ax, expr_z, cmap_name=colormap)
        self.canvas.draw_idle()

    def plot_vector(self, dx: str, dy: str) -> None:
        self._ensure_axes(is_3d=False)
        self.current_equation = f"dx={dx};dy={dy}"
        self.anim_engine.pause()
        plot_vector_field(self.ax, dx, dy)
        self.canvas.draw_idle()

    # Animation Callbacks
    def _on_animation_frame_tick(self, frame: int, mode: str) -> None:
        self.anim_toolbar.update_scrubber(frame)
        render_animation_frame(
            self.ax, self.figure, self.current_equation, frame, 
            total_frames=100, mode=mode, current_graph_mode=self.graph_mode
        )
        self.canvas.draw_idle()

    def _on_scrub(self, val: float) -> None:
        self.anim_engine.set_frame(int(val))

    def _on_speed_change(self, val: str) -> None:
        speed = float(val.replace("x", ""))
        self.anim_engine.set_speed(speed)

    def _on_anim_mode_change(self, val: str) -> None:
        self.anim_engine.set_mode(val)

    # Mouse Hover Crosshair
    def _on_mouse_move(self, event) -> None:
        if event.inaxes != self.ax or self.anim_engine.is_playing or self.graph_mode == "3D":
            return

        self._clear_cursor()

        if event.xdata is not None and event.ydata is not None:
            x_m, y_m = event.xdata, event.ydata

            # Crosshairs
            self.cursor_line_v = self.ax.axvline(x=x_m, color="#4A5568", linestyle=":", linewidth=1.0, alpha=0.7)
            self.cursor_line_h = self.ax.axhline(y=y_m, color="#4A5568", linestyle=":", linewidth=1.0, alpha=0.7)

            # Dot marker
            self.cursor_dot, = self.ax.plot(x_m, y_m, 'o', color=COLOR_AMBER, markersize=6, zorder=10)

            # Evaluate curve value at cursor x if available
            y_eval_str = f"{y_m:.2f}"
            try:
                from graphing.renderer import _eval_1d, parse_user_equation
                expr = parse_user_equation(self.current_equation)
                y_calc = float(_eval_1d(expr, np.array([x_m]))[0])
                if np.isfinite(y_calc):
                    y_eval_str = f"{y_calc:.2f}"
            except Exception:
                pass

            coord_str = f" x: {x_m:.2f}\n f(x): {y_eval_str} "
            self.coord_text = self.ax.text(
                x_m, y_m, coord_str,
                fontsize=9, color="#FFFFFF", ha="left", va="bottom",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, edgecolor=COLOR_AMBER, alpha=0.85),
                zorder=11
            )
            self.canvas.draw_idle()

    def _on_mouse_leave(self, event) -> None:
        self._clear_cursor()
        self.canvas.draw_idle()

    def _clear_cursor(self) -> None:
        if self.cursor_dot:
            try: self.cursor_dot.remove()
            except Exception: pass
            self.cursor_dot = None
        if self.cursor_line_v:
            try: self.cursor_line_v.remove()
            except Exception: pass
            self.cursor_line_v = None
        if self.cursor_line_h:
            try: self.cursor_line_h.remove()
            except Exception: pass
            self.cursor_line_h = None
        if self.coord_text:
            try: self.coord_text.remove()
            except Exception: pass
            self.coord_text = None
