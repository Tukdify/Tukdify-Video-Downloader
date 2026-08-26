from __future__ import annotations
import hashlib
import os
from pathlib import Path
import pytest

from tukdify_downloader import __version__, __app_name__
from tukdify_downloader.config import resource_dir, app_icon_path

CLIPS_ICO_SHA256 = "b056e91e5cbd2835c1f08888f2e12169c3aeee02dccbefa62f2c02a082f11ef3"


def test_canonical_ico_checksum_matches_clips():
    """Verify assets/tukdify.ico matches the canonical Tukdify Falcon ICO hash."""
    root = resource_dir()
    ico_path = root / "assets" / "tukdify.ico"
    assert ico_path.exists(), "assets/tukdify.ico must exist"

    with open(ico_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == CLIPS_ICO_SHA256, f"assets/tukdify.ico SHA256 mismatch! Got {h}, expected {CLIPS_ICO_SHA256}"


def test_no_legacy_mediaforge_assets_exist():
    """Ensure no old MediaForge images or folders exist in the project."""
    root = resource_dir()
    assert not (root / "assets" / "logo.png").exists(), "Old assets/logo.png must not exist"
    assert not (root / "assets" / "icon.ico").exists(), "Old assets/icon.ico must not exist"
    assert not (root / "mediaforge").exists(), "Legacy mediaforge/ directory must not exist"


def test_windows_version_metadata():
    """Verify version_info.txt contains correct metadata for v2.0.1."""
    root = resource_dir()
    vinfo_path = root / "version_info.txt"
    assert vinfo_path.exists(), "version_info.txt must exist"

    content = vinfo_path.read_text(encoding="utf-8")
    assert "filevers=(2, 0, 1, 0)" in content
    assert "prodvers=(2, 0, 1, 0)" in content
    assert "'CompanyName', 'Tukdify'" in content
    assert "'FileDescription', 'Tukdify Video Downloader'" in content
    assert "'FileVersion', '2.0.1.0'" in content
    assert "'OriginalFilename', 'Tukdify-Video-Downloader.exe'" in content
    assert "'ProductName', 'Tukdify Video Downloader'" in content
    assert "'ProductVersion', '2.0.1.0'" in content
    assert "MediaForge" not in content


def test_inno_setup_installer_script():
    """Verify installer/tukdify.iss configuration and shortcuts."""
    root = resource_dir()
    iss_path = root / "installer" / "tukdify.iss"
    assert iss_path.exists(), "installer/tukdify.iss must exist"

    content = iss_path.read_text(encoding="utf-8")
    assert '#define MyAppName "Tukdify Video Downloader"' in content
    assert '#define MyAppVersion "2.0.1"' in content
    assert '#define MyAppExeName "Tukdify-Video-Downloader.exe"' in content
    assert '#define MyAppPublisher "Tukdify"' in content
    assert "SetupIconFile=..\\assets\\tukdify.ico" in content
    assert "OutputBaseFilename=Tukdify-Video-Downloader-Setup-{#MyAppVersion}" in content
    assert 'Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"' in content
    assert 'Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon' in content
    assert "UninstallDisplayIcon={app}\\{#MyAppExeName}" in content
    assert "UninstallDisplayName={#MyAppName}" in content
    assert "MediaForge" not in content


def test_pyinstaller_spec_file():
    """Verify tukdify.spec packaging configuration."""
    root = resource_dir()
    spec_path = root / "tukdify.spec"
    assert spec_path.exists(), "tukdify.spec must exist"

    content = spec_path.read_text(encoding="utf-8")
    assert 'name="Tukdify-Video-Downloader"' in content
    assert 'icon="assets/tukdify.ico"' in content
    assert 'version="version_info.txt"' in content
    assert "MediaForge" not in content


def test_app_user_model_id_is_canonical():
    """Verify AppUserModelID in ui/app.py is stable Tukdify.VideoDownloader."""
    root = resource_dir()
    app_py = root / "tukdify_downloader" / "ui" / "app.py"
    assert app_py.exists()

    content = app_py.read_text(encoding="utf-8")
    assert 'SetCurrentProcessExplicitAppUserModelID("Tukdify.VideoDownloader")' in content
    assert "tukdify.videodownloader.2.0" not in content
    assert "MediaForge" not in content


def test_app_version_is_2_0_1():
    """Verify package version is bumped to 2.0.1."""
    assert __version__ == "2.0.1"
    assert __app_name__ == "Tukdify Video Downloader"
