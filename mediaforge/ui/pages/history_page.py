"""History page: a scrollable list of past downloads."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import customtkinter as ctk

from ...core import history as history_store
from .. import theme as t


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        head_host = ctk.CTkFrame(self, fg_color="transparent")
        head_host.grid(row=0, column=0, sticky="ew")
        head = t.center_column(head_host)
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text="History", font=t.font(22, "bold"), text_color=t.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(26, 16))
        t.ghost_button(head, text="Clear", width=88, height=32, hover_color=t.ERR,
                       command=self._clear).grid(row=0, column=1, sticky="e", pady=(26, 16))

        scroll_host = ctk.CTkFrame(self, fg_color="transparent")
        scroll_host.grid(row=1, column=0, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self.list = t.center_column(self.scroll, gutter=8)

    def on_show(self):
        for w in self.list.winfo_children():
            w.destroy()
        entries = history_store.load()
        if not entries:
            ctk.CTkLabel(self.list, text="Nothing downloaded yet.",
                         font=t.font(13), text_color=t.TEXT_FAINT
                         ).grid(row=0, column=0, pady=40)
            return
        for i, e in enumerate(entries):
            self._row(i, e)

    def _row(self, i: int, e: dict):
        card = ctk.CTkFrame(self.list, fg_color=t.CARD_BG, corner_radius=12,
                            border_width=1, border_color=t.BORDER)
        card.grid(row=i, column=0, sticky="ew", pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=e.get("title", "?"), anchor="w", text_color=t.TEXT,
                     font=t.font(13, "bold"), wraplength=470, justify="left"
                     ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        meta = f"{e.get('platform','')} · {e.get('mode','')} · {e.get('when','')}"
        ctk.CTkLabel(card, text=meta, anchor="w", text_color=t.TEXT_MUTED,
                     font=t.font(11)).grid(row=1, column=0, sticky="w", padx=14, pady=(2, 12))
        t.ghost_button(card, text="Open", width=72, height=30,
                       command=lambda p=e.get("filepath", ""): self._open(p)
                       ).grid(row=0, column=1, rowspan=2, padx=14)

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
