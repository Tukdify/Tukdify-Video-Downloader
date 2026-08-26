@echo off
REM ---------------------------------------------------------------------------
REM  Build Tukdify Video Downloader standalone EXE and installer locally on Windows.
REM ---------------------------------------------------------------------------
setlocal

echo [1/5] Setting up virtual environment...
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller Pillow pefile

echo [3/5] Checking for ffmpeg binaries...
if not exist ffmpeg.exe (
  echo   NOTE: ffmpeg.exe not found in repo root.
  echo   If not bundled, yt-dlp will fall back to system PATH.
)

echo [4/5] Building Standalone EXE with PyInstaller...
pyinstaller tukdify.spec --noconfirm --clean

if %ERRORLEVEL% neq 0 (
  echo Build failed!
  exit /b %ERRORLEVEL%
)

echo.
echo Standalone EXE built: dist\Tukdify-Video-Downloader.exe

echo [5/5] Building Windows Installer with Inno Setup (if available)...
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"

if exist %ISCC% (
  %ISCC% installer\tukdify.iss
  if %ERRORLEVEL% equ 0 (
    echo Installer built in: installer\Output\
  ) else (
    echo Inno Setup compilation failed!
  )
) else (
  echo Inno Setup 6 (ISCC.exe) not found. Skipping installer creation.
)

echo.
echo Build complete.
endlocal
pause
