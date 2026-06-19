# ⚒ MediaForge

**Free, offline, ad-free media downloader for Windows.**
Download video, audio (MP3), thumbnails and subtitles from YouTube and many
other sites — no login, no ads, no tracking.

> Built with Python · yt-dlp · ffmpeg · CustomTkinter · PyInstaller

---

## ✨ Features (v1.0)

- 🔗 Paste any link — **auto-detects the platform** (YouTube, Shorts, Instagram, TikTok, X, Reddit, …)
- 🔍 **Info preview** — title, channel, duration, views before you download
- ⬇️ **Video** (Best / 1080p / 720p / 480p / 360p) or **MP3** audio
- 🖼️ Optional **thumbnail** and **subtitle** download
- 📃 Whole-**playlist** download
- 📋 **Download queue** with live progress, speed & ETA, plus **Cancel**
- 🗂️ **History** of past downloads
- ⚙️ **Settings**: default folder, dark/light theme, quality, file naming
- 📦 Single `.exe`, **ffmpeg bundled inside** — nothing else to install

> **Note:** MediaForge will **not** download DRM-protected or paid content
> (YouTube Movies, Premium-exclusive, etc.) — that's technically impossible and
> against the rules. Only content you're allowed to access.

---

## 📥 For users (download & run)

1. Go to the **[Releases](../../releases/latest)** page.
2. Download **`MediaForge.exe`**.
3. Double-click it. That's it — no installation.

> Windows SmartScreen may warn about an "unknown publisher" (normal for
> unsigned indie apps) — click **More info → Run anyway**.

---

## 🛠️ For developers (run from source)

```bash
git clone <your-repo-url>
cd MediaForge
python -m venv .venv
# Windows:  .venv\Scripts\activate     | Linux/Mac:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

`ffmpeg` must be on your PATH for 1080p merging / MP3 when running from source.

---

## 🏗️ How the Windows `.exe` is built

You develop on any OS, but the `.exe` is built automatically by **GitHub
Actions** on a Windows runner — see [`.github/workflows/build-windows.yml`](.github/workflows/build-windows.yml).

- Builds on every push to `main`, on manual trigger, **and weekly**.
- Each build installs the **newest yt-dlp**, so releases never go stale when
  sites change.
- Publishes `MediaForge.exe` to the `latest` release automatically.

To build manually on a Windows machine instead, drop `ffmpeg.exe` + `ffprobe.exe`
next to `build.bat` and run it.

---

## 🗺️ Roadmap

- **v1.0** — MVP: video/MP3, quality, queue, progress, history, settings ✅
- **v1.5** — pause/resume, more naming options, batch paste
- **v2.0** — richer multi-platform UX, format chooser
- **v3.0** — dashboard, analytics, custom icon & polish
- **Creator Edition** — subtitle/metadata export toolkit

---

## ⚖️ Legal

For personal use. Respect copyright and each platform's Terms of Service.
Don't download content you don't have the right to. MediaForge does not and
will not circumvent DRM or paywalls.
