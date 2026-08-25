"""Settings page: structured cards for appearance, download defaults, and media rules."""
from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from ...config import app_data_dir, find_ffmpeg
from ...core import settings as settings_store
from .. import theme as t
from ..dialogs import Tooltip, choose_directory, short_path

NAMING_OPTIONS = {
    "title": "Title only (e.g. Video.mp4)",
    "uploader_title": "Uploader - Title (e.g. Channel - Video.mp4)",
    "title_quality": "Title with Quality tag (e.g. Video [1080p].mp4)",
}
NAMING_REVERSE = {v: k for k, v in NAMING_OPTIONS.items()}


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.s = app.settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        head_host = ctk.CTkFrame(self, fg_color="transparent")
        head_host.grid(row=0, column=0, sticky="ew")
        head = t.center_column(head_host)
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(head, text="Settings", font=t.font(20, "bold"), text_color=t.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(22, 10))

        self.save_status_lbl = ctk.CTkLabel(head, text="", font=t.font(12, "bold"), text_color=t.OK)
        self.save_status_lbl.grid(row=0, column=1, sticky="e", pady=(22, 10))

        scroll_host = ctk.CTkFrame(self, fg_color="transparent")
        scroll_host.grid(row=1, column=0, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        col = t.center_column(self.scroll, gutter=8)

        # ------------------------------------------------------------------
        # CARD 1: General & Appearance
        # ------------------------------------------------------------------
        ctk.CTkLabel(col, text="GENERAL & APPEARANCE", font=t.font(11, "bold"),
                     text_color=t.ACCENT).pack(anchor="w", padx=4, pady=(10, 6))

        card1 = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=12,
                             border_width=1, border_color=t.BORDER)
        card1.pack(fill="x", pady=(0, 14))
        card1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card1, text="Theme Mode", font=t.font(13, "bold"),
                     text_color=t.TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=12)
        self.appearance_var = ctk.StringVar(value=self.s.get("appearance", "Dark"))
        m_app = ctk.CTkSegmentedButton(card1, values=["Dark", "Light", "System"],
                                       variable=self.appearance_var, height=32,
                                       command=self._on_appearance_change)
        t.style_segmented(m_app)
        m_app.grid(row=0, column=1, sticky="e", padx=16, pady=12)

        ctk.CTkLabel(card1, text="Max Concurrent Downloads", font=t.font(13, "bold"),
                     text_color=t.TEXT).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        self.concurrency_var = ctk.StringVar(value=str(self.s.get("concurrency", 2)))
        m_conc = ctk.CTkOptionMenu(card1, values=["1", "2", "3", "4"],
                                   variable=self.concurrency_var, width=100, height=32,
                                   command=self._auto_save)
        t.style_optionmenu(m_conc)
        m_conc.grid(row=1, column=1, sticky="e", padx=16, pady=(0, 12))

        # ------------------------------------------------------------------
        # CARD 2: Download Defaults
        # ------------------------------------------------------------------
        ctk.CTkLabel(col, text="DEFAULT DOWNLOAD CONFIGURATION", font=t.font(11, "bold"),
                     text_color=t.ACCENT).pack(anchor="w", padx=4, pady=(10, 6))

        card2 = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=12,
                             border_width=1, border_color=t.BORDER)
        card2.pack(fill="x", pady=(0, 14))
        card2.grid_columnconfigure(1, weight=1)

        # Folder row
        ctk.CTkLabel(card2, text="Default Save Folder", font=t.font(13, "bold"),
                     text_color=t.TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 4))
        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        self.folder_lbl = ctk.CTkLabel(card2, text=short_path(self.folder_var.get()),
                                       font=t.mono_font(11), text_color=t.TEXT_MUTED, anchor="w")
        self.folder_lbl.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))
        Tooltip(self.folder_lbl, lambda: self.folder_var.get())

        t.ghost_button(card2, text="Change…", width=84, height=30,
                       command=self._browse_folder).grid(row=0, column=1, rowspan=2, sticky="e", padx=16)

        # Quality default
        ctk.CTkLabel(card2, text="Default Quality Preset", font=t.font(13, "bold"),
                     text_color=t.TEXT).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 14))
        self.quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best (4K/1440p)"))
        m_qual = ctk.CTkOptionMenu(card2, values=["Best (4K/1440p)", "1080p", "720p", "480p", "360p"],
                                   variable=self.quality_var, width=160, height=32,
                                   command=self._auto_save)
        t.style_optionmenu(m_qual)
        m_qual.grid(row=2, column=1, sticky="e", padx=16, pady=(0, 14))

        # Naming format
        ctk.CTkLabel(card2, text="File Naming Template", font=t.font(13, "bold"),
                     text_color=t.TEXT).grid(row=3, column=0, sticky="w", padx=16, pady=(0, 14))
        self.naming_var = ctk.StringVar(value=NAMING_OPTIONS.get(self.s.get("naming", "title")))
        m_name = ctk.CTkOptionMenu(card2, values=list(NAMING_OPTIONS.values()),
                                   variable=self.naming_var, width=220, height=32,
                                   command=self._auto_save)
        t.style_optionmenu(m_name)
        m_name.grid(row=3, column=1, sticky="e", padx=16, pady=(0, 14))

        # ------------------------------------------------------------------
        # CARD 3: Metadata & Subtitles
        # ------------------------------------------------------------------
        ctk.CTkLabel(col, text="MEDIA METADATA & STREAM OPTIONS", font=t.font(11, "bold"),
                     text_color=t.ACCENT).pack(anchor="w", padx=4, pady=(10, 6))

        card3 = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=12,
                             border_width=1, border_color=t.BORDER)
        card3.pack(fill="x", pady=(0, 14))
        card3.grid_columnconfigure(0, weight=1)

        self.meta_var = ctk.BooleanVar(value=self.s.get("embed_metadata", True))
        c1 = ctk.CTkCheckBox(card3, text="Embed complete metadata & chapters with FFmpeg",
                             variable=self.meta_var, font=t.font(12),
                             fg_color=t.ACCENT, command=self._auto_save)
        c1.pack(anchor="w", padx=16, pady=(12, 6))

        self.thumb_var = ctk.BooleanVar(value=self.s.get("write_thumbnail", False))
        c2 = ctk.CTkCheckBox(card3, text="Save cover art thumbnail image alongside media",
                             variable=self.thumb_var, font=t.font(12),
                             fg_color=t.ACCENT, command=self._auto_save)
        c2.pack(anchor="w", padx=16, pady=6)

        self.subs_var = ctk.BooleanVar(value=self.s.get("write_subtitles", False))
        c3 = ctk.CTkCheckBox(card3, text="Download subtitles and auto-captions by default",
                             variable=self.subs_var, font=t.font(12),
                             fg_color=t.ACCENT, command=self._auto_save)
        c3.pack(anchor="w", padx=16, pady=(6, 14))

        # ------------------------------------------------------------------
        # CARD 4: Diagnostics
        # ------------------------------------------------------------------
        ctk.CTkLabel(col, text="SYSTEM & ENGINE DIAGNOSTICS", font=t.font(11, "bold"),
                     text_color=t.TEXT_MUTED).pack(anchor="w", padx=4, pady=(10, 6))

        card4 = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=12,
                             border_width=1, border_color=t.BORDER)
        card4.pack(fill="x", pady=(0, 24))
        card4.grid_columnconfigure(1, weight=1)

        ffmpeg_stat = "✓ Detected & Active" if find_ffmpeg() else "⚡ System PATH / Bundled"
        ctk.CTkLabel(card4, text="FFmpeg Status", font=t.font(12, "bold"),
                     text_color=t.TEXT).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))
        ctk.CTkLabel(card4, text=ffmpeg_stat, font=t.mono_font(11),
                     text_color=t.OK).grid(row=0, column=1, sticky="e", padx=16, pady=(12, 6))

        ctk.CTkLabel(card4, text="Data Storage Path", font=t.font(12, "bold"),
                     text_color=t.TEXT).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        ctk.CTkLabel(card4, text=short_path(str(app_data_dir()), parts=3), font=t.mono_font(11),
                     text_color=t.TEXT_MUTED).grid(row=1, column=1, sticky="e", padx=16, pady=(0, 12))

    def _browse_folder(self):
        d = choose_directory(self.folder_var.get() or str(Path.home()))
        if d:
            self.folder_var.set(d)
            self.folder_lbl.configure(text=short_path(d))
            self._auto_save()

    def _on_appearance_change(self, val: str):
        self.app.apply_appearance(val)
        self._auto_save()

    def _auto_save(self, *_):
        self.s.update({
            "download_dir": self.folder_var.get(),
            "appearance": self.appearance_var.get(),
            "concurrency": int(self.concurrency_var.get() or "2"),
            "default_quality": self.quality_var.get(),
            "naming": NAMING_REVERSE.get(self.naming_var.get(), "title"),
            "embed_metadata": self.meta_var.get(),
            "write_thumbnail": self.thumb_var.get(),
            "write_subtitles": self.subs_var.get(),
        })
        settings_store.save(self.s)
        self.save_status_lbl.configure(text="Saved ✓")
        self.after(1600, lambda: self.save_status_lbl.configure(text=""))

