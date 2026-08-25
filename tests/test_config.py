from __future__ import annotations
import os
from pathlib import Path
import pytest
from tukdify_downloader.config import (
    app_data_dir,
    app_icon_path,
    branding_asset,
    support_asset,
    falcon_mark_path,
    logo_path,
    find_ffmpeg,
    resource_dir,
)

def test_app_data_dir_resolution():
    d = app_data_dir()
    assert isinstance(d, Path)
    assert "Tukdify" in str(d)
    assert d.exists()

def test_branding_asset_discovery():
    fp = falcon_mark_path()
    assert fp is not None
    assert fp.exists()
    assert "tukdify_mark_24.png" in str(fp)

def test_support_asset_discovery():
    upi_p = support_asset("upi_qr.png")
    binance_p = support_asset("binance_pay_qr.png")
    assert upi_p is not None and upi_p.exists()
    assert binance_p is not None and binance_p.exists()

def test_canonical_tukdify_ico_exists_and_valid():
    """assets/tukdify.ico exists, is resolved by app_icon_path, and contains 10 resolution layers."""
    ico_p = app_icon_path()
    assert ico_p is not None
    assert ico_p.exists()
    assert ico_p.name == "tukdify.ico"

    with open(ico_p, "rb") as f:
        header = f.read(6)
        count = int.from_bytes(header[4:6], "little")
        assert count == 10, f"Expected 10 ICO layers, got {count}"
        sizes = []
        for _ in range(count):
            entry = f.read(16)
            w = entry[0] or 256
            h = entry[1] or 256
            bpp = int.from_bytes(entry[6:8], "little")
            assert bpp == 32, f"Expected 32 bpp for layer {w}x{h}, got {bpp}"
            sizes.append((w, h))

    expected_sizes = [
        (16, 16), (20, 20), (24, 24), (32, 32), (40, 40),
        (48, 48), (64, 64), (96, 96), (128, 128), (256, 256)
    ]
    assert sizes == expected_sizes, f"Expected sizes {expected_sizes}, got {sizes}"

def test_old_mediaforge_icon_not_present_or_used():
    """Ensure old MediaForge icon is not used in packaging or workflows."""
    root = resource_dir()
    old_ico = root / "assets" / "icon.ico"
    assert not old_ico.exists(), "Old MediaForge assets/icon.ico should not exist in repository"

    # Verify build workflow uses tukdify.ico and does not reference old icon.ico
    workflow_file = root / ".github" / "workflows" / "build-windows.yml"
    assert workflow_file.exists()
    wf_text = workflow_file.read_text(encoding="utf-8")
    assert "assets/tukdify.ico" in wf_text
    assert "assets/icon.ico" not in wf_text

    # Verify build.bat uses tukdify.ico and does not reference old icon.ico
    bat_file = root / "build.bat"
    assert bat_file.exists()
    bat_text = bat_file.read_text(encoding="utf-8")
    assert "assets\\tukdify.ico" in bat_text or "assets/tukdify.ico" in bat_text
    assert "assets\\icon.ico" not in bat_text and "assets/icon.ico" not in bat_text
