from collections.abc import Callable

import customtkinter as ctk

from math_engine.analyzer import summarize_expression


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        on_plot: Callable[[str], None],
        on_derivative: Callable[[str], None],
        on_integral: Callable[[str], None],
    ) -> None:
        super().__init__(master, width=360)
        self.on_plot = on_plot
        self.on_derivative = on_derivative
        self.on_integral = on_integral

        self.title = ctk.CTkLabel(self, text="Locus Desktop", font=("Inter", 22, "bold"))
        self.title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.equation_entry = ctk.CTkEntry(self, width=320, placeholder_text="y=x^3-3x+1")
        self.equation_entry.grid(row=1, column=0, padx=12, pady=(8, 10), sticky="ew")

        ctk.CTkButton(self, text="Plot", command=self._plot).grid(row=2, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Analyze", command=self._analyze).grid(row=3, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Derivative", command=self._derivative).grid(row=4, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Integral Area", command=self._integral).grid(row=5, column=0, padx=12, pady=4, sticky="ew")

        self.output = ctk.CTkTextbox(self, width=320, height=340)
        self.output.grid(row=6, column=0, padx=12, pady=(8, 12), sticky="nsew")
        self.output.insert("1.0", "Analysis output will appear here.")

    def _expr(self) -> str:
        return self.equation_entry.get().strip()

    def _plot(self) -> None:
        self.on_plot(self._expr())

    def _analyze(self) -> None:
        report = summarize_expression(self._expr())
        self.output.delete("1.0", "end")
        self.output.insert("1.0", report)

    def _derivative(self) -> None:
        self.on_derivative(self._expr())

    def _integral(self) -> None:
        self.on_integral(self._expr())
