"""Central design tokens for Tukdify Video Downloader.

Exact Tukdify Master Brand alignment:
  - Deep Obsidian surfaces (#0A0D14, #0E131F, #141A29, #1A2236)
  - Trust Blue (#2563EB, #1D4ED8)
  - Technical Cyan (#06B6D4, #0891B2)
  - Restrained Violet (#8B5CF6)
  - Metal Silver (#E2E8F0, #94A3B8)
"""
from __future__ import annotations

import customtkinter as ctk

# -- layout -----------------------------------------------------------------
SIDEBAR_W = 220          # sidebar width in logical px
CONTENT_W = 740          # max width of the centred content column
GUTTER = 24              # min horizontal breathing room either side

# -- surfaces (light, dark) -------------------------------------------------
APP_BG = ("#f4f6f9", "#0a0d14")
SIDEBAR_BG = ("#eaedf3", "#0e131f")
CARD_BG = ("#ffffff", "#141a29")
CARD_HOVER = ("#f0f3f8", "#1a2236")
INPUT_BG = ("#ffffff", "#10141f")
BORDER = ("#dbe1ea", "#222d42")
BORDER_HOVER = ("#94a3b8", "#334155")

# -- text (light, dark) -----------------------------------------------------
TEXT = ("#0f172a", "#f8fafc")
TEXT_MUTED = ("#475569", "#94a3b8")
TEXT_FAINT = ("#64748b", "#64748b")

# -- Tukdify Master Accents -------------------------------------------------
# Trust Blue (Primary CTA, Active Navigation)
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
ACCENT_SOFT = ("#dbeafe", "#172554")
ON_ACCENT = "#ffffff"

# Technical Cyan (Speed, Metrics, Progress fill)
CYAN = "#06b6d4"
CYAN_HOVER = "#0891b2"
CYAN_SOFT = ("#cffafe", "#164e63")
ON_CYAN = "#ffffff"

# Restrained Violet (Ecosystem bridge: Clips, Multicompressor)
VIOLET = "#8b5cf6"
VIOLET_HOVER = "#7c3aed"
VIOLET_SOFT = ("#ede9fe", "#2e1065")
ON_VIOLET = "#ffffff"

# -- status -----------------------------------------------------------------
OK = "#10b981"
OK_HOVER = "#059669"
ERR = "#ef4444"
ERR_HOVER = "#dc2626"
WARN = "#f59e0b"
WARN_HOVER = "#d97706"

# -- typography -------------------------------------------------------------
FAMILY = "Segoe UI"      # native on Windows; CTk falls back gracefully elsewhere
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
        text_color=TEXT, text_color_disabled=TEXT_FAINT, corner_radius=10,
    )


def style_optionmenu(widget: ctk.CTkOptionMenu):
    widget.configure(
        fg_color=INPUT_BG, button_color=INPUT_BG, button_hover_color=CARD_HOVER,
        text_color=TEXT, corner_radius=10,
    )


def primary_button(master, **kw) -> ctk.CTkButton:
    """The dominant Trust Blue call-to-action button."""
    opts = dict(
        fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=ON_ACCENT,
        corner_radius=10, font=font(14, "bold"),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def cyan_button(master, **kw) -> ctk.CTkButton:
    """A Technical Cyan highlight button (Analyze / Quick Action)."""
    opts = dict(
        fg_color=CYAN, hover_color=CYAN_HOVER, text_color=ON_CYAN,
        corner_radius=10, font=font(13, "bold"),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def violet_button(master, **kw) -> ctk.CTkButton:
    """An ecosystem bridge button (Edit in Clips / Multicompressor)."""
    opts = dict(
        fg_color=VIOLET_SOFT, hover_color=VIOLET, text_color=VIOLET,
        corner_radius=8, font=font(12, "bold"), border_width=1, border_color=BORDER,
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)


def ghost_button(master, **kw) -> ctk.CTkButton:
    """A secondary button (transparent surface with subtle border)."""
    opts = dict(
        fg_color="transparent", hover_color=CARD_HOVER, text_color=TEXT,
        border_width=1, border_color=BORDER, corner_radius=8, font=font(13),
    )
    opts.update(kw)
    return ctk.CTkButton(master, **opts)

