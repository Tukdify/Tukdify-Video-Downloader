"""UI helpers: directory picker, safe file reveal, SupportDialog, and FollowDialog."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tkinter.filedialog as fd
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ..config import support_asset
from . import theme as t

# Verified Official and Community Channels from Tukdify Ecosystem
OFFICIAL_CHANNELS = [
    ("GitHub", "Tukdify Organization", "https://github.com/Tukdify", "⭐"),
    ("Tukdify Clips", "AI Long-to-Shorts Studio", "https://github.com/Tukdify/Tukdify-clips", "🎬"),
    ("Multicompressor", "Batch Media Optimizer", "https://github.com/Tukdify/Tukdify-Multicompressor", "⚡"),
    ("X (Twitter)", "@tukdify", "https://x.com/tukdify", "𝕏"),
    ("YouTube", "@tukdify", "https://youtube.com/@tukdify?si=v3gFBp33pqPuCdxl", "▶"),
    ("Instagram", "@tukdi_fy", "https://www.instagram.com/tukdi_fy/", "📸"),
    ("Product Hunt", "@tukdify", "https://www.producthunt.com/@tukdify", "🐱"),
    ("Reddit", "u/tukdify", "https://www.reddit.com/user/tukdify/", "👾"),
    ("LinkedIn", "Tukdify Labs", "https://www.linkedin.com/in/tukdify-labs-9b0819425", "💼"),
]

COMMUNITY_CHANNELS = [
    ("Founder GitHub", "Sourabh Jangid", "https://github.com/sourabh-jangid-dev/", "🐙"),
    ("WhatsApp Community", "Creator Hub", "https://chat.whatsapp.com/ElcR6cw483D5G3mEkoygAz", "💬"),
    ("Founder LinkedIn", "Sourabh Jangid", "https://www.linkedin.com/in/sourabh-jangid-88155a327?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app", "👤"),
    ("Founder Instagram", "@sourabh.jangid.dev", "https://www.instagram.com/sourabh.jangid.dev/", "📷"),
]

UPI_ID = "BHARATPE09U9D1V8U2Z32983@yesbankltd"
UPI_RECIPIENT = "Mr. Sourabh Jangid"


def choose_directory(initialdir: str | None = None) -> str | None:
    """Open a folder picker, preferring the native OS dialog."""
    initialdir = initialdir or str(Path.home())

    if sys.platform.startswith("linux"):
        picked = _linux_native_dir(initialdir)
        if picked is not None:
            return picked or None  # "" means user cancelled

    return fd.askdirectory(initialdir=initialdir) or None


def _linux_native_dir(initialdir: str) -> str | None:
    """Return a path from zenity/kdialog, "" if cancelled, or None if neither tool is present."""
    if shutil.which("zenity"):
        cmd = ["zenity", "--file-selection", "--directory",
               "--title=Choose download folder", f"--filename={initialdir}/"]
    elif shutil.which("kdialog"):
        cmd = ["kdialog", "--getexistingdirectory", initialdir]
    else:
        return None
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception:
        return None
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


def short_path(path: str, parts: int = 2) -> str:
    """A compact, human-friendly path showing the last parts."""
    if not path:
        return "—"
    p = Path(path)
    tail = p.parts[-parts:]
    short = "/".join(tail)
    return short if len(p.parts) <= parts else "…/" + short


def reveal_in_file_manager(path: str) -> None:
    """Safely reveal and highlight a file in the OS file manager."""
    if not path:
        return
    norm_path = os.path.normpath(path)
    try:
        if sys.platform == "win32":
            if os.path.isfile(norm_path):
                subprocess.Popen(["explorer.exe", "/select,", norm_path])
            elif os.path.isdir(norm_path):
                subprocess.Popen(["explorer.exe", norm_path])
            else:
                parent = os.path.dirname(norm_path)
                if os.path.exists(parent):
                    subprocess.Popen(["explorer.exe", parent])
        elif sys.platform == "darwin":
            if os.path.exists(norm_path):
                subprocess.Popen(["open", "-R", norm_path])
            else:
                subprocess.Popen(["open", os.path.dirname(norm_path)])
        else:
            # Linux / BSD
            folder = norm_path if os.path.isdir(norm_path) else os.path.dirname(norm_path)
            subprocess.Popen(["xdg-open", folder if os.path.exists(folder) else str(Path.home())])
    except Exception:
        pass


class Tooltip:
    """A lightweight hover tooltip for any widget."""

    def __init__(self, widget, text):
        self.widget = widget
        self._text = text
        self._tip: ctk.CTkToplevel | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        self._after_id = None

    def _resolve(self) -> str:
        return self._text() if callable(self._text) else self._text

    def _schedule(self, _evt=None):
        self._after_id = self.widget.after(450, self._show)

    def _show(self):
        text = self._resolve()
        if not text or self._tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tip = ctk.CTkToplevel(self.widget)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.geometry(f"+{x}+{y}")
        frame = ctk.CTkFrame(tip, fg_color=t.CARD_BG, corner_radius=8,
                             border_width=1, border_color=t.BORDER)
        frame.pack()
        ctk.CTkLabel(frame, text=text, font=t.font(11), text_color=t.TEXT,
                     justify="left").pack(padx=10, pady=6)

    def _hide(self, _evt=None):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None


class SupportDialog(ctk.CTkToplevel):
    """Modal dialog offering voluntary support options (UPI & Binance Pay) matching Tukdify Clips."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Support Tukdify")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=t.APP_BG)
        self.attributes("-topmost", True)
        self.transient(master)
        self.after(50, self._safe_focus_and_grab)

        self._upi_img = None
        self._binance_img = None

        self._build_ui()

    def _safe_focus_and_grab(self):
        try:
            if self.winfo_exists():
                self.focus()
                self.grab_set()
        except Exception:
            pass

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(header, text="Support Tukdify", font=t.font(18, "bold"),
                     text_color=t.TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Enjoying Tukdify Video Downloader?\nYour support keeps Tukdify tools free, offline, and independent.",
                     font=t.font(12), text_color=t.TEXT_MUTED, justify="left").pack(anchor="w", pady=(4, 0))

        # Method Switcher (Segmented button)
        self.tab_var = ctk.StringVar(value="UPI (India)")
        self.tab_menu = ctk.CTkSegmentedButton(
            self, values=["UPI (India)", "Binance Pay"], variable=self.tab_var,
            height=34, font=t.font(13, "bold"), command=self._on_tab_change,
        )
        t.style_segmented(self.tab_menu)
        self.tab_menu.pack(fill="x", padx=24, pady=10)

        # Card Container
        self.card = ctk.CTkFrame(self, fg_color=t.CARD_BG, corner_radius=14,
                                 border_width=1, border_color=t.BORDER)
        self.card.pack(fill="both", expand=True, padx=24, pady=(6, 16))

        self._show_upi_panel()

    def _on_tab_change(self, val: str):
        if "UPI" in val:
            self._show_upi_panel()
        else:
            self._show_binance_panel()

    def _show_upi_panel(self):
        for w in self.card.winfo_children():
            w.destroy()

        # QR Code Display
        qr_p = support_asset("upi_qr.png")
        if qr_p and qr_p.exists():
            try:
                img = Image.open(qr_p)
                self._upi_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 210))
                qr_box = ctk.CTkFrame(self.card, fg_color="#ffffff", corner_radius=10)
                qr_box.pack(pady=(16, 10))
                ctk.CTkLabel(qr_box, image=self._upi_img, text="").pack(padx=6, pady=6)
            except Exception:
                ctk.CTkLabel(self.card, text="UPI QR Asset", font=t.font(14, "bold")).pack(pady=30)
        else:
            ctk.CTkLabel(self.card, text="UPI QR Asset", font=t.font(14, "bold")).pack(pady=30)

        # Recipient Info
        ctk.CTkLabel(self.card, text=f"Recipient: {UPI_RECIPIENT}", font=t.font(13, "bold"),
                     text_color=t.TEXT).pack(pady=(2, 0))
        ctk.CTkLabel(self.card, text=UPI_ID, font=t.mono_font(11),
                     text_color=t.TEXT_MUTED).pack(pady=(1, 10))

        # Copy Action
        self.copy_upi_btn = t.ghost_button(self.card, text="Copy UPI ID", width=140, height=32,
                                           command=self._copy_upi)
        self.copy_upi_btn.pack(pady=(0, 14))

    def _show_binance_panel(self):
        for w in self.card.winfo_children():
            w.destroy()

        qr_p = support_asset("binance_pay_qr.png")
        if qr_p and qr_p.exists():
            try:
                img = Image.open(qr_p)
                self._binance_img = ctk.CTkImage(light_image=img, dark_image=img, size=(160, 210))
                qr_box = ctk.CTkFrame(self.card, fg_color="#ffffff", corner_radius=10)
                qr_box.pack(pady=(16, 10))
                ctk.CTkLabel(qr_box, image=self._binance_img, text="").pack(padx=6, pady=6)
            except Exception:
                ctk.CTkLabel(self.card, text="Binance Pay QR", font=t.font(14, "bold")).pack(pady=30)
        else:
            ctk.CTkLabel(self.card, text="Binance Pay QR", font=t.font(14, "bold")).pack(pady=30)

        ctk.CTkLabel(self.card, text="Binance Pay", font=t.font(14, "bold"),
                     text_color=t.TEXT).pack(pady=(2, 0))
        ctk.CTkLabel(self.card, text="Scan with the Binance app to support Tukdify.",
                     font=t.font(11), text_color=t.TEXT_MUTED).pack(pady=(2, 14))

    def _copy_upi(self):
        self.clipboard_clear()
        self.clipboard_append(UPI_ID)
        self.copy_upi_btn.configure(text="Copied! ✓")
        self.after(1800, lambda: self.copy_upi_btn.configure(text="Copy UPI ID"))


