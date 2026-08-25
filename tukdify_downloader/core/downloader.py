"""yt-dlp wrapper: info extraction + downloading with progress + cancel."""
from __future__ import annotations

import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from typing import Callable

import yt_dlp

from ..config import find_ffmpeg

# yt-dlp colourises its _speed_str / _eta_str with ANSI escape codes; strip them
# so the GUI never shows raw terminal sequences like "[0;32m498 KB/s[0m".
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _clean(text: str) -> str:
    """Remove ANSI colour codes and surrounding whitespace from yt-dlp strings."""
    return _ANSI_RE.sub("", text or "").strip()


class CancelledError(Exception):
    """Raised inside the progress hook to abort an in-flight download."""


@dataclass
class MediaInfo:
    """Normalised subset of yt-dlp's info dict for the UI."""
    title: str = ""
    uploader: str = ""
    duration: int = 0          # seconds
    view_count: int = 0
    thumbnail: str = ""
    is_playlist: bool = False
    entry_count: int = 0
    qualities: list[str] = field(default_factory=list)  # e.g. ["2160p", "1440p", "1080p", "720p"]
    entries: list[dict] = field(default_factory=list)   # playlist entries if applicable
    raw: dict = field(default_factory=dict)

    @property
    def duration_str(self) -> str:
        s = int(self.duration or 0)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

    @property
    def views_str(self) -> str:
        n = self.view_count or 0
        for unit, div in (("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)):
            if n >= div:
                return f"{n / div:.1f}{unit}"
        return str(n)


# Quality label -> max height (None = best available).
_QUALITY_HEIGHT = {
    "Best": None,
    "Best (4K/1440p)": None,
    "4K": 2160,
    "2160p": 2160,
    "1440p": 1440,
    "1080p": 1080,
    "1080p Full HD": 1080,
    "720p": 720,
    "720p HD": 720,
    "480p": 480,
    "360p": 360,
}

# Output filename templates per naming mode.
_NAMING_TEMPLATE = {
    "title": "%(title)s.%(ext)s",
    "uploader_title": "%(uploader)s - %(title)s.%(ext)s",
    "title_quality": "%(title)s [%(height)sp].%(ext)s",
}


def _quiet_logger():
    class _L:
        def debug(self, m): pass
        def info(self, m): pass
        def warning(self, m): pass
        def error(self, m): pass
    return _L()


def extract_info(url: str, playlist: bool = False) -> MediaInfo:
    """Fetch metadata for *url* without downloading. Raises on failure."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "logger": _quiet_logger(),
        "noplaylist": not playlist,
        "extract_flat": "in_playlist" if playlist else False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        data = ydl.extract_info(url, download=False)

    info = MediaInfo(raw=data)
    if data.get("_type") == "playlist" or "entries" in data:
        entries = [e for e in (data.get("entries") or []) if e]
        info.is_playlist = True
        info.entry_count = len(entries)
        info.entries = entries
        info.title = data.get("title") or "Playlist"
        info.uploader = data.get("uploader") or data.get("channel") or ""
        
        # Robust playlist thumbnail fallback (Bug 2 fix)
        info.thumbnail = data.get("thumbnail") or ""
        if not info.thumbnail and entries:
            for entry in entries:
                thumb = entry.get("thumbnail")
                if not thumb and entry.get("thumbnails"):
                    thumb = entry["thumbnails"][-1].get("url")
                if thumb:
                    info.thumbnail = thumb
                    break
        return info

    info.title = data.get("title") or "Untitled"
    info.uploader = data.get("uploader") or data.get("channel") or ""
    info.duration = data.get("duration") or 0
    info.view_count = data.get("view_count") or 0
    info.thumbnail = data.get("thumbnail") or ""
    heights = sorted(
        {f.get("height") for f in (data.get("formats") or []) if f.get("height")},
        reverse=True,
    )
    info.qualities = [f"{h}p" for h in heights]
    return info


@dataclass
class DownloadJob:
    """A single queued download request with unique UUID tracking."""
    url: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = ""
    mode: str = "Video"           # Video | MP3
    quality: str = "Best"
    download_dir: str = "."
    naming: str = "title"
    write_thumbnail: bool = False
    write_subtitles: bool = False
    subtitles_lang: str = "en"
    embed_metadata: bool = True
    is_playlist: bool = False
    title: str = ""               # filled in once known
    # runtime state
    status: str = "queued"        # queued|downloading|done|error|cancelled|paused
    progress: float = 0.0         # 0..1
    speed: str = ""
    eta: str = ""
    message: str = ""
    filepath: str = ""
    _cancel: threading.Event = field(default_factory=threading.Event)

    def cancel(self):
        self._cancel.set()


class Downloader:
    """Runs a single :class:`DownloadJob`, reporting progress via callback."""

    def __init__(self, job: DownloadJob, on_progress: Callable[[DownloadJob], None]):
        self.job = job
        self.on_progress = on_progress

    # -- yt-dlp option assembly -------------------------------------------
    def _build_opts(self) -> dict:
        job = self.job
        template = _NAMING_TEMPLATE.get(job.naming, _NAMING_TEMPLATE["title"])
        outtmpl = os.path.join(job.download_dir, template)

        opts: dict = {
            "outtmpl": outtmpl,
            "noplaylist": not job.is_playlist,
            "ignoreerrors": job.is_playlist,   # keep going on a bad playlist item
            "continuedl": True,                 # resume partial files
            "retries": 5,
            "quiet": True,
            "no_warnings": True,
            "logger": _quiet_logger(),
            "progress_hooks": [self._hook],
            "postprocessors": [],
        }

        ffmpeg_dir = find_ffmpeg()
        if ffmpeg_dir:
            opts["ffmpeg_location"] = ffmpeg_dir

        if job.mode == "MP3":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"].append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320" if "320" in job.quality else "192",
            })
        else:
            height = _QUALITY_HEIGHT.get(job.quality)
            if height:
                opts["format"] = (
                    f"bestvideo[height<={height}]+bestaudio/"
                    f"best[height<={height}]/best"
                )
            else:
                opts["format"] = "bestvideo+bestaudio/best"
            opts["merge_output_format"] = "mp4"

        if job.write_thumbnail:
            opts["writethumbnail"] = True
        if job.write_subtitles:
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = True
            lang = job.subtitles_lang or "en"
            opts["subtitleslangs"] = [f"{lang}.*", lang, "en.*", "en"]
        if job.embed_metadata and job.mode != "MP3":
            opts["postprocessors"].append({"key": "FFmpegMetadata"})

        return opts

    # -- progress -----------------------------------------------------------
    def _hook(self, d: dict):
        job = self.job
        if job._cancel.is_set():
            raise CancelledError()
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            job.progress = (done / total) if total else 0.0
            job.speed = _clean(d.get("_speed_str", ""))
            job.eta = _clean(d.get("_eta_str", ""))
            job.status = "downloading"
        elif status == "finished":
            # download done; post-processing (merge/convert) may still run
            job.progress = 1.0
            job.message = "Processing…"
            if d.get("filename"):
                job.filepath = d["filename"]
        self.on_progress(job)

    # -- run ----------------------------------------------------------------
    def run(self) -> DownloadJob:
        job = self.job
        try:
            job.status = "downloading"
            job.message = "Starting…"
            self.on_progress(job)
            with yt_dlp.YoutubeDL(self._build_opts()) as ydl:
                info = ydl.extract_info(job.url, download=True)
            if not job.title:
                job.title = (info or {}).get("title", job.url)
            
            # Accurate final filepath calculation (Bug 1 fix for MP3 & video)
            try:
                raw_filename = ydl.prepare_filename(info)
                if job.mode == "MP3":
                    base_path = os.path.splitext(raw_filename)[0]
                    job.filepath = f"{base_path}.mp3"
                else:
                    job.filepath = raw_filename
            except Exception:
                pass

            job.status = "done"
            job.progress = 1.0
            job.message = "Completed"
        except CancelledError:
            job.status = "cancelled"
            job.message = "Cancelled"
        except yt_dlp.utils.DownloadError as e:
            job.status = "error"
            job.message = _friendly_error(str(e))
        except Exception as e:  # noqa: BLE001 - surface anything else to the UI
            job.status = "error"
            job.message = _friendly_error(str(e))
        self.on_progress(job)
        return job


def _friendly_error(raw: str) -> str:
    """Translate noisy yt-dlp errors into something a human can act on."""
    raw = _clean(raw)
    low = raw.lower()
    if "drm" in low or "this video is drm protected" in low:
        return "This video is DRM-protected and cannot be downloaded."
    if "private video" in low:
        return "This video is private."
    if "members-only" in low or "join this channel" in low:
        return "Members-only content (needs your login cookies)."
    if "video unavailable" in low:
        return "Video unavailable or removed."
    if "sign in to confirm your age" in low or "age" in low and "restrict" in low:
        return "Age-restricted (needs login cookies)."
    if "unable to download webpage" in low or "getaddrinfo" in low or \
       "failed to resolve" in low or "connection" in low:
        return "Network error — check your internet connection."
    if "unsupported url" in low or "no video formats" in low:
        return "Unsupported or invalid link."
    # Keep it short: last meaningful line.
    line = raw.strip().splitlines()[-1] if raw.strip() else "Download failed."
    return line.replace("ERROR:", "").strip()[:200] or "Download failed."

