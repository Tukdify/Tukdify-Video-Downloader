"""Downloads page: paste a URL, preview info, set options, queue downloads."""
from __future__ import annotations

import threading
import tkinter.filedialog as fd
from pathlib import Path

import customtkinter as ctk

from ...core import history as history_store
from ...core import settings as settings_store
from ...core.downloader import DownloadJob, MediaInfo, extract_info
from ...core.manager import DownloadManager
from ...core.platforms import detect_platform, looks_like_url

QUALITIES = ["Best", "1080p", "720p", "480p", "360p"]
MODES = ["Video", "MP3"]


class DownloadsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.s = app.settings
        self._info: MediaInfo | None = None
        self._info_token = 0
        self.manager = DownloadManager(on_update=self._on_job_update)
        self._cards: dict[int, "JobCard"] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_input()
        self._build_options()
        self._build_queue()

    # -- URL row + info preview --------------------------------------------
    def _build_input(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 8))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text="Paste a link",
                     font=ctk.CTkFont(size=22, weight="bold")
                     ).grid(row=0, column=0, columnspan=3, sticky="w")

        self.url_var = ctk.StringVar()
        self.url_var.trace_add("write", lambda *_: self._on_url_change())
        self.url_entry = ctk.CTkEntry(
            top, textvariable=self.url_var, height=44,
            placeholder_text="https://youtube.com/watch?v=…  (video, short, playlist, reel…)",
            font=ctk.CTkFont(size=14),
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self.fetch_btn = ctk.CTkButton(top, text="Fetch info", width=110, height=44,
                                       command=self._fetch_info)
        self.fetch_btn.grid(row=1, column=1, padx=(8, 0), pady=(10, 0))
        ctk.CTkButton(top, text="Paste", width=80, height=44, fg_color="gray30",
                      hover_color="gray25", command=self._paste
                      ).grid(row=1, column=2, padx=(8, 0), pady=(10, 0))

        self.platform_lbl = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=12),
                                         text_color=("gray40", "gray60"))
        self.platform_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        # Info preview card (hidden until fetched)
        self.info_card = ctk.CTkFrame(self, corner_radius=10)
        self.info_card.grid_columnconfigure(0, weight=1)
        self.info_title = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                       font=ctk.CTkFont(size=15, weight="bold"),
                                       justify="left", wraplength=620)
        self.info_title.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 2))
        self.info_meta = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                      text_color=("gray40", "gray60"))
        self.info_meta.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

    # -- options + download button -----------------------------------------
    def _build_options(self):
        opt = ctk.CTkFrame(self, corner_radius=10)
        opt.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        for c in range(4):
            opt.grid_columnconfigure(c, weight=1)

        ctk.CTkLabel(opt, text="Type").grid(row=0, column=0, padx=14, pady=(12, 0), sticky="w")
        self.mode_var = ctk.StringVar(value=self.s.get("default_mode", "Video"))
        self.mode_menu = ctk.CTkSegmentedButton(opt, values=MODES, variable=self.mode_var,
                                                command=lambda _: self._sync_quality_state())
        self.mode_menu.grid(row=1, column=0, padx=14, pady=(2, 12), sticky="ew")

        ctk.CTkLabel(opt, text="Quality").grid(row=0, column=1, padx=14, pady=(12, 0), sticky="w")
        self.quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best"))
        self.quality_menu = ctk.CTkOptionMenu(opt, values=QUALITIES, variable=self.quality_var)
        self.quality_menu.grid(row=1, column=1, padx=14, pady=(2, 12), sticky="ew")

        # extras
        extras = ctk.CTkFrame(opt, fg_color="transparent")
        extras.grid(row=0, column=2, rowspan=2, columnspan=2, sticky="w", padx=14)
        self.thumb_var = ctk.BooleanVar(value=self.s.get("write_thumbnail", False))
        self.subs_var = ctk.BooleanVar(value=self.s.get("write_subtitles", False))
        self.playlist_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(extras, text="Thumbnail", variable=self.thumb_var).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(extras, text="Subtitles", variable=self.subs_var).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(extras, text="Whole playlist", variable=self.playlist_var).pack(anchor="w", pady=2)

        # folder + download
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=1, column=0, sticky="ews", padx=24, pady=(96, 8))
        bottom.grid_columnconfigure(0, weight=1)
        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        self.folder_entry = ctk.CTkEntry(bottom, textvariable=self.folder_var, height=40)
        self.folder_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(bottom, text="📂 Folder", width=100, height=40, fg_color="gray30",
                      hover_color="gray25", command=self._choose_folder
                      ).grid(row=0, column=1, padx=(8, 0))
        self.download_btn = ctk.CTkButton(bottom, text="⬇  Download", width=150, height=40,
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          command=self._start_download)
        self.download_btn.grid(row=0, column=2, padx=(8, 0))
        self._sync_quality_state()

    def _build_queue(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=2, column=0, sticky="new", padx=24, pady=(8, 0))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Queue", font=ctk.CTkFont(size=15, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="Cancel all", width=90, height=28, fg_color="gray30",
                      hover_color="gray25", command=self.manager.cancel_all
                      ).grid(row=0, column=1, sticky="e")

        self.queue_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.queue_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(4, 16))
        self.queue_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.empty_lbl = ctk.CTkLabel(self.queue_frame, text="No downloads yet.",
                                      text_color=("gray50", "gray50"))
        self.empty_lbl.grid(row=0, column=0, pady=24)

    # -- helpers ------------------------------------------------------------
    def _sync_quality_state(self):
        is_mp3 = self.mode_var.get() == "MP3"
        self.quality_menu.configure(state="disabled" if is_mp3 else "normal")

    def _paste(self):
        try:
            self.url_var.set(self.clipboard_get().strip())
        except Exception:
            pass

    def _choose_folder(self):
        d = fd.askdirectory(initialdir=self.folder_var.get() or str(Path.home()))
        if d:
            self.folder_var.set(d)

    def _on_url_change(self):
        url = self.url_var.get().strip()
        if looks_like_url(url):
            p = detect_platform(url)
            self.platform_lbl.configure(text=f"Platform:  {p}" if p else "")
        else:
            self.platform_lbl.configure(text="")
        self.info_card.grid_remove()
        self._info = None

    # -- info fetch (threaded) ---------------------------------------------
    def _fetch_info(self):
        url = self.url_var.get().strip()
        if not looks_like_url(url):
            self.platform_lbl.configure(text="⚠  That doesn't look like a valid link.")
            return
        self._info_token += 1
        token = self._info_token
        self.fetch_btn.configure(state="disabled", text="…")
        self.info_card.grid(row=0, column=0, sticky="ew", padx=24, pady=(150, 0))
        self.info_title.configure(text="Fetching info…")
        self.info_meta.configure(text="")

        def work():
            try:
                info = extract_info(url, playlist=self.playlist_var.get())
                self.after(0, lambda: self._show_info(info, token))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._info_error(msg, token))

        threading.Thread(target=work, daemon=True).start()

    def _show_info(self, info: MediaInfo, token: int):
        if token != self._info_token:
            return
        self._info = info
        self.fetch_btn.configure(state="normal", text="Fetch info")
        self.info_title.configure(text=info.title)
        if info.is_playlist:
            meta = f"📃 Playlist · {info.entry_count} videos · {info.uploader}"
        else:
            bits = [f"⏱ {info.duration_str}", f"👁 {info.views_str} views"]
            if info.uploader:
                bits.insert(0, f"📺 {info.uploader}")
            meta = "    ".join(bits)
        self.info_meta.configure(text=meta)

    def _info_error(self, msg: str, token: int):
        if token != self._info_token:
            return
        self.fetch_btn.configure(state="normal", text="Fetch info")
        self.info_title.configure(text="Couldn't fetch info")
        from ...core.downloader import _friendly_error
        self.info_meta.configure(text=_friendly_error(msg))

    # -- queue a download ---------------------------------------------------
    def _start_download(self):
        url = self.url_var.get().strip()
        if not looks_like_url(url):
            self.platform_lbl.configure(text="⚠  Enter a valid link first.")
            return
        job = DownloadJob(
            url=url,
            platform=detect_platform(url),
            mode=self.mode_var.get(),
            quality=self.quality_var.get(),
            download_dir=self.folder_var.get() or self.s.get("download_dir"),
            naming=self.s.get("naming", "title"),
            write_thumbnail=self.thumb_var.get(),
            write_subtitles=self.subs_var.get(),
            embed_metadata=self.s.get("embed_metadata", True),
            is_playlist=self.playlist_var.get(),
            title=self._info.title if self._info else "",
        )
        if self.empty_lbl.winfo_ismapped():
            self.empty_lbl.grid_remove()
        card = JobCard(self.queue_frame, job, self.manager)
        card.grid(row=len(self._cards), column=0, sticky="ew", pady=5, padx=4)
        self._cards[id(job)] = card
        self.manager.enqueue(job)
        # persist last-used dir
        self.s["download_dir"] = job.download_dir
        settings_store.save(self.s)

    def _on_job_update(self, job: DownloadJob):
        # called from worker thread -> marshal to UI thread
        self.after(0, lambda: self._apply_update(job))

    def _apply_update(self, job: DownloadJob):
        card = self._cards.get(id(job))
        if card:
            card.refresh()
        if job.status == "done":
            history_store.add(job.title or job.url, job.url, job.platform,
                              job.mode, job.filepath)


