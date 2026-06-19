"""Paths, ffmpeg resolution, and runtime helpers shared across MediaForge."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running inside a PyInstaller bundle (the .exe)."""
    return getattr(sys, "frozen", False)


def resource_dir() -> Path:
    """Directory where bundled resources live (PyInstaller _MEIPASS or source root)."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
    return Path(__file__).resolve().parent.parent


def app_data_dir() -> Path:
    """Per-user writable directory for settings, history and logs."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "MediaForge"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_download_dir() -> Path:
    """Sensible default save location (the OS Downloads folder)."""
    candidate = Path.home() / "Downloads"
    return candidate if candidate.exists() else Path.home()


def find_ffmpeg() -> str | None:
    """Locate an ffmpeg binary.

    Order: bundled-next-to-exe -> PyInstaller temp dir -> system PATH.
    Returns the directory containing ffmpeg (what yt-dlp's ``ffmpeg_location``
    expects), or ``None`` to let yt-dlp search the system PATH itself.
    """
    names = ["ffmpeg.exe", "ffmpeg"] if os.name == "nt" else ["ffmpeg"]

    search_dirs = []
    if is_frozen():
        search_dirs.append(Path(os.path.dirname(sys.executable)))
        search_dirs.append(resource_dir())
    # Also allow a local ./ffmpeg/ folder during development.
    search_dirs.append(resource_dir() / "ffmpeg")

    for d in search_dirs:
        for name in names:
            p = d / name
            if p.exists():
                return str(d)

    # Fall back to system PATH.
    from shutil import which
    for name in names:
        if which(name):
            return None  # yt-dlp will find it on PATH
    return None
