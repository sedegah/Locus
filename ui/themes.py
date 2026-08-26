import os
import customtkinter as ctk
import matplotlib as mpl
import matplotlib.font_manager as fm

APP_TITLE = "Locus — Advanced Mathematical Visualization Engine"
WINDOW_SIZE = "1400x900"
SIDEBAR_WIDTH = 380

# Color Palette (Aesthetic Gold & Deep Onyx / Matte Black)
BG_DARK = "#090A0F"       # Main canvas background
PANEL_BG = "#11131B"      # Sidebar and toolbar background
SURFACE_BG = "#181B26"    # Cards and nested frames
BORDER_COLOR = "#262938"   # Subtle borders

# Accent Palette
COLOR_GOLD = "#FFC72C"    # Primary Hero Amber Gold
COLOR_AMBER = "#FFC72C"   # Primary Brand Accent
COLOR_CYAN = "#00E5FF"    # Electric Cyan
COLOR_MAGENTA = "#FF2E93" # Vibrant Rose Magenta
COLOR_PURPLE = "#A855F7"  # Deep Violet Purple
COLOR_GREEN = "#10B981"   # Emerald Green
COLOR_YELLOW = "#F59E0B"  # Warm Yellow
COLOR_ORANGE = "#F97316"  # Sunset Orange

THEME_PALETTE = [COLOR_AMBER, COLOR_CYAN, COLOR_MAGENTA, COLOR_GREEN, COLOR_PURPLE, COLOR_ORANGE]

# Typography Design System — IBM Plex Sans
FONT_FAMILY = "IBM Plex Sans"

def _init_fonts():
    """Register IBM Plex Sans for CustomTkinter, Windows GDI, and Matplotlib."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonts_dir = os.path.join(base_dir, "assets", "fonts")
    regular_font = os.path.abspath(os.path.join(fonts_dir, "IBMPlexSans.ttf"))
    italic_font = os.path.abspath(os.path.join(fonts_dir, "IBMPlexSans-Italic.ttf"))

    if os.name == "nt":
        try:
            import ctypes
            gdi = ctypes.windll.gdi32
            user32 = ctypes.windll.user32
            if os.path.exists(regular_font):
                gdi.AddFontResourceExW(regular_font, 0x10, 0)
            if os.path.exists(italic_font):
                gdi.AddFontResourceExW(italic_font, 0x10, 0)
            user32.SendMessageW(0xFFFF, 0x001D, 0, 0)
        except Exception:
            pass

    if os.path.exists(regular_font):
        try:
            ctk.FontManager.load_font(regular_font)
            fm.fontManager.addfont(regular_font)
        except Exception:
            pass

    if os.path.exists(italic_font):
        try:
            ctk.FontManager.load_font(italic_font)
            fm.fontManager.addfont(italic_font)
        except Exception:
            pass

    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [FONT_FAMILY, "Segoe UI", "DejaVu Sans", "Arial"]

_init_fonts()

FONT_TITLE = (FONT_FAMILY, 26, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "italic")
FONT_HEADER = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BOLD = (FONT_FAMILY, 11, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_SMALL_BOLD = (FONT_FAMILY, 10, "bold")
FONT_MONO = ("Consolas", 11)


def apply_mpl_theme(fig, ax, is_3d=False):
    """Apply high-end onyx & gold cyber styling to a Matplotlib figure and axis."""
    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)
    
    if is_3d:
        try:
            fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
        except Exception:
            pass
        # 3D Axes styling
        xaxis = getattr(ax, "xaxis", getattr(ax, "w_xaxis", None))
        yaxis = getattr(ax, "yaxis", getattr(ax, "w_yaxis", None))
        zaxis = getattr(ax, "zaxis", getattr(ax, "w_zaxis", None))
        
        pane_bg = (0.07, 0.08, 0.11, 1.0)
        if xaxis and hasattr(xaxis, "set_pane_color"):
            xaxis.set_pane_color(pane_bg)
        if yaxis and hasattr(yaxis, "set_pane_color"):
            yaxis.set_pane_color(pane_bg)
        if zaxis and hasattr(zaxis, "set_pane_color"):
            zaxis.set_pane_color(pane_bg)
        
        ax.xaxis.label.set_color("#CBD5E1")
        ax.yaxis.label.set_color("#CBD5E1")
        ax.zaxis.label.set_color("#CBD5E1")
        
        ax.tick_params(colors="#94A3B8")
    else:
        try:
            fig.subplots_adjust(left=0.06, right=0.97, top=0.93, bottom=0.08)
        except Exception:
            pass
        # 2D Axes styling
        ax.set_aspect('auto')
        ax.tick_params(colors="#94A3B8", which='both', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)
            spine.set_linewidth(1.2)
        
        ax.xaxis.label.set_color("#CBD5E1")
        ax.yaxis.label.set_color("#CBD5E1")
        ax.title.set_color("#F8FAFC")
        ax.title.set_fontsize(11)
        ax.title.set_weight("bold")
        
        ax.grid(True, linestyle="--", alpha=0.22, color="#33384B")

