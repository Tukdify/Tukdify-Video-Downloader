"""Small UI helpers: a modern folder picker, path shortening and tooltips."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tkinter.filedialog as fd
from pathlib import Path

import customtkinter as ctk

from . import theme as t


def choose_directory(initialdir: str | None = None) -> str | None:
    """Open a folder picker, preferring the native OS dialog.

    On Linux the stock Tk chooser looks dated, so we use the desktop's native
    GTK/KDE dialog (zenity / kdialog) when present. Windows and macOS already
    get a native dialog from Tk, so we fall back to that everywhere else.
    """
    initialdir = initialdir or str(Path.home())

    if sys.platform.startswith("linux"):
        picked = _linux_native_dir(initialdir)
        if picked is not None:
            return picked or None  # "" means the user cancelled

    return fd.askdirectory(initialdir=initialdir) or None


def _linux_native_dir(initialdir: str) -> str | None:
    """Return a path from zenity/kdialog, "" if cancelled, or None if neither
    tool is available (so the caller can fall back to Tk)."""
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
    return ""  # user cancelled


def short_path(path: str, parts: int = 2) -> str:
    """A compact, human-friendly path: the last *parts* components.

    e.g. ``/home/me/Desktop/youtube video download`` -> ``Desktop/youtube video download``.
    The full path is still available for tooltips / details.
    """
    if not path:
        return "—"
    p = Path(path)
    tail = p.parts[-parts:]
    short = "/".join(tail)
    return short if len(p.parts) <= parts else "…/" + short


class Tooltip:
    """A lightweight hover tooltip for any widget.

    *text* may be a string or a zero-arg callable (resolved each time it shows,
    so it can reflect a value that changes — like the current folder).
    """

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
