from __future__ import annotations
import os
from pathlib import Path
import pytest
from tukdify_downloader.config import (
    app_data_dir,
    branding_asset,
    support_asset,
    falcon_mark_path,
    logo_path,
    find_ffmpeg,
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
