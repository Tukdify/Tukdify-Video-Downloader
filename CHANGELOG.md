# Changelog

All notable changes to **MediaForge** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-06-19

A UI/UX-focused release. No changes to the download engine — same reliable
yt-dlp + ffmpeg core, with a much more polished and professional desktop feel.

### Added
- **URL placeholder** — the link field now shows a clear hint
  (“Paste a video URL here — YouTube, Instagram, TikTok and more…”) that
  disappears on focus and returns when the field is empty.
- **Native folder picker** — “Change” / “Browse” now open the desktop’s native
  folder dialog (GTK/KDE on Linux, native on Windows/macOS) instead of the
  dated Tk chooser.
- **Hover tooltip** on the download location showing the full path.

### Changed
- **Modern UI redesign** — a neutral, professional dark theme (refined indigo
  accent), a centred max-width content layout, an integrated URL bar
  (Paste + Fetch info), a single Type / Quality / Extras options row, a compact
  download-location row, and a prominent primary download button. The logo now
  appears only in the sidebar header and the About page.
- **Cleaner queue cards** — improved spacing, typography and information
  hierarchy: status on the left, speed / ETA right-aligned and muted, a thin
  rounded progress bar, and consistent, vertically-centred actions
  (Cancel → Open / Failed).
- **Improved download-location display** — long paths are shortened to the last
  segments (e.g. `📁 …/Desktop/youtube video download`); the full path is
  available on hover.
- **Better responsiveness** — verified across 1280×720, 1366×768 and 1920×1080
  with no clipping, overlap or truncated controls; layout stays centred and
  readable on ultrawide and high-DPI displays.

### Fixed
- **ANSI escape codes** are now stripped from yt-dlp output, so download speed,
  ETA and error messages render cleanly (e.g. `498 KB/s · ETA 17:07` instead of
  raw terminal colour codes).

## [1.0.0] — 2026-06-19

Initial release.

### Added
- Multi-platform media downloader built on yt-dlp and ffmpeg.
- Video and MP3 (audio) downloads with selectable quality.
- Optional thumbnail, subtitle and metadata embedding; playlist support.
- Sidebar navigation: Downloads, History, Settings and About.
- Download queue with live progress, cancel and open-folder actions.
- Persistent settings and download history.
- Offline, ad-free and login-free — downloads never leave your computer.
- Windows executable, automatically built and published from source.

[1.1.0]: https://github.com/sourabh-jangid-dev/mediaforge/releases/tag/v1.1.0
[1.0.0]: https://github.com/sourabh-jangid-dev/mediaforge/releases/tag/v1.0.0
