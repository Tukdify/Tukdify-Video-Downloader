from __future__ import annotations
import pytest
from tukdify_downloader.core.platforms import detect_platform, looks_like_url

def test_detect_platform_youtube():
    assert detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "YouTube"
    assert detect_platform("https://youtu.be/dQw4w9WgXcQ") == "YouTube"
    assert detect_platform("https://www.youtube.com/shorts/abcdef123") == "YouTube Shorts"

def test_detect_platform_tiktok_instagram():
    assert detect_platform("https://www.tiktok.com/@user/video/12345") == "TikTok"
    assert detect_platform("https://www.instagram.com/reel/C12345/") == "Instagram"

def test_detect_platform_x_twitter():
    assert detect_platform("https://twitter.com/tukdify/status/123") == "X (Twitter)"
    assert detect_platform("https://x.com/tukdify/status/123") == "X (Twitter)"

def test_looks_like_url():
    assert looks_like_url("https://youtube.com") is True
    assert looks_like_url("youtube.com/watch?v=123") is True
    assert looks_like_url("not a url") is False
    assert looks_like_url("") is False
