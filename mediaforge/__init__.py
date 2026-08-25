"""Backward-compatibility shim for MediaForge -> Tukdify Video Downloader."""
from __future__ import annotations
import sys
import tukdify_downloader
sys.modules["mediaforge"] = tukdify_downloader
from tukdify_downloader import *
