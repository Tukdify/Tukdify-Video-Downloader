"""Main application window: sidebar navigation + stacked pages."""
from __future__ import annotations

import customtkinter as ctk

from .. import __app_name__, __version__
from ..config import logo_path
from ..core import settings as settings_store
from . import theme as t
from .pages.downloads_page import DownloadsPage
from .pages.history_page import HistoryPage
from .pages.settings_page import SettingsPage
from .pages.about_page import AboutPage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = settings_store.load()

        ctk.set_appearance_mode(self.settings.get("appearance", "Dark"))
        ctk.set_default_color_theme("blue")

        self.title(f"{__app_name__} {__version__}")
        self.geometry("1140x740")
        self.minsize(980, 620)
        self.configure(fg_color=t.APP_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages()
        self.select_page("Downloads")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # -- sidebar ------------------------------------------------------------
    def _build_sidebar(self):
        bar = ctk.CTkFrame(self, width=t.SIDEBAR_W, corner_radius=0, fg_color=t.SIDEBAR_BG)
        bar.grid(row=0, column=0, sticky="nsw")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_rowconfigure(7, weight=1)

        # Brand: small logo + wordmark (the logo lives only here and on About).
        brand = ctk.CTkFrame(bar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=20, pady=(26, 2), sticky="w")
        self._logo_img = None
        lp = logo_path()
        if lp is not None:
            try:
                from PIL import Image
                self._logo_img = ctk.CTkImage(Image.open(lp), size=(26, 26))
                ctk.CTkLabel(brand, image=self._logo_img, text="").pack(side="left", padx=(0, 10))
            except Exception:
                self._logo_img = None
        ctk.CTkLabel(brand, text="MediaForge", font=t.font(19, "bold"),
                     text_color=t.TEXT).pack(side="left")

        ctk.CTkLabel(bar, text="Download anything.", font=t.font(11),
                     text_color=t.TEXT_FAINT).grid(row=1, column=0, padx=22, pady=(0, 26),
                                                   sticky="w")

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        items = [("Downloads", "  Downloads", "⬇"), ("History", "  History", "🕘"),
                 ("Settings", "  Settings", "⚙"), ("About", "  About", "ℹ")]
        for i, (key, label, icon) in enumerate(items, start=2):
            btn = ctk.CTkButton(
                bar, text=f"{icon}{label}", anchor="w", height=40, corner_radius=9,
                fg_color="transparent", text_color=t.TEXT_MUTED,
                hover_color=t.CARD_HOVER, font=t.font(14),
                command=lambda k=key: self.select_page(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=3, sticky="ew")
            self._nav_buttons[key] = btn

        ctk.CTkLabel(bar, text=f"v{__version__}", font=t.font(11),
                     text_color=t.TEXT_FAINT).grid(row=8, column=0, padx=22, pady=18,
                                                   sticky="sw")

    # -- pages --------------------------------------------------------------
    def _build_pages(self):
        container = ctk.CTkFrame(self, corner_radius=0, fg_color=t.APP_BG)
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
            active = k == key
            btn.configure(
                fg_color=t.ACCENT_SOFT if active else "transparent",
                text_color=t.ACCENT if active else t.TEXT_MUTED,
                hover_color=t.ACCENT_SOFT if active else t.CARD_HOVER,
                font=t.font(14, "bold" if active else "normal"),
            )
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
