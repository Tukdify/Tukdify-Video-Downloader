"""MediaForge entry point.

Run normally to open the app. Pass --selftest to build the window, render every
page once, then exit 0 — used by CI to verify the packaged .exe actually launches.
"""
import sys


def _selftest() -> int:
    from mediaforge.ui.app import App
    app = App()
    app.update()
    for page in ("Downloads", "History", "Settings", "About"):
        app.select_page(page)
        app.update()
    app._on_close()
    print("MediaForge self-test OK")
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    from mediaforge.ui.app import run
    run()


if __name__ == "__main__":
    main()
