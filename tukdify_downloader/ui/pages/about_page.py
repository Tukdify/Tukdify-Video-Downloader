"""About page: Tukdify brand identity, version, ecosystem suite, and diagnostics."""
from __future__ import annotations

import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ... import __app_name__, __version__
from ...config import logo_path
from .. import theme as t
from ..dialogs import FollowDialog, SupportDialog

ABOUT_TEXT = (
    "Tukdify Video Downloader is a high-performance desktop media utility "
    "engineered for creators, video editors, and archivists.\n\n"
    "• Fast & Private: Zero telemetry, no ads, no accounts required. All processing runs locally.\n"
    "• High Resolution: Supports 4K (2160p), 1440p, 1080p Full HD, and 320kbps MP3 Audio.\n"
    "• Multi-Platform: Universal compatibility with YouTube, TikTok, Instagram, X, Twitch, and 1000+ sites.\n"
    "• Non-Destructive: Smart stream merging and chapter metadata embedding via FFmpeg.\n\n"
    "Part of the Tukdify Creator Suite:\n"
    "  ‣ Tukdify Clips — AI Long-Form to Viral Shorts Generator\n"
    "  ‣ Tukdify Video Downloader — Fast Universal Media Ingestion\n"
    "  ‣ Tukdify Multicompressor — GPU-Accelerated Batch Compressor"
)


class AboutPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll_host = ctk.CTkFrame(self, fg_color="transparent")
        scroll_host.grid(row=0, column=0, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        col = t.center_column(self.scroll, gutter=8)

        # Brand Hero (Metal Silver Falcon)
        self._logo_img = None
        lp = logo_path()
        if lp is not None:
            try:
                self._logo_img = ctk.CTkImage(Image.open(lp), size=(88, 88))
                ctk.CTkLabel(col, image=self._logo_img, text="").pack(anchor="w", pady=(24, 6))
            except Exception:
                self._logo_img = None

        ctk.CTkLabel(col, text="Tukdify Video Downloader", font=t.font(24, "bold"),
                     text_color=t.TEXT).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(col, text=f"Version {__version__} · Tukdify Desktop Ecosystem", font=t.font(13),
                     text_color=t.ACCENT).pack(anchor="w", pady=(2, 16))

        # Main Info Card
        card = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                            border_width=1, border_color=t.BORDER)
        card.pack(fill="x", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=ABOUT_TEXT, justify="left", anchor="w",
                     wraplength=620, font=t.font(13), text_color=t.TEXT
                     ).pack(anchor="w", padx=22, pady=20)

        # Quick Actions Row
        actions_card = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                                   border_width=1, border_color=t.BORDER)
        actions_card.pack(fill="x", pady=(0, 24))
        actions_card.grid_columnconfigure((0, 1, 2), weight=1)

        t.primary_button(actions_card, text="❤️  Support Project", height=38,
                         command=lambda: SupportDialog(self)).grid(row=0, column=0, padx=12, pady=14, sticky="ew")
        t.cyan_button(actions_card, text="🌐  Connect & Follow", height=38,
                      command=lambda: FollowDialog(self)).grid(row=0, column=1, padx=12, pady=14, sticky="ew")
        t.ghost_button(actions_card, text="⭐  GitHub Repo", height=38,
                       command=lambda: webbrowser.open("https://github.com/Tukdify/Tukdify-Video-Downloader")
                       ).grid(row=0, column=2, padx=12, pady=14, sticky="ew")

