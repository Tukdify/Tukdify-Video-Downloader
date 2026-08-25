from __future__ import annotations
import pytest
from main import _selftest

def test_full_app_ui_lifecycle():
    exit_code = _selftest()
    assert exit_code == 0
