# Changelog

All notable changes to **Tukdify Video Downloader** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] — 2026-08-26

Windows packaging, shell integration, and branding polish release.

### Added
- **Windows Inno Setup Installer:** Added official Windows Setup installer (`Tukdify-Video-Downloader-Setup-2.0.1.exe`) matching Tukdify Clips packaging standards.
- **Start Menu & Desktop Shortcuts:** Installer provisions Start Menu (`Tukdify Video Downloader`) and optional Desktop shortcuts with the canonical Falcon icon.
- **Add/Remove Programs Integration:** Registered Windows uninstaller with clean cleanup while preserving user downloads and `%APPDATA%` settings.
- **Dual Windows Distribution:** Releases officially provide both the Setup Installer (`Tukdify-Video-Downloader-Setup-2.0.1.exe`) and Standalone Portable executable (`Tukdify-Video-Downloader.exe`) along with `SHA256SUMS.txt`.
- **PyInstaller Specification:** Added `tukdify.spec` for deterministic, repeatable builds.
- **Packaging Test Suite:** Added `test_packaging_branding.py` to continuously verify canonical icon hashes, PE version metadata, Inno Setup configurations, and AppUserModelID.

### Fixed
- **Explorer Preview & Shell Identity:** Purged legacy MediaForge assets (`assets/logo.png` and legacy tree) and updated Windows AppUserModelID to stable `Tukdify.VideoDownloader`.
- **Windows PE Version Metadata:** Updated executable metadata resource to `v2.0.1.0` with full publisher and product attribution.

---

## [2.0.0] — 2026-08-25

Major re-architecture and complete rebranding into the **Tukdify Creator Ecosystem**.

### Added
- **Tukdify Master Brand System:** Integrated canonical Metal Silver Falcon mark, Obsidian Dark theme (`#0A0D14`, `#0E131F`, `#141A29`), Trust Blue (`#2563EB`), and Technical Cyan (`#06B6D4`).
- **Streamlined 4-Step Canvas:** Paste URL → Automatic Stream Analysis → 3-Choice Format Selector → 52px Primary Download CTA.
- **Interactive Playlist Picker Modal:** Inspect and select specific videos before downloading with Select All / Clear All toolbar.
- **Collapsible Advanced Options Drawer:** Granular controls for resolution override (4K to 360p), subtitle languages, cover art, chapter metadata, and custom directory path.
- **Tukdify Ecosystem Bridge Buttons:** Direct one-click workflow actions to launch Tukdify Clips and Tukdify Multicompressor upon download completion.
- **Searchable History with Platform Filters:** Instant search by title/URL, platform filter chips (YouTube, TikTok, Instagram, X, Facebook, Other), and single-item deletion.
- **Support & Community Modals:** Tukdify Clips parity Support Dialog (UPI & Binance Pay with one-click copy) and Connect/Follow Dialog.
- **Zero-Network Automated Test Suite:** Comprehensive `pytest` coverage for platforms, options builder, configuration, history persistence, and UI lifecycle.

### Fixed
- **MP3 Output Extension:** Fixed issue where MP3 audio downloads retained temporary video container extensions.
- **Playlist Thumbnail Fallback:** Added robust multi-tier fallback scanner to resolve valid thumbnails for entire playlists.
- **Queue Job Collision:** Migrated job tracking to `uuid.uuid4()` strings.
- **Safe Windows File Reveal:** Hardened file reveal command using `explorer.exe /select,"<filepath>"`.

---

## [1.1.0] — 2026-06-19

A UI/UX-focused release.

### Added
- **URL placeholder** and native folder pickers (GTK/KDE on Linux, native on Windows/macOS).
- **Hover tooltip** on download location showing full path.

---

## [1.0.0] — 2026-06-19

Initial release.

[2.0.1]: https://github.com/Tukdify/Tukdify-Video-Downloader/releases/tag/v2.0.1
[2.0.0]: https://github.com/Tukdify/Tukdify-Video-Downloader/releases/tag/v2.0.0
[1.1.0]: https://github.com/Tukdify/Tukdify-Video-Downloader/releases/tag/v1.1.0
[1.0.0]: https://github.com/Tukdify/Tukdify-Video-Downloader/releases/tag/v1.0.0
