<p align="center">
  <img src="assets/branding/tukdify_falcon_256.png" alt="Tukdify Falcon" width="128">
</p>

<h1 align="center">Tukdify Video Downloader</h1>
<p align="center"><strong>Universal 4K & MP3 Media Ingestion for Creators & Editors</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue.svg?style=flat-square" alt="Version 2.0.0">
  <img src="https://img.shields.io/badge/ecosystem-Tukdify%20Suite-8B5CF6.svg?style=flat-square" alt="Tukdify Suite">
  <img src="https://img.shields.io/badge/license-MIT-emerald.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-cyan.svg?style=flat-square" alt="Platforms">
</p>

---

## 🦅 Overview

**Tukdify Video Downloader** is a high-performance desktop media utility engineered for creators, video editors, and archivists. Built with Python, CustomTkinter, and yt-dlp, it provides a fast, private, offline-first workflow for downloading 4K video, 320kbps MP3 audio, cover art, and subtitles across 1,000+ platforms.

Part of the **Tukdify Creator Ecosystem**:
- 🎬 **[Tukdify Clips](https://github.com/Tukdify/Tukdify-clips)** — AI Long-Form to Viral Shorts Studio
- ⬇️ **[Tukdify Video Downloader](https://github.com/Tukdify/Tukdify-Video-Downloader)** — Universal 4K & MP3 Ingestion
- ⚡ **[Tukdify Multicompressor](https://github.com/Tukdify/Tukdify-Multicompressor)** — GPU-Accelerated Media Optimizer

---

## ⚡ Key Features (v2.0.0)

- 🎯 **Streamlined 4-Step Canvas:** Paste URL → Automatic Stream Analysis → Choose Format → Download.
- 📺 **4K & High-Bitrate Audio:** One-click presets for `Best Video (4K/1440p)`, `1080p Full HD`, and `MP3 Audio (320k)`.
- 📁 **Interactive Playlist Picker:** Inspect and select individual videos from multi-item playlists before downloading.
- 🎛️ **Collapsible Advanced Drawer:** Granular controls for resolution override, subtitle language selection, metadata embedding, and save folders.
- 🔍 **Searchable History:** Instant keyword search, platform filtering pills, file size indicators, and safe single-item management.
- 🛡️ **Zero Tracking & Local-First:** No accounts, no telemetry, and no DRM bypass. All processing occurs locally on your machine.
- 📦 **Single Standalone Executable:** Windows executable bundles FFmpeg 7.1 essentials — zero external setup needed.

---

## 📥 Download & Run (Windows)

1. Go to the **[Releases](../../releases/latest)** page.
2. Download **`Tukdify-Video-Downloader.exe`**.
3. Double-click to launch — completely portable with zero installation required.

---

## 🛠️ Development & Source Setup

```bash
git clone https://github.com/Tukdify/Tukdify-Video-Downloader.git
cd Tukdify-Video-Downloader
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Running Test Suite

```bash
PYTHONPATH=. pytest -v
```

### Running Offline UI Self-Test

```bash
python main.py --selftest
```

---

## ⚖️ Legal Notice

For personal, authorized archiving and workflow use. Please respect copyright and individual platform Terms of Service. Tukdify does not circumvent DRM or access paid/encrypted media.
