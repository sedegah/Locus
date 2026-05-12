from collections.abc import Callable

import customtkinter as ctk
from PIL import Image, ImageTk

from math_engine.analyzer import get_math_analysis_data, _create_math_image


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
        self.equation_entry.grid(row=1, column=0, padx=12, pady=(8, 4), sticky="ew")

        # Create math keyboard
        self._create_math_keyboard()
        self.math_keyboard_frame.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

        ctk.CTkButton(self, text="Plot", command=self._plot).grid(row=3, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Analyze", command=self._analyze).grid(row=4, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Derivative", command=self._derivative).grid(row=5, column=0, padx=12, pady=4, sticky="ew")
        ctk.CTkButton(self, text="Integral Area", command=self._integral).grid(row=6, column=0, padx=12, pady=4, sticky="ew")

        # Create a scrollable frame for math images
        self.output_frame = ctk.CTkScrollableFrame(self, width=320, height=340)
        self.output_frame.grid(row=7, column=0, padx=12, pady=(8, 12), sticky="nsew")
        
        # Initialize with welcome message
        self._clear_output()
        self._add_text_label("Analysis output will appear here.")

    def _create_math_keyboard(self) -> None:
        """Create a compact math keyboard with commonly used functions and symbols"""
        self.math_keyboard_frame = ctk.CTkFrame(self)
        
        # Define math buttons organized by category
        math_buttons = [
            # Row 1: Powers and roots
            ("x²", "x^2"), ("x³", "x^3"), ("√x", "sqrt(x)"), ("ⁿ√x", "x**(1/n)"),
            # Row 2: Trigonometric functions
            ("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("π", "pi"),
            # Row 3: Logarithmic and exponential
            ("ln", "ln("), ("log", "log("), ("eˣ", "exp("), ("e", "e"),
            # Row 4: Operations and symbols
            ("÷", "/"), ("×", "*"), ("±", "+-"), ("|x|", "abs(x)"),
        ]
        
        # Create buttons in a grid layout
        for i, (text, insert_text) in enumerate(math_buttons):
            row = i // 4
            col = i % 4
            
            btn = ctk.CTkButton(
                self.math_keyboard_frame,
                text=text,
                width=70,
                height=28,
                font=("Inter", 11),
                command=lambda t=insert_text: self._insert_to_entry(t)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)

    def _insert_to_entry(self, text: str) -> None:
        """Insert text at the current cursor position in the equation entry"""
        current_text = self.equation_entry.get()
        cursor_pos = self.equation_entry.index(ctk.INSERT)
        
        # Insert the text at cursor position
        new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
        self.equation_entry.delete(0, ctk.END)
        self.equation_entry.insert(0, new_text)
        
        # Set cursor position after inserted text
        self.equation_entry.icursor(cursor_pos + len(text))

    def _expr(self) -> str:
        return self.equation_entry.get().strip()

    def _plot(self) -> None:
        self.on_plot(self._expr())

    def _clear_output(self) -> None:
        """Clear all widgets from the output frame"""
        for widget in self.output_frame.winfo_children():
            widget.destroy()

    def _add_text_label(self, text: str) -> None:
        """Add a text label to the output frame"""
        label = ctk.CTkLabel(self.output_frame, text=text, wraplength=280, justify="left")
        label.pack(pady=2, padx=5, anchor="w")

    def _add_math_image(self, math_text: str, label_text: str = "") -> None:
        """Add a math image with optional label"""
        if label_text:
            self._add_text_label(label_text)
        
        try:
            img = _create_math_image(math_text, fontsize=14)
            photo = ImageTk.PhotoImage(img)
            
            math_label = ctk.CTkLabel(self.output_frame, image=photo, text="")
            math_label.image = photo  # Keep a reference
            math_label.pack(pady=5, padx=5)
        except Exception as e:
            self._add_text_label(f"Math rendering error: {e}")

    def _analyze(self) -> None:
        self._clear_output()
        
        data = get_math_analysis_data(self._expr())
        
        if "error" in data:
            self._add_text_label(data["error"])
            return
        
        # Add beautiful math rendering
        self._add_math_image(data["original"], "Function:")
        self._add_math_image(data["derivative"], "First derivative:")
        self._add_math_image(data["second_derivative"], "Second derivative:")
        self._add_math_image(data['roots'], "All roots:")
        self._add_math_image(data['real_roots'], "Real roots:")
        self._add_math_image(data['imaginary_roots'], "Imaginary roots:")
        self._add_math_image(data['critical_points'], "Critical points:")
        self._add_math_image(data['inflection_points'], "Inflection points:")
        self._add_math_image(data['concavity'], "Concavity analysis:")
        self._add_math_image(data["integral"], "Indefinite integral:")
        self._add_text_label(f"Domain: {data['domain']}")

    def _derivative(self) -> None:
        self.on_derivative(self._expr())

    def _integral(self) -> None:
        self.on_integral(self._expr())
