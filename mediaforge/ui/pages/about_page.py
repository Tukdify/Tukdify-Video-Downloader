"""About page: version, credits, and an honest scope note."""
from __future__ import annotations

import customtkinter as ctk

from ... import __version__
from ...config import logo_path
from .. import theme as t

ABOUT_TEXT = (
    "MediaForge is a free, offline, ad-free desktop downloader for video, "
    "audio, thumbnails and subtitles from YouTube and many other sites.\n\n"
    "No login. No ads. No tracking. Your downloads never leave your computer.\n\n"
    "Built with Python, yt-dlp, ffmpeg and CustomTkinter.\n\n"
    "Please respect copyright. MediaForge cannot and will not download "
    "DRM-protected or paid content — only material you are allowed to access."
)


class AboutPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        col = t.center_column(self)
        r = 0

        # Logo (if available) — one of only two places the logo appears.
        self._logo_img = None
        lp = logo_path()
        if lp is not None:
            try:
                from PIL import Image
                self._logo_img = ctk.CTkImage(Image.open(lp), size=(112, 112))
                ctk.CTkLabel(col, image=self._logo_img, text=""
                             ).grid(row=r, column=0, sticky="w", pady=(28, 6)); r += 1
            except Exception:
                self._logo_img = None

        ctk.CTkLabel(col, text="MediaForge", font=t.font(28, "bold"), text_color=t.TEXT
                     ).grid(row=r, column=0, sticky="w", pady=(8, 0)); r += 1
        ctk.CTkLabel(col, text=f"Version {__version__}", font=t.font(13),
                     text_color=t.TEXT_MUTED).grid(row=r, column=0, sticky="w",
                                                   pady=(0, 18)); r += 1

        card = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                            border_width=1, border_color=t.BORDER)
        card.grid(row=r, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=ABOUT_TEXT, justify="left", anchor="w",
                     wraplength=620, font=t.font(13), text_color=t.TEXT
                     ).grid(row=0, column=0, sticky="w", padx=22, pady=22)
