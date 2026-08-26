"""Main application window: top global header navigation + spacious content canvas."""
from __future__ import annotations

import sys
import customtkinter as ctk
from PIL import Image

from .. import __app_name__, __version__
from ..config import app_icon_path, falcon_mark_path, logo_path
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
        self.geometry("1120x760")
        self.minsize(960, 640)
        self.configure(fg_color=t.APP_BG)

        self._apply_window_icon()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top Global Header
        self.grid_rowconfigure(1, weight=1)  # Full Content Area

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._build_header()
        self._build_pages()
        self.select_page("Downloads")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_window_icon(self):
        """Apply the canonical Tukdify Falcon icon to the window titlebar and OS taskbar."""
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Tukdify.VideoDownloader")
            except Exception:
                pass

        ico = app_icon_path()
        if ico and ico.exists():
            try:
                self.iconbitmap(default=str(ico))
            except Exception:
                try:
                    self.iconbitmap(str(ico))
                except Exception:
                    pass

        # Also set iconphoto using PhotoImage for Linux/macOS and fallback
        try:
            from PIL import ImageTk
            png_path = logo_path() or falcon_mark_path()
            if png_path and png_path.exists():
                self._window_photo = ImageTk.PhotoImage(file=str(png_path))
                self.wm_iconphoto(True, self._window_photo)
        except Exception:
            pass

    # -- top global header (Tukdify Clips signature architecture) -----------
    def _build_header(self):
        header_bar = ctk.CTkFrame(
            self, height=56, corner_radius=0, fg_color=t.SIDEBAR_BG,
            border_width=0,
        )
        header_bar.grid(row=0, column=0, sticky="ew")
        header_bar.grid_propagate(False)
        header_bar.grid_columnconfigure(1, weight=1)

        # 1. Left: Product Branding (Falcon + Tukdify Downloader · by Tukdify)
        brand = ctk.CTkFrame(header_bar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=(18, 12), pady=8, sticky="w")

        self._logo_img = None
        fp = falcon_mark_path()
        if fp is not None:
            try:
                self._logo_img = ctk.CTkImage(Image.open(fp), size=(22, 22))
                ctk.CTkLabel(brand, image=self._logo_img, text="").pack(side="left", padx=(0, 8))
            except Exception:
                self._logo_img = None

        ctk.CTkLabel(brand, text="Tukdify Downloader", font=t.font(14, "bold"),
                     text_color=t.TEXT).pack(side="left")
        ctk.CTkLabel(brand, text=" · ", font=t.font(13, "bold"),
                     text_color=t.TEXT_FAINT).pack(side="left")
        ctk.CTkLabel(brand, text="by Tukdify", font=t.font(11),
                     text_color=t.TEXT_MUTED).pack(side="left")

        # 2. Center: Segmented Navigation Pills
        nav_container = ctk.CTkFrame(header_bar, fg_color="transparent")
        nav_container.grid(row=0, column=1, pady=8, sticky="n")

        nav_pill_box = ctk.CTkFrame(
            nav_container, fg_color=t.INPUT_BG, corner_radius=8,
            border_width=1, border_color=t.BORDER,
        )
        nav_pill_box.pack(side="top")

        page_items = [
            ("Downloads", "Downloads", "⬇ "),
            ("History", "History", "🕘 "),
            ("Settings", "Settings", "⚙ "),
            ("About", "About", "ℹ "),
        ]

        for key, label, icon in page_items:
            btn = ctk.CTkButton(
                nav_pill_box, text=f"{icon}{label}", height=32, width=105,
                corner_radius=6, fg_color="transparent", text_color=t.TEXT_MUTED,
                hover_color=t.CARD_HOVER, font=t.font(12, "bold"),
                command=lambda k=key: self.select_page(k),
            )
            btn.pack(side="left", padx=2, pady=2)
            self._nav_buttons[key] = btn

        # 3. Right: Utility Actions (Follow & Support)
        actions = ctk.CTkFrame(header_bar, fg_color="transparent")
        actions.grid(row=0, column=2, padx=(12, 18), pady=8, sticky="e")

        self.follow_btn = ctk.CTkButton(
            actions, text="🌐  Follow", width=86, height=32, corner_radius=8,
            fg_color=t.INPUT_BG, border_width=1, border_color=t.BORDER,
            text_color=t.TEXT, hover_color=t.CARD_HOVER, font=t.font(12, "bold"),
            command=lambda: FollowDialog(self),
        )
        self.follow_btn.pack(side="left", padx=(0, 8))

        self.support_btn = ctk.CTkButton(
            actions, text="❤️  Support", width=92, height=32, corner_radius=8,
            fg_color=t.ACCENT_SOFT, border_width=1, border_color=t.BORDER,
            text_color=t.TEXT, hover_color=t.ACCENT, font=t.font(12, "bold"),
            command=lambda: SupportDialog(self),
        )
        self.support_btn.pack(side="left")

        # Bottom subtle separator line
        sep = ctk.CTkFrame(self, height=1, fg_color=t.BORDER, corner_radius=0)
        sep.grid(row=0, column=0, sticky="sew")

    # -- pages --------------------------------------------------------------
    def _build_pages(self):
        container = ctk.CTkFrame(self, corner_radius=0, fg_color=t.APP_BG)
        container.grid(row=1, column=0, sticky="nsew")
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
                fg_color=t.ACCENT if active else "transparent",
                text_color="#ffffff" if active else t.TEXT_MUTED,
                hover_color=t.ACCENT_HOVER if active else t.CARD_HOVER,
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
