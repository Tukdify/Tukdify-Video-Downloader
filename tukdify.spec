# -*- mode: python ; coding: utf-8 -*-
"""Tukdify Video Downloader — PyInstaller spec (standalone onefile, Windows).

Build:   pyinstaller tukdify.spec --noconfirm
Output:  dist/Tukdify-Video-Downloader.exe
"""
import os
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect customtkinter package data & hidden imports
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")

datas = [("assets", "assets")] + ctk_datas
binaries = list(ctk_binaries)
hiddenimports = list(ctk_hiddenimports)

# External CLI binaries (ffmpeg.exe, ffprobe.exe). Bundled if present.
for b in ["ffmpeg.exe", "ffprobe.exe", "ffmpeg", "ffprobe"]:
    if os.path.isfile(b):
        binaries.append((b, "."))

excludes = [
    "matplotlib", "PyQt5", "PyQt6", "PySide2", "PySide6",
    "scipy", "pandas", "IPython", "notebook", "pytest",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Tukdify-Video-Downloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                      # Keep UPX OFF to prevent antivirus false positives
    console=False,                  # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="version_info.txt" if os.path.isfile("version_info.txt") else None,
    icon="assets/tukdify.ico" if os.path.isfile("assets/tukdify.ico") else None,
)
