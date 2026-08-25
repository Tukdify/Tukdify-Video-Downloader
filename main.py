"""Tukdify Video Downloader entry point.

Run normally to open the app. Pass --selftest to build the window, render every
page once, then exit 0 — used by CI to verify the packaged .exe launches cleanly.
"""
import sys


def _selftest() -> int:
    from tukdify_downloader.ui.app import App
    app = App()
    app.update()
    for page in ("Downloads", "History", "Settings", "About"):
        app.select_page(page)
        app.update()
    app._on_close()
    print("Tukdify Video Downloader self-test OK")
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    from tukdify_downloader.ui.app import run
    run()


if __name__ == "__main__":
    main()
