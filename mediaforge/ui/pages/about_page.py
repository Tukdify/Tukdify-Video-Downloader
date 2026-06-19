"""About page: version, credits, and an honest scope note."""
from __future__ import annotations

import customtkinter as ctk

from ... import __version__

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

        ctk.CTkLabel(self, text="⚒  MediaForge",
                     font=ctk.CTkFont(size=28, weight="bold")
                     ).grid(row=0, column=0, sticky="w", padx=24, pady=(28, 0))
        ctk.CTkLabel(self, text=f"Version {__version__}",
                     text_color=("gray40", "gray60")
                     ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 16))

        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=4)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=ABOUT_TEXT, justify="left", anchor="w",
                     wraplength=640, font=ctk.CTkFont(size=13)
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=20)
