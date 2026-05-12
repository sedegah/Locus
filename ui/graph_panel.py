import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from graphing.renderer import plot_derivative, plot_integral_area, sample_and_plot


class GraphPanel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Graph View")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        toolbar_frame = ctk.CTkFrame(self)
        toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Initialize cursor tracking
        self.cursor_dot = None
        self.coord_text = None
        self.current_equation = ""
        
        # Connect mouse motion event
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('axes_leave_event', self._on_mouse_leave)
        
        self.canvas.draw()

    def plot_equation(self, equation: str) -> None:
        self.current_equation = equation
        sample_and_plot(self.ax, equation)
        self.canvas.draw_idle()

    def plot_derivative(self, equation: str) -> None:
        self.current_equation = equation
        plot_derivative(self.ax, equation)
        self.canvas.draw_idle()

    def plot_integral_area(self, equation: str) -> None:
        self.current_equation = equation
        plot_integral_area(self.ax, equation)
        self.canvas.draw_idle()

    def _on_mouse_move(self, event):
        """Handle mouse movement over the plot"""
        if event.inaxes != self.ax:
            return
        
        # Remove previous cursor dot and text
        if self.cursor_dot:
            self.cursor_dot.remove()
            self.cursor_dot = None
        if self.coord_text:
            self.coord_text.remove()
            self.coord_text = None
        
        if event.xdata is not None and event.ydata is not None:
            # Add cursor dot
            self.cursor_dot, = self.ax.plot(event.xdata, event.ydata, 'ro', markersize=6, zorder=10)
            
            # Calculate y-value on the function if we have an equation
            y_func = event.ydata
            if self.current_equation:
                try:
                    from graphing.renderer import parse_user_equation, _eval_expr
                    import numpy as np
                    expr = parse_user_equation(self.current_equation)
                    y_func = _eval_expr(expr, np.array([event.xdata]))[0]
                except:
                    pass  # Use cursor y-value if calculation fails
            
            # Add coordinate text
            coord_str = f'({event.xdata:.2f}, {y_func:.2f})'
            self.coord_text = self.ax.text(event.xdata, event.ydata, coord_str, 
                                        fontsize=9, ha='left', va='bottom',
                                        bbox=dict(boxstyle='round,pad=0.3', 
                                                facecolor='yellow', alpha=0.7),
                                        zorder=11)
            
            # Force canvas update
            self.canvas.draw()

    def _on_mouse_leave(self, event):
        """Handle mouse leaving the plot area"""
        if self.cursor_dot:
            self.cursor_dot.remove()
            self.cursor_dot = None
        if self.coord_text:
            self.coord_text.remove()
            self.coord_text = None
        self.canvas.draw_idle()
