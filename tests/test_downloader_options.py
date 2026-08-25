from __future__ import annotations
import pytest
from tukdify_downloader.core.downloader import DownloadJob, Downloader

def test_job_uuid_generation():
    job1 = DownloadJob(url="https://youtube.com/watch?v=1")
    job2 = DownloadJob(url="https://youtube.com/watch?v=2")
    assert job1.id != job2.id
    assert len(job1.id) == 36  # standard UUID string length

def test_downloader_build_opts_video():
    job = DownloadJob(
        url="https://youtube.com/watch?v=test",
        mode="Video",
        quality="1080p",
        download_dir="/downloads",
        write_subtitles=True,
        subtitles_lang="en",
    )
    downloader = Downloader(job, on_progress=lambda j: None)
    opts = downloader._build_opts()
    assert opts["noplaylist"] is True
    assert "bestvideo[height<=1080]" in opts["format"]
    assert opts["writesubtitles"] is True
    assert "en.*" in opts["subtitleslangs"]

def test_downloader_build_opts_mp3_320k():
    job = DownloadJob(
        url="https://youtube.com/watch?v=test",
        mode="MP3",
        quality="320k",
        download_dir="/downloads",
    )
    downloader = Downloader(job, on_progress=lambda j: None)
    opts = downloader._build_opts()
    assert opts["format"] == "bestaudio/best"
    postprocessors = opts["postprocessors"]
    assert any(p.get("key") == "FFmpegExtractAudio" and p.get("preferredquality") == "320" for p in postprocessors)
