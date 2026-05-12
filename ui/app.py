import customtkinter as ctk

from ui.graph_panel import GraphPanel
from ui.sidebar import Sidebar


class LocusApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.geometry("1400x800")
        self.title("Locus Desktop")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.graph_panel = GraphPanel(self)
        self.graph_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)

        self.sidebar = Sidebar(self, on_plot=self.graph_panel.plot_equation)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=16, pady=16)
