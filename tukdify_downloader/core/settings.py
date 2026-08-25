"""User settings persisted as JSON in the per-user app-data directory."""
from __future__ import annotations

import json
from pathlib import Path

from ..config import app_data_dir, default_download_dir

_DEFAULTS = {
    "download_dir": str(default_download_dir()),
    "appearance": "Dark",          # Dark | Light | System
    "default_quality": "Best (4K/1440p)",  # Best (4K/1440p) | 1080p | 720p | 480p | 360p
    "default_mode": "Video",        # Video | MP3
    "naming": "title",              # title | uploader_title | title_quality
    "write_thumbnail": False,
    "write_subtitles": False,
    "subtitles_lang": "en",
    "embed_metadata": True,
    "concurrency": 2,
}


def _settings_file() -> Path:
    return app_data_dir() / "settings.json"


def load() -> dict:
    """Return saved settings merged over defaults."""
    data = dict(_DEFAULTS)
    sf = _settings_file()
    if sf.exists():
        try:
            data.update(json.loads(sf.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    # Guard against a download dir that no longer exists.
    if not Path(data["download_dir"]).exists():
        data["download_dir"] = str(default_download_dir())
    return data


def save(data: dict) -> None:
    """Persist *data* (merged over defaults) to disk."""
    merged = dict(_DEFAULTS)
    merged.update(data)
    try:
        _settings_file().write_text(json.dumps(merged, indent=2), encoding="utf-8")
    except OSError:
        pass

