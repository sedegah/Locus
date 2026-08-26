import customtkinter as ctk

from ui.graph_panel import GraphPanel
from ui.sidebar import Sidebar
from ui.themes import APP_TITLE, BG_DARK, WINDOW_SIZE, _init_fonts


class LocusApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        _init_fonts()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.geometry(WINDOW_SIZE)
        self.title(APP_TITLE)
        self.configure(fg_color=BG_DARK)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Graph Panel
        self.graph_panel = GraphPanel(self)
        self.graph_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        # Pass root reference for animation timing loops
        self.graph_panel.set_root(self)

        # Sidebar
        self.sidebar = Sidebar(
            self,
            on_plot=self.graph_panel.plot_equation,
            on_derivative=self.graph_panel.plot_derivative,
            on_integral=self.graph_panel.plot_integral_area,
            on_riemann=self.graph_panel.plot_riemann_sum,
            on_parametric=self.graph_panel.plot_parametric,
            on_polar=self.graph_panel.plot_polar,
            on_3d=self.graph_panel.plot_3d,
            on_vector=self.graph_panel.plot_vector,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=12, pady=12)
