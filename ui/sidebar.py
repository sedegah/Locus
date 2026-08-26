import customtkinter as ctk
from collections.abc import Callable
from PIL import Image, ImageTk

from math_engine.analyzer import _create_math_image, get_math_analysis_data
from ui.themes import (
    BORDER_COLOR, COLOR_AMBER, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, PANEL_BG, SIDEBAR_WIDTH, SURFACE_BG,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADER, FONT_BODY, FONT_BOLD, FONT_SMALL, FONT_SMALL_BOLD
)


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        on_plot: Callable[[str], None],
        on_derivative: Callable[[str], None],
        on_integral: Callable[[str], None],
        on_riemann: Callable[[str, int, str], None],
        on_parametric: Callable[[str, str], None],
        on_polar: Callable[[str], None],
        on_3d: Callable[[str, str], None],
        on_vector: Callable[[str, str], None],
    ) -> None:
        super().__init__(master, width=SIDEBAR_WIDTH, fg_color=PANEL_BG, corner_radius=12)
        self.on_plot = on_plot
        self.on_derivative = on_derivative
        self.on_integral = on_integral
        self.on_riemann = on_riemann
        self.on_parametric = on_parametric
        self.on_polar = on_polar
        self.on_3d = on_3d
        self.on_vector = on_vector

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        
        lbl_title = ctk.CTkLabel(title_frame, text="LOCUS", font=FONT_TITLE, text_color=COLOR_AMBER)
        lbl_title.pack(side="left")
        lbl_sub = ctk.CTkLabel(title_frame, text=" Math Engine", font=FONT_SUBTITLE, text_color="#94A3B8")
        lbl_sub.pack(side="left", padx=6)

        # Mode Tabview
        self.tabview = ctk.CTkTabview(self, fg_color=SURFACE_BG, segmented_button_selected_color=COLOR_AMBER)
        self.tabview.grid(row=1, column=0, padx=12, pady=4, sticky="ew")
        
        self.tab_2d = self.tabview.add("2D & Calc")
        self.tab_para = self.tabview.add("Param & Polar")
        self.tab_3d = self.tabview.add("3D & Vector")
        self.tab_presets = self.tabview.add("Presets")

        self._build_2d_tab()
        self._build_para_tab()
        self._build_3d_tab()
        self._build_presets_tab()

        # Output Scrollable Frame for Symbolic Analysis
        lbl_out = ctk.CTkLabel(self, text="Symbolic Analysis Output", font=FONT_HEADER, text_color="#E2E8F0")
        lbl_out.grid(row=2, column=0, padx=12, pady=(8, 2), sticky="w")

        self.output_frame = ctk.CTkScrollableFrame(self, width=SIDEBAR_WIDTH - 24, height=220, fg_color=SURFACE_BG, corner_radius=8)
        self.output_frame.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self._clear_output()
        self._add_text_label("Enter an equation and click 'Analyze' to view derivatives, integrals, and domain analysis.")

    # 1. 2D Tab Construction
    def _build_2d_tab(self) -> None:
        self.eq_entry = ctk.CTkEntry(self.tab_2d, placeholder_text="e.g. y = x^3 - 3x + 1", font=FONT_HEADER)
        self.eq_entry.insert(0, "y = x^3 - 3x + 1")
        self.eq_entry.pack(fill="x", padx=6, pady=4)

        # Math Keyboard
        kb_frame = ctk.CTkFrame(self.tab_2d, fg_color="transparent")
        kb_frame.pack(fill="x", padx=4, pady=2)

        buttons = [
            ("x²", "x^2"), ("x³", "x^3"), ("√", "sqrt("), ("sin", "sin("),
            ("cos", "cos("), ("tan", "tan("), ("ln", "ln("), ("eˣ", "exp("),
            ("π", "pi"), ("|x|", "abs("), ("÷", "/"), ("×", "*")
        ]
        for i, (text, val) in enumerate(buttons):
            row, col = i // 4, i % 4
            btn = ctk.CTkButton(
                kb_frame, text=text, width=54, height=26, font=FONT_SMALL_BOLD, fg_color=PANEL_BG, hover_color=BORDER_COLOR,
                command=lambda v=val: self._insert_to_entry(self.eq_entry, v)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)

        # Actions
        btn_grid = ctk.CTkFrame(self.tab_2d, fg_color="transparent")
        btn_grid.pack(fill="x", padx=4, pady=4)

        ctk.CTkButton(btn_grid, text="Plot 2D", fg_color=COLOR_AMBER, text_color="#090A0F", font=FONT_BOLD, command=self._on_plot_click).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(btn_grid, text="Analyze", fg_color=SURFACE_BG, font=FONT_BODY, command=self._on_analyze_click).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(btn_grid, text="Derivative", fg_color=SURFACE_BG, font=FONT_BODY, command=self._on_derivative_click).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(btn_grid, text="Integral Area", fg_color=SURFACE_BG, font=FONT_BODY, command=self._on_integral_click).grid(row=1, column=1, padx=2, pady=2, sticky="ew")

        # Riemann controls
        riemann_frame = ctk.CTkFrame(self.tab_2d, fg_color=PANEL_BG, corner_radius=6)
        riemann_frame.pack(fill="x", padx=4, pady=4)

        ctk.CTkLabel(riemann_frame, text="Riemann Rectangles (N):", font=FONT_SMALL).pack(side="top", anchor="w", padx=6, pady=(4, 0))
        self.slider_n = ctk.CTkSlider(riemann_frame, from_=2, to=40, number_of_steps=38, button_color=COLOR_GREEN)
        self.slider_n.set(12)
        self.slider_n.pack(fill="x", padx=6, pady=2)

        self.method_opt = ctk.CTkOptionMenu(riemann_frame, values=["midpoint", "left", "right"], height=24, fg_color=SURFACE_BG, font=FONT_SMALL)
        self.method_opt.pack(side="left", padx=6, pady=4)

        ctk.CTkButton(riemann_frame, text="Riemann Sum", height=24, fg_color=COLOR_GREEN, text_color="#090A0F", font=FONT_SMALL_BOLD, command=self._on_riemann_click).pack(side="right", padx=6, pady=4)

    # 2. Parametric & Polar Tab
    def _build_para_tab(self) -> None:
        ctk.CTkLabel(self.tab_para, text="Parametric: x(t) & y(t)", font=FONT_BOLD).pack(anchor="w", padx=6, pady=(4, 0))
        self.entry_px = ctk.CTkEntry(self.tab_para, placeholder_text="x(t) e.g. sin(3*t)", font=FONT_BODY)
        self.entry_px.insert(0, "16*sin(t)^3")
        self.entry_px.pack(fill="x", padx=6, pady=2)

        self.entry_py = ctk.CTkEntry(self.tab_para, placeholder_text="y(t) e.g. sin(4*t)", font=FONT_BODY)
        self.entry_py.insert(0, "13*cos(t) - 5*cos(2*t) - 2*cos(3*t) - cos(4*t)")
        self.entry_py.pack(fill="x", padx=6, pady=2)

        ctk.CTkButton(self.tab_para, text="Plot Parametric", fg_color=COLOR_MAGENTA, text_color="#FFFFFF", font=FONT_BOLD, command=self._on_parametric_click).pack(fill="x", padx=6, pady=4)

        ctk.CTkLabel(self.tab_para, text="Polar: r(θ)", font=FONT_BOLD).pack(anchor="w", padx=6, pady=(8, 0))
        self.entry_polar = ctk.CTkEntry(self.tab_para, placeholder_text="r(theta) e.g. cos(4*theta)", font=FONT_BODY)
        self.entry_polar.insert(0, "cos(4*theta)")
        self.entry_polar.pack(fill="x", padx=6, pady=2)

        ctk.CTkButton(self.tab_para, text="Plot Polar Graph", fg_color=COLOR_GREEN, text_color="#090A0F", font=FONT_BOLD, command=self._on_polar_click).pack(fill="x", padx=6, pady=4)

    # 3. 3D & Vector Tab
    def _build_3d_tab(self) -> None:
        ctk.CTkLabel(self.tab_3d, text="3D Surface: z = f(x, y)", font=FONT_BOLD).pack(anchor="w", padx=6, pady=(4, 0))
        self.entry_3d = ctk.CTkEntry(self.tab_3d, placeholder_text="z = f(x, y) e.g. sin(sqrt(x^2+y^2))", font=FONT_BODY)
        self.entry_3d.insert(0, "sin(sqrt(x^2 + y^2))")
        self.entry_3d.pack(fill="x", padx=6, pady=2)

        self.cmap_opt = ctk.CTkOptionMenu(self.tab_3d, values=["viridis", "plasma", "coolwarm", "magma", "neon"], fg_color=PANEL_BG, font=FONT_SMALL)
        self.cmap_opt.pack(fill="x", padx=6, pady=2)

        ctk.CTkButton(self.tab_3d, text="Plot 3D Surface", fg_color=COLOR_AMBER, text_color="#090A0F", font=FONT_BOLD, command=self._on_3d_click).pack(fill="x", padx=6, pady=4)

        ctk.CTkLabel(self.tab_3d, text="Vector Field: dx/dt & dy/dt", font=FONT_BOLD).pack(anchor="w", padx=6, pady=(8, 0))
        self.entry_dx = ctk.CTkEntry(self.tab_3d, placeholder_text="dx/dt e.g. y", font=FONT_BODY)
        self.entry_dx.insert(0, "y")
        self.entry_dx.pack(fill="x", padx=6, pady=2)

        self.entry_dy = ctk.CTkEntry(self.tab_3d, placeholder_text="dy/dt e.g. -x - 0.2*y", font=FONT_BODY)
        self.entry_dy.insert(0, "-x - 0.2*y")
        self.entry_dy.pack(fill="x", padx=6, pady=2)

        ctk.CTkButton(self.tab_3d, text="Plot Vector Field", fg_color=COLOR_MAGENTA, text_color="#FFFFFF", font=FONT_BOLD, command=self._on_vector_click).pack(fill="x", padx=6, pady=4)

    # 4. Presets Tab
    def _build_presets_tab(self) -> None:
        presets = [
            ("Heart Curve", "para", ("16*sin(t)^3", "13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t)")),
            ("Rhodonea Rose", "polar", "cos(4*theta)"),
            ("Lissajous Knot", "para", ("sin(3*t)", "sin(4*t)")),
            ("Damped Oscillation", "2d", "exp(-0.3*x)*cos(3*x)"),
            ("3D Ripple Wave", "3d", "sin(sqrt(x^2+y^2))"),
            ("3D Saddle Surface", "3d", "x^2 - y^2"),
            ("Vector Oscillator", "vector", ("y", "-x - 0.2*y")),
        ]
        for name, ptype, val in presets:
            btn = ctk.CTkButton(
                self.tab_presets, text=f"✦ {name}", anchor="w", fg_color=PANEL_BG, hover_color=BORDER_COLOR, font=FONT_BODY,
                command=lambda t=ptype, v=val: self._load_preset(t, v)
            )
            btn.pack(fill="x", padx=6, pady=2)

    # Helpers
    def _insert_to_entry(self, entry_widget, text: str) -> None:
        pos = entry_widget.index(ctk.INSERT)
        curr = entry_widget.get()
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, curr[:pos] + text + curr[pos:])
        entry_widget.icursor(pos + len(text))

    def _load_preset(self, ptype: str, val) -> None:
        if ptype == "2d":
            self.eq_entry.delete(0, ctk.END)
            self.eq_entry.insert(0, val)
            self.on_plot(val)
        elif ptype == "para":
            self.on_parametric(val[0], val[1])
        elif ptype == "polar":
            self.on_polar(val)
        elif ptype == "3d":
            self.on_3d(val, "viridis")
        elif ptype == "vector":
            self.on_vector(val[0], val[1])

    # Button Event Handlers
    def _on_plot_click(self) -> None:
        self.on_plot(self.eq_entry.get().strip())

    def _on_derivative_click(self) -> None:
        self.on_derivative(self.eq_entry.get().strip())

    def _on_integral_click(self) -> None:
        self.on_integral(self.eq_entry.get().strip())

    def _on_riemann_click(self) -> None:
        n = int(self.slider_n.get())
        method = self.method_opt.get()
        self.on_riemann(self.eq_entry.get().strip(), n, method)

    def _on_parametric_click(self) -> None:
        self.on_parametric(self.entry_px.get().strip(), self.entry_py.get().strip())

    def _on_polar_click(self) -> None:
        self.on_polar(self.entry_polar.get().strip())

    def _on_3d_click(self) -> None:
        self.on_3d(self.entry_3d.get().strip(), self.cmap_opt.get())

    def _on_vector_click(self) -> None:
        self.on_vector(self.entry_dx.get().strip(), self.entry_dy.get().strip())

    def _on_analyze_click(self) -> None:
        self._clear_output()
        data = get_math_analysis_data(self.eq_entry.get().strip())
        if "error" in data:
            self._add_text_label(data["error"])
            return

        self._add_math_image(data["original"], "Function f(x):")
        self._add_math_image(data["derivative"], "First Derivative f'(x):")
        self._add_math_image(data["second_derivative"], "Second Derivative f''(x):")
        self._add_math_image(data["real_roots"], "Real Roots:")
        self._add_math_image(data["critical_points"], "Critical Points:")
        self._add_math_image(data["integral"], "Indefinite Integral:")
        self._add_text_label(f"Domain: {data['domain']}")

    def _clear_output(self) -> None:
        for widget in self.output_frame.winfo_children():
            widget.destroy()

    def _add_text_label(self, text: str) -> None:
        label = ctk.CTkLabel(self.output_frame, text=text, wraplength=280, justify="left", text_color="#A0A0A0")
        label.pack(pady=2, padx=5, anchor="w")

    def _add_math_image(self, math_text: str, label_text: str = "") -> None:
        if label_text:
            self._add_text_label(label_text)
        try:
            img = _create_math_image(math_text, fontsize=11)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            lbl = ctk.CTkLabel(self.output_frame, image=ctk_img, text="")
            lbl.pack(pady=4, padx=5)
        except Exception as e:
            self._add_text_label(f"Render Error: {e}")
