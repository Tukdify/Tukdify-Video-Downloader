"""Central design tokens for Tukdify Video Downloader.

Exact Tukdify Clips Obsidian Studio Design System (Claude & Lovable design skills):
  - Deep obsidian studio canvas: #0e1017
  - Primary card & section panels: #171923
  - Inset wells, inputs, list rows: #1f212d
  - Elevated surfaces, popovers, hover states: #252838
  - Structural borders: #2b2f42 / Hover: #3b415a
  - Vivid Indigo brand accent: #6366f1 (Hover: #7a7dff, Pressed: #4f52d6)
  - Accessible high-contrast typography: #f0f2f8, muted: #8b92a7, faint: #52576d
  - Semantic status: Success (#10b981), Warning (#f59e0b), Error (#ef4444)
"""
from __future__ import annotations

import customtkinter as ctk

# -- layout -----------------------------------------------------------------
SIDEBAR_W = 224          # sidebar width in logical px
CONTENT_W = 760          # max width of the centred content column
GUTTER = 24              # min horizontal breathing room either side

# -- surfaces (light, dark) -------------------------------------------------
APP_BG = ("#f6f8fb", "#0e1017")
SIDEBAR_BG = ("#edf0f6", "#12141d")
CARD_BG = ("#ffffff", "#171923")
CARD_HOVER = ("#f1f4f9", "#252838")
INPUT_BG = ("#f8fafc", "#1f212d")
INPUT_BORDER = ("#d5dbe5", "#2b2f42")
BORDER = ("#dbe1ea", "#2b2f42")
BORDER_HOVER = ("#94a3b8", "#3b415a")
BORDER_FOCUS = "#6366f1"

# -- text (light, dark) -----------------------------------------------------
TEXT = ("#0f172a", "#f0f2f8")
TEXT_MUTED = ("#475569", "#8b92a7")
TEXT_FAINT = ("#64748b", "#52576d")

# -- Tukdify Clips Vivid Indigo Accent --------------------------------------
ACCENT = "#6366f1"
ACCENT_HOVER = "#7a7dff"
ACCENT_PRESSED = "#4f52d6"
ACCENT_SOFT = ("#e0e7ff", "#1e1b4b")
ON_ACCENT = "#ffffff"

# -- semantic status --------------------------------------------------------
SUCCESS = "#10b981"
SUCCESS_HOVER = "#059669"
SUCCESS_SOFT = ("#d1fae5", "#064e3b")

WARNING = "#f59e0b"
WARNING_HOVER = "#d97706"
WARNING_SOFT = ("#fef3c7", "#78350f")

ERROR = "#ef4444"
ERROR_HOVER = "#dc2626"
ERROR_SOFT = ("#fee2e2", "#7f1d1d")

# Backward compatibility aliases
OK = SUCCESS
OK_HOVER = SUCCESS_HOVER
WARN = WARNING
WARN_HOVER = WARNING_HOVER
ERR = ERROR
ERR_HOVER = ERROR_HOVER
CYAN = ACCENT
CYAN_HOVER = ACCENT_HOVER
CYAN_SOFT = ACCENT_SOFT
ON_CYAN = ON_ACCENT
VIOLET = ACCENT
VIOLET_HOVER = ACCENT_HOVER
VIOLET_SOFT = ACCENT_SOFT
ON_VIOLET = ON_ACCENT

# -- typography -------------------------------------------------------------
FAMILY = "Segoe UI"
FAMILY_MONO = "Consolas"


def font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    """A themed UI font. Must be called after the Tk root exists."""
    return ctk.CTkFont(family=FAMILY, size=size, weight=weight)


def mono_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    """A themed monospace font for speeds, bitrates, ETA and timers."""
    return ctk.CTkFont(family=FAMILY_MONO, size=size, weight=weight)


def center_column(parent, row: int = 0, max_w: int = CONTENT_W, gutter: int = GUTTER):
    """Grid a centred, max-width content frame into *parent* and return it."""
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
    """The dominant Vivid Indigo call-to-action button."""
    opts = dict(
        fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=ON_ACCENT,
        corner_radius=8, font=font(14, "bold"),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def cyan_button(master, **kw) -> ctk.CTkButton:
    """Highlight button (Analyze / Quick Action) styled with Vivid Indigo."""
    opts = dict(
        fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=ON_ACCENT,
        corner_radius=8, font=font(13, "bold"),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def violet_button(master, **kw) -> ctk.CTkButton:
    """Ecosystem bridge button (Clips, Support, Links)."""
    opts = dict(
        fg_color=ACCENT_SOFT, hover_color=ACCENT, text_color=TEXT,
        corner_radius=8, font=font(12, "bold"), border_width=1, border_color=BORDER,
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def ghost_button(master, **kw) -> ctk.CTkButton:
    """A secondary button (surface with subtle border)."""
    opts = dict(
        fg_color=INPUT_BG, hover_color=CARD_HOVER, text_color=TEXT,
        border_width=1, border_color=BORDER, corner_radius=8, font=font(13),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)
