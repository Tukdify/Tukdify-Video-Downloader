"""Lightweight URL -> platform detection (no network calls)."""
from __future__ import annotations

from urllib.parse import urlparse

# (display name, list of host substrings) — checked in order.
_HOST_MAP = [
    ("YouTube", ["youtube.com", "youtu.be", "youtube-nocookie.com"]),
    ("Instagram", ["instagram.com", "instagr.am"]),
    ("TikTok", ["tiktok.com"]),
    ("Facebook", ["facebook.com", "fb.watch", "fb.com"]),
    ("X (Twitter)", ["twitter.com", "x.com", "t.co"]),
    ("Reddit", ["reddit.com", "redd.it"]),
    ("Twitch", ["twitch.tv"]),
    ("Vimeo", ["vimeo.com"]),
    ("Dailymotion", ["dailymotion.com", "dai.ly"]),
    ("SoundCloud", ["soundcloud.com"]),
    ("Pinterest", ["pinterest.com", "pin.it"]),
]


def detect_platform(url: str) -> str:
    """Return a human-readable platform name for *url* ('Unknown' if unrecognised)."""
    if not url or "." not in url:
        return ""
    raw = url.strip()
    if "://" not in raw:
        raw = "https://" + raw
    host = (urlparse(raw).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return "Unknown"

    path = urlparse(raw).path.lower()
    for name, hosts in _HOST_MAP:
        if any(h in host for h in hosts):
            if name == "YouTube" and "/shorts/" in path:
                return "YouTube Shorts"
            return name
    return "Unknown"


def looks_like_url(text: str) -> bool:
    """Cheap sanity check that *text* could be a URL."""
    if not text:
        return False
    t = text.strip()
    return ("." in t) and (" " not in t) and len(t) > 4