class FollowDialog(ctk.CTkToplevel):
    """Modal dialog displaying official Tukdify channels and community connections."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Connect with Tukdify")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=t.APP_BG)
        self.attributes("-topmost", True)
        self.transient(master)
        self.after(50, self._safe_focus_and_grab)

        self._build_ui()

    def _safe_focus_and_grab(self):
        try:
            if self.winfo_exists():
                self.focus()
                self.grab_set()
        except Exception:
            pass

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(header, text="Connect with Tukdify", font=t.font(18, "bold"),
                     text_color=t.TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Follow Tukdify and connect with the creator community.",
                     font=t.font(12), text_color=t.TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        # Official Channels Section
        ctk.CTkLabel(scroll, text="OFFICIAL CHANNELS", font=t.font(11, "bold"),
                     text_color=t.ACCENT).pack(anchor="w", padx=8, pady=(8, 4))
        for name, sub, url, icon in OFFICIAL_CHANNELS:
            self._channel_row(scroll, name, sub, url, icon)

        # Community Section
        ctk.CTkLabel(scroll, text="COMMUNITY & FOUNDER", font=t.font(11, "bold"),
                     text_color=t.VIOLET).pack(anchor="w", padx=8, pady=(16, 4))
        for name, sub, url, icon in COMMUNITY_CHANNELS:
            self._channel_row(scroll, name, sub, url, icon)

    def _channel_row(self, parent, name: str, sub: str, url: str, icon: str):
        card = ctk.CTkFrame(parent, fg_color=t.CARD_BG, corner_radius=10,
                            border_width=1, border_color=t.BORDER)
        card.pack(fill="x", padx=4, pady=3)
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text=icon, font=t.font(14), width=32).grid(row=0, column=0, rowspan=2, padx=(10, 4))
        ctk.CTkLabel(card, text=name, font=t.font(13, "bold"), text_color=t.TEXT, anchor="w").grid(row=0, column=1, sticky="w", pady=(6, 0))
        ctk.CTkLabel(card, text=sub, font=t.font(11), text_color=t.TEXT_MUTED, anchor="w").grid(row=1, column=1, sticky="w", pady=(0, 6))

        t.ghost_button(card, text="Open ↗", width=64, height=28,
                       command=lambda u=url: webbrowser.open(u)).grid(row=0, column=2, rowspan=2, padx=10)

