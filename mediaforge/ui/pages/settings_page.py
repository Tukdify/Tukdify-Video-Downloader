"""Settings page: defaults persisted to the app-data settings file."""
from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from ...core import settings as settings_store
from .. import theme as t
from ..dialogs import choose_directory

NAMING_LABELS = {
    "title": "Video title",
    "uploader_title": "Uploader - Title",
}
NAMING_REVERSE = {v: k for k, v in NAMING_LABELS.items()}


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.s = app.settings
        self.grid_columnconfigure(0, weight=1)

        col = t.center_column(self)

        ctk.CTkLabel(col, text="Settings", font=t.font(22, "bold"), text_color=t.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(26, 16))

        body = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                            border_width=1, border_color=t.BORDER)
        body.grid(row=1, column=0, sticky="ew")
        body.grid_columnconfigure(1, weight=1)
        r = 0

        # Download folder
        ctk.CTkLabel(body, text="Default folder", text_color=t.TEXT, font=t.font(13)
                     ).grid(row=r, column=0, sticky="w", padx=18, pady=(18, 6))
        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        ctk.CTkEntry(body, textvariable=self.folder_var, height=36, fg_color=t.INPUT_BG,
                     border_color=t.BORDER, text_color=t.TEXT
                     ).grid(row=r, column=1, sticky="ew", padx=(0, 8), pady=(18, 6))
        t.ghost_button(body, text="Browse", width=80, command=self._browse
                       ).grid(row=r, column=2, padx=(0, 18), pady=(18, 6))
        r += 1

        # Appearance
        ctk.CTkLabel(body, text="Appearance", text_color=t.TEXT, font=t.font(13)
                     ).grid(row=r, column=0, sticky="w", padx=18, pady=8)
        self.appearance_var = ctk.StringVar(value=self.s.get("appearance", "Dark"))
        m1 = ctk.CTkOptionMenu(body, values=["Dark", "Light", "System"],
                               variable=self.appearance_var, command=self._on_appearance)
        t.style_optionmenu(m1)
        m1.grid(row=r, column=1, sticky="w", pady=8)
        r += 1

        # Default quality
        ctk.CTkLabel(body, text="Default quality", text_color=t.TEXT, font=t.font(13)
                     ).grid(row=r, column=0, sticky="w", padx=18, pady=8)
        self.quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best"))
        m2 = ctk.CTkOptionMenu(body, values=["Best", "1080p", "720p", "480p", "360p"],
                               variable=self.quality_var)
        t.style_optionmenu(m2)
        m2.grid(row=r, column=1, sticky="w", pady=8)
        r += 1

        # Naming
        ctk.CTkLabel(body, text="File naming", text_color=t.TEXT, font=t.font(13)
                     ).grid(row=r, column=0, sticky="w", padx=18, pady=8)
        self.naming_var = ctk.StringVar(
            value=NAMING_LABELS.get(self.s.get("naming", "title"), "Video title"))
        m3 = ctk.CTkOptionMenu(body, values=list(NAMING_LABELS.values()),
                               variable=self.naming_var)
        t.style_optionmenu(m3)
        m3.grid(row=r, column=1, sticky="w", pady=8)
        r += 1

        # Metadata
        self.meta_var = ctk.BooleanVar(value=self.s.get("embed_metadata", True))
        ctk.CTkCheckBox(body, text="Embed metadata into video files", font=t.font(13),
                        variable=self.meta_var, fg_color=t.ACCENT,
                        hover_color=t.ACCENT_HOVER, text_color=t.TEXT
                        ).grid(row=r, column=0, columnspan=2, sticky="w", padx=18, pady=(8, 18))
        r += 1

        save_row = ctk.CTkFrame(col, fg_color="transparent")
        save_row.grid(row=2, column=0, sticky="w", pady=18)
        t.primary_button(save_row, text="💾  Save settings", height=42, width=170,
                         command=self._save).pack(side="left")
        self.saved_lbl = ctk.CTkLabel(save_row, text="", text_color=t.OK, font=t.font(13))
        self.saved_lbl.pack(side="left", padx=14)

    def _browse(self):
        d = choose_directory(self.folder_var.get() or str(Path.home()))
        if d:
            self.folder_var.set(d)

    def _on_appearance(self, mode: str):
        self.app.apply_appearance(mode)

    def _save(self):
        self.s.update({
            "download_dir": self.folder_var.get(),
            "appearance": self.appearance_var.get(),
            "default_quality": self.quality_var.get(),
            "naming": NAMING_REVERSE.get(self.naming_var.get(), "title"),
            "embed_metadata": self.meta_var.get(),
        })
        settings_store.save(self.s)
        self.saved_lbl.configure(text="Saved ✓")
        self.after(1800, lambda: self.saved_lbl.configure(text=""))
