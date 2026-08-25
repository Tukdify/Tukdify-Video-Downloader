"""Paths, ffmpeg resolution, asset helpers and runtime utilities for Tukdify."""
from __future__ import annotations

import os
import shutil
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
    """Per-user writable directory for settings, history and logs.

    Migrates existing settings/history from legacy %APPDATA%/MediaForge if present.
    """
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    target_dir = base / "Tukdify" / "VideoDownloader"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Backward-compatible migration from legacy MediaForge directory
    legacy_dir = base / "MediaForge"
    if legacy_dir.exists():
        for filename in ("settings.json", "history.json"):
            old_file = legacy_dir / filename
            new_file = target_dir / filename
            if old_file.exists() and not new_file.exists():
                try:
                    shutil.copy2(old_file, new_file)
                except OSError:
                    pass

    return target_dir


def default_download_dir() -> Path:
    """Sensible default save location (the OS Downloads folder / Tukdify Downloads)."""
    candidate = Path.home() / "Downloads"
    return candidate if candidate.exists() else Path.home()


def branding_asset(name: str) -> Path | None:
    """Resolve a canonical branding asset from assets/branding/ or assets/."""
    candidates = [
        resource_dir() / "assets" / "branding" / name,
        resource_dir() / "assets" / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def support_asset(name: str) -> Path | None:
    """Resolve a support asset (QR codes, etc.) from assets/support/ or assets/."""
    candidates = [
        resource_dir() / "assets" / "support" / name,
        resource_dir() / "assets" / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def logo_path() -> Path | None:
    """Path to the primary 256px or default Falcon logo PNG."""
    return branding_asset("tukdify_falcon_256.png") or branding_asset("tukdify_falcon.png")


def falcon_mark_path() -> Path | None:
    """Path to the compact 24px header Falcon mark."""
    return branding_asset("tukdify_mark_24.png") or logo_path()


def app_icon_path() -> Path | None:
    """Path to the canonical Tukdify Falcon Windows .ico file."""
    candidates = [
        resource_dir() / "assets" / "tukdify.ico",
        resource_dir() / "assets" / "branding" / "tukdify.ico",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


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
    for name in names:
        if shutil.which(name):
            return None  # yt-dlp will find it on PATH
    return None

