"""Central design tokens for MediaForge's UI.

A single, neutral, professional palette (inspired by Linear / Notion / Raycast)
so every page stays visually consistent. Colours are ``(light, dark)`` tuples
that CustomTkinter resolves for the active appearance mode.
"""
from __future__ import annotations

import customtkinter as ctk

# -- layout -----------------------------------------------------------------
SIDEBAR_W = 210          # sidebar width in logical px
CONTENT_W = 700          # max width of the centred content column
GUTTER = 24              # min horizontal breathing room either side

# -- surfaces ---------------------------------------------------------------
APP_BG = ("#f6f7f9", "#0c0d11")
SIDEBAR_BG = ("#eceef1", "#101218")
CARD_BG = ("#ffffff", "#15171f")
CARD_HOVER = ("#eef0f3", "#1b1e27")
INPUT_BG = ("#ffffff", "#191c25")
BORDER = ("#e3e6ea", "#262a35")

# -- text -------------------------------------------------------------------
TEXT = ("#15171f", "#e6e8ee")
TEXT_MUTED = ("#5f6571", "#9398a6")
TEXT_FAINT = ("#9298a4", "#565b69")

# -- accent (refined indigo — deliberately less "bright blue") ---------------
ACCENT = "#6366f1"
ACCENT_HOVER = "#4f52e0"
ACCENT_SOFT = ("#ecedfe", "#1e2033")   # subtle fill for the active nav item
ON_ACCENT = "#ffffff"

# -- status -----------------------------------------------------------------
OK = "#22c55e"
OK_HOVER = "#16a34a"
ERR = "#ef4444"
ERR_HOVER = "#dc2626"
WARN = "#f59e0b"

# -- typography -------------------------------------------------------------
FAMILY = "Segoe UI"      # native on Windows; CTk falls back gracefully elsewhere


def font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    """A themed font. Must be called after the Tk root exists."""
    return ctk.CTkFont(family=FAMILY, size=size, weight=weight)


def center_column(parent, row: int = 0, max_w: int = CONTENT_W, gutter: int = GUTTER):
    """Grid a centred, max-width content frame into *parent* and return it.

    The two spacer columns soak up extra width on large/ultrawide displays so
    content stays a comfortable reading width, while ``minsize`` keeps a gutter
    on small screens. Children should be gridded into column 0 of the result.
    """
    parent.grid_columnconfigure(0, weight=1, minsize=gutter)
    parent.grid_columnconfigure(1, weight=0, minsize=max_w)
    parent.grid_columnconfigure(2, weight=1, minsize=gutter)
    content = ctk.CTkFrame(parent, fg_color="transparent")
    content.grid(row=row, column=1, sticky="new")
    content.grid_columnconfigure(0, weight=1)
    return content


# -- reusable widget styles -------------------------------------------------
def style_segmented(widget: ctk.CTkSegmentedButton):
    widget.configure(
        fg_color=INPUT_BG, selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
        unselected_color=INPUT_BG, unselected_hover_color=CARD_HOVER,
        text_color=TEXT, text_color_disabled=TEXT_FAINT, corner_radius=8,
    )


def style_optionmenu(widget: ctk.CTkOptionMenu):
    widget.configure(
        fg_color=INPUT_BG, button_color=INPUT_BG, button_hover_color=CARD_HOVER,
        text_color=TEXT, corner_radius=8,
    )


def primary_button(master, **kw) -> ctk.CTkButton:
    """The dominant call-to-action button."""
    opts = dict(
        fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=ON_ACCENT,
        corner_radius=12, font=font(15, "bold"),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def ghost_button(master, **kw) -> ctk.CTkButton:
    """A quiet, secondary button (transparent with a hairline border)."""
    opts = dict(
        fg_color="transparent", hover_color=CARD_HOVER, text_color=TEXT,
        border_width=1, border_color=BORDER, corner_radius=8, font=font(13),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)
