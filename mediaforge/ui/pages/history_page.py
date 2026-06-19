"""History page: a scrollable list of past downloads."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import customtkinter as ctk

from ...core import history as history_store


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="History",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="Clear", width=90, fg_color="gray30",
                      hover_color="#b91c1c", command=self._clear
                      ).grid(row=0, column=1, sticky="e")

        self.list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self.list.grid_columnconfigure(0, weight=1)

    def on_show(self):
        for w in self.list.winfo_children():
            w.destroy()
        entries = history_store.load()
        if not entries:
            ctk.CTkLabel(self.list, text="Nothing downloaded yet.",
                         text_color=("gray50", "gray50")).grid(row=0, column=0, pady=24)
            return
        for i, e in enumerate(entries):
            self._row(i, e)

    def _row(self, i: int, e: dict):
        card = ctk.CTkFrame(self.list, corner_radius=8)
        card.grid(row=i, column=0, sticky="ew", pady=4, padx=4)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=e.get("title", "?"), anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     wraplength=560, justify="left"
                     ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
        meta = f"{e.get('platform','')} · {e.get('mode','')} · {e.get('when','')}"
        ctk.CTkLabel(card, text=meta, anchor="w", text_color=("gray40", "gray60"),
                     font=ctk.CTkFont(size=11)
                     ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))
        ctk.CTkButton(card, text="Open", width=70, fg_color="gray30",
                      hover_color="gray25",
                      command=lambda p=e.get("filepath", ""): self._open(p)
                      ).grid(row=0, column=1, rowspan=2, padx=12)

    def _open(self, path: str):
        folder = str(Path(path).parent) if path else str(Path.home())
        try:
            if sys.platform == "win32":
                import os
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception:
            pass

    def _clear(self):
        history_store.clear()
        self.on_show()
