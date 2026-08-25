"""History page: searchable, platform-filterable records with safe file reveal."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from ...core import history as history_store
from .. import theme as t
from ..dialogs import reveal_in_file_manager

FILTER_PLATFORMS = ["All", "YouTube", "TikTok", "Instagram", "X (Twitter)", "Facebook", "Other"]


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._entries: list[dict] = []
        self._search_query: str = ""
        self._active_platform: str = "All"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters()
        self._build_list()

    def _build_header(self):
        head_host = ctk.CTkFrame(self, fg_color="transparent")
        head_host.grid(row=0, column=0, sticky="ew")
        head = t.center_column(head_host)
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(head, text="Download History", font=t.font(20, "bold"), text_color=t.TEXT
                     ).grid(row=0, column=0, sticky="w", pady=(22, 10))

        t.ghost_button(head, text="Clear All", width=84, height=30, hover_color=t.ERR,
                       command=self._clear).grid(row=0, column=1, sticky="e", pady=(22, 10))

    def _build_filters(self):
        filter_host = ctk.CTkFrame(self, fg_color="transparent")
        filter_host.grid(row=1, column=0, sticky="ew")
        col = t.center_column(filter_host)
        col.grid_columnconfigure(0, weight=1)

        # Search Bar
        search_box = ctk.CTkFrame(col, fg_color=t.INPUT_BG, corner_radius=10,
                                  border_width=1, border_color=t.BORDER)
        search_box.pack(fill="x", pady=(0, 10))
        search_box.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_box, text="🔍", font=t.font(13), width=32).grid(row=0, column=0, padx=(8, 0))
        self.search_entry = ctk.CTkEntry(search_box, placeholder_text="Search history by title, URL or platform…",
                                         border_width=0, fg_color="transparent", font=t.font(13))
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Platform Filter Pills
        self.filter_var = ctk.StringVar(value="All")
        self.filter_pills = ctk.CTkSegmentedButton(
            col, values=FILTER_PLATFORMS, height=32, variable=self.filter_var,
            font=t.font(11, "bold"), command=self._on_filter_platform,
        )
        t.style_segmented(self.filter_pills)
        self.filter_pills.pack(fill="x", pady=(0, 12))

    def _build_list(self):
        scroll_host = ctk.CTkFrame(self, fg_color="transparent")
        scroll_host.grid(row=2, column=0, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self.list = t.center_column(self.scroll, gutter=8)

    def on_show(self):
        self._entries = history_store.load()
        self._render_filtered()

    def _on_search(self, _evt=None):
        self._search_query = self.search_entry.get().strip().lower()
        self._render_filtered()

    def _on_filter_platform(self, val: str):
        self._active_platform = val
        self._render_filtered()

    def _render_filtered(self):
        for w in self.list.winfo_children():
            w.destroy()

        filtered = []
        for e in self._entries:
            title = (e.get("title") or "").lower()
            url = (e.get("url") or "").lower()
            platform = e.get("platform") or "Unknown"

            if self._search_query and (self._search_query not in title and self._search_query not in url):
                continue
            if self._active_platform != "All":
                if self._active_platform == "Other":
                    if platform in ["YouTube", "TikTok", "Instagram", "X (Twitter)", "Facebook"]:
                        continue
                elif self._active_platform not in platform:
                    continue
            filtered.append(e)

        if not filtered:
            empty_msg = "No matching downloads found." if self._entries else "No downloads in history yet."
            ctk.CTkLabel(self.list, text=empty_msg, font=t.font(13),
                         text_color=t.TEXT_FAINT).grid(row=0, column=0, pady=40)
            return

        for i, e in enumerate(filtered):
            self._row(i, e)

    def _row(self, i: int, e: dict):
        card = ctk.CTkFrame(self.list, fg_color=t.CARD_BG, corner_radius=12,
                            border_width=1, border_color=t.BORDER)
        card.grid(row=i, column=0, sticky="ew", pady=4)
        card.grid_columnconfigure(0, weight=1)

        title = e.get("title") or e.get("url", "Untitled Download")
        ctk.CTkLabel(card, text=title, anchor="w", text_color=t.TEXT,
                     font=t.font(13, "bold"), wraplength=460, justify="left"
                     ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))

        # Format meta text with date
        when_str = e.get("when", "")
        formatted_date = when_str.replace("T", " ") if when_str else ""
        size_part = f" · {e.get('size')}" if e.get("size") else ""
        meta = f"{e.get('platform','Media')} · {e.get('mode','Video')} {e.get('quality','')}{size_part} · {formatted_date}"
        
        ctk.CTkLabel(card, text=meta, anchor="w", text_color=t.TEXT_MUTED,
                     font=t.font(11)).grid(row=1, column=0, sticky="w", padx=16, pady=(2, 12))

        # Action Buttons
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.grid(row=0, column=1, rowspan=2, padx=14, sticky="e")

        t.ghost_button(btn_box, text="📁 Reveal", width=74, height=28,
                       command=lambda p=e.get("filepath", ""): reveal_in_file_manager(p)).pack(side="left", padx=3)

        del_btn = ctk.CTkButton(btn_box, text="✕", width=28, height=28, fg_color="transparent",
                                hover_color=t.ERR, text_color=t.TEXT_MUTED, font=t.font(11),
                                command=lambda item=e: self._delete_item(item))
        del_btn.pack(side="left", padx=3)

    def _delete_item(self, item: dict):
        history_store.remove(item.get("filepath") or item.get("url", ""))
        self.on_show()

    def _clear(self):
        history_store.clear()
        self.on_show()

