from collections.abc import Callable

import customtkinter as ctk

from math_engine.analyzer import summarize_expression
from math_engine.parser import parse_user_equation


class Sidebar(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, on_plot: Callable[[str], None]) -> None:
        super().__init__(master, width=320)
        self.on_plot = on_plot

        self.grid_rowconfigure(6, weight=1)

        self.title = ctk.CTkLabel(self, text="Locus Desktop", font=("Inter", 22, "bold"))
        self.title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.input_label = ctk.CTkLabel(self, text="Equation")
        self.input_label.grid(row=1, column=0, padx=12, pady=(6, 4), sticky="w")

        self.equation_entry = ctk.CTkEntry(self, width=280, placeholder_text="Enter equation, e.g. y=x^2+3x")
        self.equation_entry.grid(row=2, column=0, padx=12, pady=4, sticky="ew")

        self.plot_button = ctk.CTkButton(self, text="Plot", command=self._plot_clicked)
        self.plot_button.grid(row=3, column=0, padx=12, pady=8, sticky="ew")

        self.analyze_button = ctk.CTkButton(self, text="Analyze", command=self._analyze_clicked)
        self.analyze_button.grid(row=4, column=0, padx=12, pady=(0, 8), sticky="ew")

        self.output = ctk.CTkTextbox(self, width=280, height=260)
        self.output.grid(row=5, column=0, padx=12, pady=(4, 12), sticky="nsew")
        self.output.insert("1.0", "Analysis output will appear here.")

    def _plot_clicked(self) -> None:
        self.on_plot(self.equation_entry.get())

    def _analyze_clicked(self) -> None:
        raw = self.equation_entry.get()
        expr = parse_user_equation(raw)
        report = summarize_expression(expr)
        self.output.delete("1.0", "end")
        self.output.insert("1.0", report)
