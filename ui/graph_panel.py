import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

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
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, sticky="ew")
        self.canvas.draw()

    def plot_equation(self, equation: str) -> None:
        sample_and_plot(self.ax, equation)
        self.canvas.draw_idle()

    def plot_derivative(self, equation: str) -> None:
        plot_derivative(self.ax, equation)
        self.canvas.draw_idle()

    def plot_integral_area(self, equation: str) -> None:
        plot_integral_area(self.ax, equation)
        self.canvas.draw_idle()
