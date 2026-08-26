import customtkinter as ctk
from collections.abc import Callable

from ui.themes import PANEL_BG, SURFACE_BG, BORDER_COLOR, COLOR_AMBER, COLOR_CYAN, COLOR_MAGENTA, FONT_HEADER, FONT_SMALL, FONT_BODY, FONT_SMALL_BOLD


class AnimationToolbar(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkFrame,
        on_play_toggle: Callable[[], bool],
        on_step_fw: Callable[[], None],
        on_step_bw: Callable[[], None],
        on_reset: Callable[[], None],
        on_scrub: Callable[[float], None],
        on_speed_change: Callable[[str], None],
        on_mode_change: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color=PANEL_BG, corner_radius=8, border_width=1, border_color=BORDER_COLOR)

        self.on_play_toggle = on_play_toggle
        self.on_step_fw = on_step_fw
        self.on_step_bw = on_step_bw
        self.on_reset = on_reset
        self.on_scrub = on_scrub
        self.on_speed_change = on_speed_change
        self.on_mode_change = on_mode_change

        self.grid_columnconfigure(4, weight=1)  # Scrubber takes available space

        # 1. Reset Button
        self.btn_reset = ctk.CTkButton(
            self, text="⏹", width=36, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR, command=self._handle_reset
        )
        self.btn_reset.grid(row=0, column=0, padx=(8, 2), pady=6)

        # 2. Step Backward
        self.btn_bw = ctk.CTkButton(
            self, text="⏮", width=36, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR, command=self.on_step_bw
        )
        self.btn_bw.grid(row=0, column=1, padx=2, pady=6)

        # 3. Play / Pause Button
        self.btn_play = ctk.CTkButton(
            self, text="▶ Play", width=80, height=32, fg_color=COLOR_AMBER, text_color="#090A0F",
            hover_color="#EAB308", font=FONT_HEADER, command=self._handle_play
        )
        self.btn_play.grid(row=0, column=2, padx=4, pady=6)

        # 4. Step Forward
        self.btn_fw = ctk.CTkButton(
            self, text="⏭", width=36, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR, command=self.on_step_fw
        )
        self.btn_fw.grid(row=0, column=3, padx=2, pady=6)

        # 5. Scrubber Slider
        self.slider_scrub = ctk.CTkSlider(
            self, from_=0, to=99, number_of_steps=100, button_color=COLOR_AMBER, button_hover_color=COLOR_MAGENTA,
            progress_color=COLOR_AMBER, command=self._handle_scrub
        )
        self.slider_scrub.set(0)
        self.slider_scrub.grid(row=0, column=4, padx=12, pady=6, sticky="ew")

        # 6. Speed Menu
        self.speed_option = ctk.CTkOptionMenu(
            self, values=["0.25x", "0.5x", "1.0x", "2.0x", "4.0x"], width=80, height=32,
            fg_color=SURFACE_BG, button_color=BORDER_COLOR, font=FONT_SMALL, command=self.on_speed_change
        )
        self.speed_option.set("1.0x")
        self.speed_option.grid(row=0, column=5, padx=4, pady=6)

        # 7. Animation Mode Menu
        self.mode_option = ctk.CTkOptionMenu(
            self, values=["Trace Draw", "Tangent Glide", "Riemann Accumulator", "Parameter Sweep"], width=160, height=32,
            fg_color=SURFACE_BG, button_color=BORDER_COLOR, font=FONT_SMALL, command=self.on_mode_change
        )
        self.mode_option.set("Trace Draw")
        self.mode_option.grid(row=0, column=6, padx=(4, 8), pady=6)

    def _handle_play(self) -> None:
        is_playing = self.on_play_toggle()
        if is_playing:
            self.btn_play.configure(text="⏸ Pause", fg_color=COLOR_MAGENTA, text_color="#FFFFFF")
        else:
            self.btn_play.configure(text="▶ Play", fg_color=COLOR_AMBER, text_color="#090A0F")

    def _handle_reset(self) -> None:
        self.btn_play.configure(text="▶ Play", fg_color=COLOR_AMBER, text_color="#090A0F")
        self.slider_scrub.set(0)
        self.on_reset()

    def _handle_scrub(self, val: float) -> None:
        self.on_scrub(val)

    def update_scrubber(self, frame: int) -> None:
        self.slider_scrub.set(frame)


class NavControlToolbar(ctk.CTkFrame):
    """Sleek CustomTkinter Navigation Bar replacing standard Matplotlib toolbar."""
    def __init__(
        self,
        master: ctk.CTkFrame,
        on_home: Callable[[], None],
        on_pan_toggle: Callable[[], bool],
        on_zoom_toggle: Callable[[], bool],
        on_save: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color=PANEL_BG, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        
        self.on_home = on_home
        self.on_pan_toggle = on_pan_toggle
        self.on_zoom_toggle = on_zoom_toggle
        self.on_save = on_save

        # 1. Home / Reset View
        self.btn_home = ctk.CTkButton(
            self, text="⌂ Reset", width=68, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR,
            font=FONT_SMALL_BOLD, command=self._handle_home
        )
        self.btn_home.pack(side="left", padx=4, pady=4)

        # 2. Pan Mode
        self.btn_pan = ctk.CTkButton(
            self, text="↔ Pan", width=64, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR,
            font=FONT_SMALL_BOLD, command=self._handle_pan
        )
        self.btn_pan.pack(side="left", padx=2, pady=4)

        # 3. Zoom Box Mode
        self.btn_zoom = ctk.CTkButton(
            self, text="🔍 Zoom", width=68, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR,
            font=FONT_SMALL_BOLD, command=self._handle_zoom
        )
        self.btn_zoom.pack(side="left", padx=2, pady=4)

        # 4. Save Figure
        self.btn_save = ctk.CTkButton(
            self, text="📷 Save", width=64, height=32, fg_color=SURFACE_BG, hover_color=BORDER_COLOR,
            font=FONT_SMALL_BOLD, command=self.on_save
        )
        self.btn_save.pack(side="left", padx=(2, 4), pady=4)

    def _handle_home(self) -> None:
        self.btn_pan.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")
        self.btn_zoom.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")
        self.on_home()

    def _handle_pan(self) -> None:
        is_active = self.on_pan_toggle()
        if is_active:
            self.btn_pan.configure(fg_color=COLOR_AMBER, text_color="#090A0F")
            self.btn_zoom.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")
        else:
            self.btn_pan.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")

    def _handle_zoom(self) -> None:
        is_active = self.on_zoom_toggle()
        if is_active:
            self.btn_zoom.configure(fg_color=COLOR_AMBER, text_color="#090A0F")
            self.btn_pan.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")
        else:
            self.btn_zoom.configure(fg_color=SURFACE_BG, text_color="#FFFFFF")
