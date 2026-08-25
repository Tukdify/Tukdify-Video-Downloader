@echo off
REM ---------------------------------------------------------------------------
REM  Build Tukdify-Video-Downloader.exe locally on Windows.
REM  (You normally don't need this - GitHub Actions builds it for you. Use this
REM   only if you want to build on your own Windows machine.)
REM
REM  Requirements: Python 3.10+ installed and on PATH, plus ffmpeg.exe and
REM  ffprobe.exe placed next to this file (download from gyan.dev or BtbN).
REM ---------------------------------------------------------------------------
setlocal

echo [1/4] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/4] Installing dependencies (newest yt-dlp)...
python -m pip install --upgrade pip
pip install -U yt-dlp customtkinter pyinstaller Pillow

echo [3/4] Checking for ffmpeg...
if not exist ffmpeg.exe (
  echo   WARNING: ffmpeg.exe not found next to build.bat.
  echo   1080p/4K stream merging and MP3 extraction will not work without it.
)

echo [4/4] Building EXE...
set ICON=
if exist assets\icon.ico set ICON=--icon assets\icon.ico

pyinstaller --noconfirm --onefile --windowed ^
  --name Tukdify-Video-Downloader ^
  --version-file version_info.txt ^
  --collect-all customtkinter ^
  --add-data "assets;assets" ^
  --add-binary "ffmpeg.exe;." ^
  --add-binary "ffprobe.exe;." ^
  %ICON% ^
  main.py

echo.
echo Done. Your app is at: dist\Tukdify-Video-Downloader.exe
endlocal
pause
