from __future__ import annotations
import os
import pytest
from tukdify_downloader.core import settings as settings_store
from tukdify_downloader.core import history as history_store

def test_settings_load_and_save(tmp_path, monkeypatch):
    monkeypatch.setattr("tukdify_downloader.config.app_data_dir", lambda: tmp_path)
    data = settings_store.load()
    assert "download_dir" in data
    assert data["appearance"] in ("Dark", "Light", "System")

    data["default_quality"] = "1080p"
    settings_store.save(data)
    loaded = settings_store.load()
    assert loaded["default_quality"] == "1080p"

def test_history_add_remove_clear(tmp_path, monkeypatch):
    monkeypatch.setattr("tukdify_downloader.config.app_data_dir", lambda: tmp_path)
    history_store.clear()
    assert len(history_store.load()) == 0

    history_store.add("Sample Title", "https://youtube.com/watch?v=abc", "YouTube", "Video", "/path/to/vid.mp4", "1080p")
    entries = history_store.load()
    assert len(entries) == 1
    assert entries[0]["title"] == "Sample Title"
    assert entries[0]["quality"] == "1080p"

    history_store.remove("/path/to/vid.mp4")
    assert len(history_store.load()) == 0
