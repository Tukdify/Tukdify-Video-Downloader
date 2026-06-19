"""Main application window: sidebar navigation + stacked pages."""
from __future__ import annotations

import customtkinter as ctk

from .. import __app_name__, __version__
from ..core import settings as settings_store
from .pages.downloads_page import DownloadsPage
from .pages.history_page import HistoryPage
from .pages.settings_page import SettingsPage
from .pages.about_page import AboutPage

ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
SIDEBAR_BG = ("#e5e7eb", "#16181d")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = settings_store.load()

        ctk.set_appearance_mode(self.settings.get("appearance", "Dark"))
        ctk.set_default_color_theme("blue")

        self.title(f"{__app_name__} {__version__}")
        self.geometry("980x660")
        self.minsize(840, 560)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages()
        self.select_page("Downloads")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # -- sidebar ------------------------------------------------------------
    def _build_sidebar(self):
        bar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=SIDEBAR_BG)
        bar.grid(row=0, column=0, sticky="nsw")
        bar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            bar, text="⚒  MediaForge",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")
        ctk.CTkLabel(
            bar, text="Download anything.",
            font=ctk.CTkFont(size=11), text_color=("gray45", "gray60"),
        ).grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        items = [("Downloads", "⬇  Downloads"), ("History", "🕘  History"),
                 ("Settings", "⚙  Settings"), ("About", "ℹ  About")]
        for i, (key, label) in enumerate(items, start=2):
            btn = ctk.CTkButton(
                bar, text=label, anchor="w", height=42, corner_radius=8,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("#d1d5db", "#23262e"),
                font=ctk.CTkFont(size=14),
                command=lambda k=key: self.select_page(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=4, sticky="ew")
            self._nav_buttons[key] = btn

        ctk.CTkLabel(
            bar, text=f"v{__version__}",
            font=ctk.CTkFont(size=11), text_color=("gray50", "gray50"),
        ).grid(row=7, column=0, padx=20, pady=16, sticky="sw")

    # -- pages --------------------------------------------------------------
    def _build_pages(self):
        container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages: dict[str, ctk.CTkFrame] = {
            "Downloads": DownloadsPage(container, self),
            "History": HistoryPage(container, self),
            "Settings": SettingsPage(container, self),
            "About": AboutPage(container, self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def select_page(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.configure(fg_color=ACCENT if k == key else "transparent",
                          text_color=("white" if k == key else ("gray10", "gray90")))
        page = self.pages[key]
        if hasattr(page, "on_show"):
            page.on_show()
        page.tkraise()

    # -- lifecycle ----------------------------------------------------------
    def apply_appearance(self, mode: str):
        ctk.set_appearance_mode(mode)

    def _on_close(self):
        try:
            self.pages["Downloads"].manager.shutdown()
        except Exception:
            pass
        self.destroy()


def run():
    App().mainloop()
