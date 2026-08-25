"""Main application window: sidebar navigation + stacked pages."""
from __future__ import annotations

import customtkinter as ctk
from PIL import Image

from .. import __app_name__, __version__
from ..config import falcon_mark_path
from ..core import settings as settings_store
from . import theme as t
from .dialogs import FollowDialog, SupportDialog
from .pages.about_page import AboutPage
from .pages.downloads_page import DownloadsPage
from .pages.history_page import HistoryPage
from .pages.settings_page import SettingsPage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = settings_store.load()

        ctk.set_appearance_mode(self.settings.get("appearance", "Dark"))
        ctk.set_default_color_theme("blue")

        self.title(f"{__app_name__} v{__version__}")
        self.geometry("1160x760")
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
        bar.grid_rowconfigure(9, weight=1)

        # Brand: Metal Silver Falcon + Tukdify Wordmark
        brand = ctk.CTkFrame(bar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=18, pady=(24, 2), sticky="w")
        self._logo_img = None
        fp = falcon_mark_path()
        if fp is not None:
            try:
                self._logo_img = ctk.CTkImage(Image.open(fp), size=(24, 24))
                ctk.CTkLabel(brand, image=self._logo_img, text="").pack(side="left", padx=(0, 8))
            except Exception:
                self._logo_img = None

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(brand_text, text="Tukdify", font=t.font(17, "bold"),
                     text_color=t.TEXT).pack(anchor="w")

        ctk.CTkLabel(bar, text="Video Downloader", font=t.font(12, "bold"),
                     text_color=t.ACCENT).grid(row=1, column=0, padx=20, pady=(0, 2), sticky="w")
        ctk.CTkLabel(bar, text="Fast · Private · Offline-first", font=t.font(11),
                     text_color=t.TEXT_FAINT).grid(row=2, column=0, padx=20, pady=(0, 22), sticky="w")

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        
        # Primary Pages
        page_items = [
            ("Downloads", "  Downloads", "⬇"),
            ("History", "  History", "🕘"),
            ("Settings", "  Settings", "⚙"),
        ]
        for i, (key, label, icon) in enumerate(page_items, start=3):
            btn = ctk.CTkButton(
                bar, text=f"{icon}{label}", anchor="w", height=38, corner_radius=10,
                fg_color="transparent", text_color=t.TEXT_MUTED,
                hover_color=t.CARD_HOVER, font=t.font(13, "bold"),
                command=lambda k=key: self.select_page(k),
            )
            btn.grid(row=i, column=0, padx=12, pady=3, sticky="ew")
            self._nav_buttons[key] = btn

        # Divider line
        divider = ctk.CTkFrame(bar, height=1, fg_color=t.BORDER)
        divider.grid(row=6, column=0, padx=16, pady=12, sticky="ew")

        # Modals / Secondary Actions (Support & Follow)
        self.support_btn = ctk.CTkButton(
            bar, text="❤️  Support Tukdify", anchor="w", height=36, corner_radius=10,
            fg_color="transparent", text_color=t.TEXT_MUTED,
            hover_color=t.CARD_HOVER, font=t.font(12, "bold"),
            command=lambda: SupportDialog(self),
        )
        self.support_btn.grid(row=7, column=0, padx=12, pady=2, sticky="ew")

        self.follow_btn = ctk.CTkButton(
            bar, text="🌐  Connect / Follow", anchor="w", height=36, corner_radius=10,
            fg_color="transparent", text_color=t.TEXT_MUTED,
            hover_color=t.CARD_HOVER, font=t.font(12, "bold"),
            command=lambda: FollowDialog(self),
        )
        self.follow_btn.grid(row=8, column=0, padx=12, pady=2, sticky="ew")

        # About page
        self.about_btn = ctk.CTkButton(
            bar, text="ℹ  About", anchor="w", height=36, corner_radius=10,
            fg_color="transparent", text_color=t.TEXT_MUTED,
            hover_color=t.CARD_HOVER, font=t.font(12),
            command=lambda: self.select_page("About"),
        )
        self.about_btn.grid(row=9, column=0, padx=12, pady=(2, 0), sticky="new")
        self._nav_buttons["About"] = self.about_btn

        ctk.CTkLabel(bar, text=f"v{__version__} · Tukdify Suite", font=t.font(10),
                     text_color=t.TEXT_FAINT).grid(row=10, column=0, padx=20, pady=14,
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

