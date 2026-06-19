"""Settings page: defaults persisted to the app-data settings file."""
from __future__ import annotations

import tkinter.filedialog as fd
from pathlib import Path

import customtkinter as ctk

from ...core import settings as settings_store

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

        ctk.CTkLabel(self, text="Settings",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 12))

        body = ctk.CTkFrame(self, corner_radius=10)
        body.grid(row=1, column=0, sticky="ew", padx=24, pady=4)
        body.grid_columnconfigure(1, weight=1)
        r = 0

        # Download folder
        ctk.CTkLabel(body, text="Default folder").grid(row=r, column=0, sticky="w", padx=16, pady=(16, 6))
        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        ctk.CTkEntry(body, textvariable=self.folder_var, height=36
                     ).grid(row=r, column=1, sticky="ew", padx=(0, 8), pady=(16, 6))
        ctk.CTkButton(body, text="Browse", width=80, command=self._browse
                      ).grid(row=r, column=2, padx=(0, 16), pady=(16, 6))
        r += 1

        # Appearance
        ctk.CTkLabel(body, text="Appearance").grid(row=r, column=0, sticky="w", padx=16, pady=6)
        self.appearance_var = ctk.StringVar(value=self.s.get("appearance", "Dark"))
        ctk.CTkOptionMenu(body, values=["Dark", "Light", "System"],
                          variable=self.appearance_var, command=self._on_appearance
                          ).grid(row=r, column=1, sticky="w", pady=6)
        r += 1

        # Default quality
        ctk.CTkLabel(body, text="Default quality").grid(row=r, column=0, sticky="w", padx=16, pady=6)
        self.quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best"))
        ctk.CTkOptionMenu(body, values=["Best", "1080p", "720p", "480p", "360p"],
                          variable=self.quality_var
                          ).grid(row=r, column=1, sticky="w", pady=6)
        r += 1

        # Naming
        ctk.CTkLabel(body, text="File naming").grid(row=r, column=0, sticky="w", padx=16, pady=6)
        self.naming_var = ctk.StringVar(
            value=NAMING_LABELS.get(self.s.get("naming", "title"), "Video title"))
        ctk.CTkOptionMenu(body, values=list(NAMING_LABELS.values()),
                          variable=self.naming_var
                          ).grid(row=r, column=1, sticky="w", pady=6)
        r += 1

        # Metadata
        self.meta_var = ctk.BooleanVar(value=self.s.get("embed_metadata", True))
        ctk.CTkCheckBox(body, text="Embed metadata into video files",
                        variable=self.meta_var
                        ).grid(row=r, column=0, columnspan=2, sticky="w", padx=16, pady=(6, 16))
        r += 1

        ctk.CTkButton(self, text="💾 Save settings", height=40, width=160,
                      font=ctk.CTkFont(size=14, weight="bold"), command=self._save
                      ).grid(row=2, column=0, sticky="w", padx=24, pady=16)
        self.saved_lbl = ctk.CTkLabel(self, text="", text_color="#16a34a")
        self.saved_lbl.grid(row=2, column=0, sticky="w", padx=200, pady=16)

    def _browse(self):
        d = fd.askdirectory(initialdir=self.folder_var.get() or str(Path.home()))
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