class JobCard(ctk.CTkFrame):
    """One row in the queue: title, progress bar, status, cancel/open buttons."""

    def __init__(self, master, job: DownloadJob, manager: DownloadManager):
        super().__init__(master, corner_radius=8)
        self.job = job
        self.manager = manager
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self, text=job.title or job.url, anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"), wraplength=560, justify="left")
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))

        self.sub_lbl = ctk.CTkLabel(self, text=self._subtitle(), anchor="w",
                                    text_color=("gray40", "gray60"),
                                    font=ctk.CTkFont(size=11))
        self.sub_lbl.grid(row=1, column=0, sticky="w", padx=12)

        self.bar = ctk.CTkProgressBar(self)
        self.bar.set(0)
        self.bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 10))

        self.action_btn = ctk.CTkButton(self, text="Cancel", width=80, fg_color="gray30",
                                        hover_color="#b91c1c", command=self._cancel)
        self.action_btn.grid(row=0, column=1, rowspan=3, padx=12)

    def _subtitle(self) -> str:
        tag = f"{self.job.platform} · {self.job.mode}"
        if self.job.mode == "Video":
            tag += f" · {self.job.quality}"
        return tag

    def refresh(self):
        job = self.job
        self.bar.set(job.progress)
        if job.title and self.title_lbl.cget("text") != job.title:
            self.title_lbl.configure(text=job.title)
        status_map = {
            "queued": ("⏳ Queued", "gray"),
            "downloading": (
                f"⬇ {job.progress*100:.0f}%   {job.speed}   ETA {job.eta}".strip(),
                None),
            "done": ("✅ Completed", "#16a34a"),
            "error": (f"❌ {job.message}", "#dc2626"),
            "cancelled": ("🚫 Cancelled", "#9ca3af"),
        }
        text, color = status_map.get(job.status, (job.status, None))
        if job.status == "downloading" and job.message == "Processing…":
            text = "⚙ Processing…"
        self.sub_lbl.configure(text=text, text_color=color or ("gray40", "gray60"))

        if job.status in ("done", "error", "cancelled"):
            if job.status == "done":
                self.action_btn.configure(text="Open", fg_color="#16a34a",
                                          hover_color="#15803d", command=self._open)
            else:
                self.action_btn.configure(state="disabled")
            self.bar.configure(progress_color="#16a34a" if job.status == "done" else "gray40")

    def _cancel(self):
        self.manager.cancel(self.job)

    def _open(self):
        import subprocess
        import sys
        path = self.job.filepath
        folder = str(Path(path).parent) if path else self.job.download_dir
        try:
            if sys.platform == "win32":
                import os
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception:
            pass
