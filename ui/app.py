import customtkinter as ctk

from ui.graph_panel import GraphPanel
from ui.sidebar import Sidebar
from ui.themes import APP_TITLE, WINDOW_SIZE


class LocusApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry(WINDOW_SIZE)
        self.title(APP_TITLE)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.graph_panel = GraphPanel(self)
        self.graph_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)

        self.sidebar = Sidebar(
            self,
            on_plot=self.graph_panel.plot_equation,
            on_derivative=self.graph_panel.plot_derivative,
            on_integral=self.graph_panel.plot_integral_area,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=16, pady=16)
