"""Downloads page: paste a URL, preview info, set options, queue downloads."""
from __future__ import annotations

import io
import threading
import urllib.request
from pathlib import Path

import customtkinter as ctk

from ...core import history as history_store
from ...core import settings as settings_store
from ...core.downloader import DownloadJob, MediaInfo, extract_info
from ...core.manager import DownloadManager
from ...core.platforms import detect_platform, looks_like_url
from .. import theme as t
from ..dialogs import Tooltip, choose_directory, short_path

QUALITIES = ["Best", "1080p", "720p", "480p", "360p"]
MODES = ["Video", "MP3"]
THUMB_SIZE = (168, 94)   # 16:9 preview
URL_PLACEHOLDER = "Paste a video URL here — YouTube, Instagram, TikTok and more…"


class DownloadsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.s = app.settings
        self._info: MediaInfo | None = None
        self._info_token = 0
        self._thumb_img = None      # keep a ref so Tk doesn't GC the image
        self.manager = DownloadManager(on_update=self._on_job_update)
        self._cards: dict[int, "JobCard"] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_composer()
        self._build_queue()

    # ======================================================================
    # Composer (URL → info → options → location → download)
    # ======================================================================
    def _build_composer(self):
        host = ctk.CTkFrame(self, fg_color="transparent")
        host.grid(row=0, column=0, sticky="ew")
        col = t.center_column(host)
        r = 0

        ctk.CTkLabel(col, text="New download", font=t.font(13, "bold"),
                     text_color=t.TEXT_MUTED).grid(row=r, column=0, sticky="w",
                                                   pady=(26, 10)); r += 1

        # --- URL bar: entry + paste + fetch, all in one rounded input ------
        bar = ctk.CTkFrame(col, fg_color=t.INPUT_BG, corner_radius=14,
                           border_width=1, border_color=t.BORDER)
        bar.grid(row=r, column=0, sticky="ew"); r += 1
        bar.grid_columnconfigure(0, weight=1)

        # Manual placeholder: CTkEntry's built-in placeholder is unreliable when
        # a textvariable is attached, so we manage hint text on focus ourselves.
        self._ph_active = False
        self.url_entry = ctk.CTkEntry(
            bar, height=44, border_width=0, fg_color="transparent",
            font=t.font(15), text_color=t.TEXT,
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(18, 6), pady=8)
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)
        self.url_entry.bind("<KeyRelease>", lambda _e: self._on_url_change())
        self._show_placeholder()
        t.ghost_button(bar, text="Paste", width=72, height=36,
                       command=self._paste).grid(row=0, column=1, padx=4, pady=8)
        self.fetch_btn = t.primary_button(bar, text="Fetch info", width=104, height=36,
                                          font=t.font(13, "bold"), command=self._fetch_info)
        self.fetch_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        self.platform_lbl = ctk.CTkLabel(col, text="", font=t.font(12),
                                         text_color=t.TEXT_MUTED, anchor="w")
        self.platform_lbl.grid(row=r, column=0, sticky="w", padx=4, pady=(6, 0)); r += 1

        # --- Info preview card (hidden until fetched) ----------------------
        self.info_card = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                                      border_width=1, border_color=t.BORDER)
        self.info_card.grid_columnconfigure(1, weight=1)
        self._info_row = r
        self.thumb_lbl = ctk.CTkLabel(self.info_card, text="", width=THUMB_SIZE[0],
                                      height=THUMB_SIZE[1], fg_color=t.INPUT_BG,
                                      corner_radius=10)
        self.thumb_lbl.grid(row=0, column=0, rowspan=3, padx=12, pady=12)
        self.info_title = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                       font=t.font(15, "bold"), text_color=t.TEXT,
                                       justify="left", wraplength=440)
        self.info_title.grid(row=0, column=1, sticky="w", padx=(2, 16), pady=(14, 0))
        self.info_channel = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                         font=t.font(12), text_color=t.TEXT_MUTED)
        self.info_channel.grid(row=1, column=1, sticky="w", padx=(2, 16), pady=(2, 0))
        self.info_meta = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                      font=t.font(12), text_color=t.TEXT_FAINT)
        self.info_meta.grid(row=2, column=1, sticky="w", padx=(2, 16), pady=(6, 14))
        r += 1

        # --- Options row: Type · Quality · Extras (single row) -------------
        opts = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                            border_width=1, border_color=t.BORDER)
        opts.grid(row=r, column=0, sticky="ew", pady=(16, 0)); r += 1
        opts.grid_columnconfigure(2, weight=1)

        type_box = ctk.CTkFrame(opts, fg_color="transparent")
        type_box.grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")
        ctk.CTkLabel(type_box, text="Type", font=t.font(11), text_color=t.TEXT_MUTED
                     ).pack(anchor="w", pady=(0, 4))
        self.mode_var = ctk.StringVar(value=self.s.get("default_mode", "Video"))
        self.mode_menu = ctk.CTkSegmentedButton(type_box, values=MODES, height=34,
                                                variable=self.mode_var, width=150,
                                                command=lambda _: self._sync_quality_state())
        t.style_segmented(self.mode_menu)
        self.mode_menu.pack(anchor="w")

        qual_box = ctk.CTkFrame(opts, fg_color="transparent")
        qual_box.grid(row=0, column=1, padx=8, pady=14, sticky="w")
        ctk.CTkLabel(qual_box, text="Quality", font=t.font(11), text_color=t.TEXT_MUTED
                     ).pack(anchor="w", pady=(0, 4))
        self.quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best"))
        self.quality_menu = ctk.CTkOptionMenu(qual_box, values=QUALITIES, height=34,
                                              width=120, variable=self.quality_var)
        t.style_optionmenu(self.quality_menu)
        self.quality_menu.pack(anchor="w")

        extras_box = ctk.CTkFrame(opts, fg_color="transparent")
        extras_box.grid(row=0, column=2, padx=(8, 16), pady=14, sticky="e")
        ctk.CTkLabel(extras_box, text="Extras", font=t.font(11), text_color=t.TEXT_MUTED
                     ).pack(anchor="w", pady=(0, 4))
        checks = ctk.CTkFrame(extras_box, fg_color="transparent")
        checks.pack(anchor="w")
        self.thumb_var = ctk.BooleanVar(value=self.s.get("write_thumbnail", False))
        self.subs_var = ctk.BooleanVar(value=self.s.get("write_subtitles", False))
        self.playlist_var = ctk.BooleanVar(value=False)
        for txt, var in (("Thumbnail", self.thumb_var), ("Subtitles", self.subs_var),
                         ("Playlist", self.playlist_var)):
            ctk.CTkCheckBox(checks, text=txt, variable=var, font=t.font(12),
                            checkbox_width=18, checkbox_height=18, corner_radius=5,
                            fg_color=t.ACCENT, hover_color=t.ACCENT_HOVER,
                            text_color=t.TEXT).pack(side="left", padx=(0, 14))

        # --- Location row (compact) ----------------------------------------
        loc = ctk.CTkFrame(col, fg_color="transparent")
        loc.grid(row=r, column=0, sticky="ew", pady=(16, 0)); r += 1
        loc.grid_columnconfigure(0, weight=1)
        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        info_wrap = ctk.CTkFrame(loc, fg_color="transparent")
        info_wrap.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_wrap, text="Download location", font=t.font(11),
                     text_color=t.TEXT_MUTED).pack(anchor="w")
        self.folder_lbl = ctk.CTkLabel(info_wrap, text=self._folder_text(),
                                       font=t.font(13), text_color=t.TEXT, anchor="w")
        self.folder_lbl.pack(anchor="w", pady=(1, 0))
        Tooltip(self.folder_lbl, lambda: self.folder_var.get())  # full path on hover
        t.ghost_button(loc, text="Change", width=84, height=34,
                       command=self._choose_folder).grid(row=0, column=1, padx=(8, 0))

        # --- Primary CTA ---------------------------------------------------
        self.download_btn = t.primary_button(col, text="⬇   Download", width=300,
                                             height=52, command=self._start_download)
        self.download_btn.grid(row=r, column=0, pady=(24, 22)); r += 1
        self._sync_quality_state()

    # ======================================================================
    # Queue
    # ======================================================================
    def _build_queue(self):
        host = ctk.CTkFrame(self, fg_color="transparent")
        host.grid(row=1, column=0, sticky="nsew")
        host.grid_rowconfigure(1, weight=1)
        host.grid_columnconfigure(0, weight=1)

        head = t.center_column(host, row=0)
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text="Queue", font=t.font(13, "bold"),
                     text_color=t.TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.clear_btn = ctk.CTkButton(head, text="Cancel all", width=88, height=28,
                                       fg_color="transparent", hover_color=t.CARD_HOVER,
                                       text_color=t.TEXT_MUTED, font=t.font(12),
                                       command=self.manager.cancel_all)
        self.clear_btn.grid(row=0, column=1, sticky="e", pady=(0, 8))

        scroll_host = ctk.CTkFrame(host, fg_color="transparent")
        scroll_host.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)
        self.queue_scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.queue_scroll.grid(row=0, column=0, sticky="nsew")
        self.queue_scroll.grid_columnconfigure(0, weight=1)
        self.queue_frame = t.center_column(self.queue_scroll, gutter=8)

        self.empty_lbl = ctk.CTkLabel(self.queue_frame,
                                      text="Nothing in the queue yet.\nPaste a link above to get started.",
                                      font=t.font(13), text_color=t.TEXT_FAINT,
                                      justify="center")
        self.empty_lbl.grid(row=0, column=0, pady=40)

    # ======================================================================
    # Helpers
    # ======================================================================
    def _folder_text(self) -> str:
        return f"📁  {short_path(self.folder_var.get() or str(Path.home()))}"

    def _sync_quality_state(self):
        is_mp3 = self.mode_var.get() == "MP3"
        self.quality_menu.configure(state="disabled" if is_mp3 else "normal")

    # -- URL field (manual placeholder) ------------------------------------
    def _url_get(self) -> str:
        return "" if self._ph_active else self.url_entry.get().strip()

    def _url_set(self, text: str):
        self._clear_placeholder()
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, text)
        if not text and self.focus_get() is not self.url_entry:
            self._show_placeholder()

    def _show_placeholder(self):
        if not self.url_entry.get():
            self._ph_active = True
            self.url_entry.configure(text_color=t.TEXT_FAINT)
            self.url_entry.insert(0, URL_PLACEHOLDER)

    def _clear_placeholder(self):
        if self._ph_active:
            self._ph_active = False
            self.url_entry.delete(0, "end")
            self.url_entry.configure(text_color=t.TEXT)

    def _on_url_focus_in(self, _evt=None):
        self._clear_placeholder()

    def _on_url_focus_out(self, _evt=None):
        if not self.url_entry.get():
            self._show_placeholder()

    def _paste(self):
        try:
            self._url_set(self.clipboard_get().strip())
            self._on_url_change()
        except Exception:
            pass

    def _choose_folder(self):
        d = choose_directory(self.folder_var.get() or str(Path.home()))
        if d:
            self.folder_var.set(d)
            self.folder_lbl.configure(text=self._folder_text())

    def _on_url_change(self):
        url = self._url_get()
        if looks_like_url(url):
            p = detect_platform(url)
            self.platform_lbl.configure(text=f"Detected: {p}" if p else "")
        else:
            self.platform_lbl.configure(text="")
        self.info_card.grid_remove()
        self._info = None

    # -- info fetch (threaded) ---------------------------------------------
    def _fetch_info(self):
        url = self._url_get()
        if not looks_like_url(url):
            self.platform_lbl.configure(text="⚠  That doesn't look like a valid link.")
            return
        self._info_token += 1
        token = self._info_token
        self.fetch_btn.configure(state="disabled", text="…")
        self.info_card.grid(row=self._info_row, column=0, sticky="ew", pady=(14, 0))
        self.info_title.configure(text="Fetching info…")
        self.info_channel.configure(text="")
        self.info_meta.configure(text="")
        self.thumb_lbl.configure(image=None, text="")
        self._thumb_img = None

        def work():
            try:
                info = extract_info(url, playlist=self.playlist_var.get())
                self.after(0, lambda: self._show_info(info, token))
                if info.thumbnail:
                    self._fetch_thumb(info.thumbnail, token)
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._info_error(msg, token))

        threading.Thread(target=work, daemon=True).start()

    def _fetch_thumb(self, url: str, token: int):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
            from PIL import Image
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img = self._fit_cover(img, THUMB_SIZE)
            self.after(0, lambda: self._set_thumb(img, token))
        except Exception:
            pass

    @staticmethod
    def _fit_cover(img, size):
        """Centre-crop *img* to fill *size* (object-fit: cover) with rounded corners."""
        from PIL import Image, ImageDraw
        tw, th = size
        sw, sh = img.size
        scale = max(tw / sw, th / sh)
        img = img.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
        left = (img.width - tw) // 2
        top = (img.height - th) // 2
        img = img.crop((left, top, left + tw, top + th))
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, th - 1], radius=10, fill=255)
        img.putalpha(mask)
        return img

    def _set_thumb(self, img, token: int):
        if token != self._info_token:
            return
        self._thumb_img = ctk.CTkImage(light_image=img, dark_image=img, size=THUMB_SIZE)
        self.thumb_lbl.configure(image=self._thumb_img, text="", fg_color="transparent")

    def _show_info(self, info: MediaInfo, token: int):
        if token != self._info_token:
            return
        self._info = info
        self.fetch_btn.configure(state="normal", text="Fetch info")
        self.info_title.configure(text=info.title)
        self.info_channel.configure(text=info.uploader or "")
        if info.is_playlist:
            meta = f"📃  Playlist · {info.entry_count} videos"
        else:
            bits = [f"⏱  {info.duration_str}"]
            if info.view_count:
                bits.append(f"👁  {info.views_str} views")
            meta = "      ".join(bits)
        self.info_meta.configure(text=meta)

    def _info_error(self, msg: str, token: int):
        if token != self._info_token:
            return
        self.fetch_btn.configure(state="normal", text="Fetch info")
        self.thumb_lbl.configure(image=None, text="⚠", font=t.font(22))
        self.info_title.configure(text="Couldn't fetch info")
        self.info_channel.configure(text="")
        from ...core.downloader import _friendly_error
        self.info_meta.configure(text=_friendly_error(msg))

    # -- queue a download ---------------------------------------------------
    def _start_download(self):
        url = self._url_get()
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
        card.grid(row=len(self._cards), column=0, sticky="ew", pady=6)
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
    """One compact card in the queue: title, progress, status + speed/ETA, actions."""

    def __init__(self, master, job: DownloadJob, manager: DownloadManager):
        super().__init__(master, fg_color=t.CARD_BG, corner_radius=12,
                         border_width=1, border_color=t.BORDER)
        self.job = job
        self.manager = manager
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self, text=job.title or job.url, anchor="w", text_color=t.TEXT,
            font=t.font(13, "bold"), wraplength=440, justify="left")
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))

        # Action button is vertically centred across the whole card.
        self.action_btn = ctk.CTkButton(self, text="Cancel", width=82, height=32,
                                        fg_color="transparent", border_width=1,
                                        border_color=t.BORDER, text_color=t.TEXT_MUTED,
                                        hover_color=t.ERR, font=t.font(12),
                                        command=self._cancel)
        self.action_btn.grid(row=0, column=1, rowspan=3, padx=(8, 16), sticky="e")

        self.bar = ctk.CTkProgressBar(self, height=6, corner_radius=3,
                                      progress_color=t.ACCENT)
        self.bar.set(0)
        self.bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(10, 8))

        # Status row: state on the left, speed / ETA right-aligned.
        status_row = ctk.CTkFrame(self, fg_color="transparent")
        status_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        status_row.grid_columnconfigure(0, weight=1)
        self.status_lbl = ctk.CTkLabel(status_row, text="Queued", anchor="w",
                                       text_color=t.TEXT_MUTED, font=t.font(12),
                                       wraplength=380, justify="left")
        self.status_lbl.grid(row=0, column=0, sticky="w")
        self.detail_lbl = ctk.CTkLabel(status_row, text=self._tag(), anchor="e",
                                       text_color=t.TEXT_FAINT, font=t.font(11))
        self.detail_lbl.grid(row=0, column=1, sticky="e")

    def _tag(self) -> str:
        tag = f"{self.job.platform} · {self.job.mode}"
        if self.job.mode == "Video":
            tag += f" · {self.job.quality}"
        return tag

    def refresh(self):
        job = self.job
        self.bar.set(job.progress)
        if job.title and self.title_lbl.cget("text") != job.title:
            self.title_lbl.configure(text=job.title)

        if job.status == "queued":
            self.status_lbl.configure(text="Queued", text_color=t.TEXT_MUTED)
            self.detail_lbl.configure(text=self._tag())
        elif job.status == "downloading":
            if job.message == "Processing…":
                self.status_lbl.configure(text="Processing…", text_color=t.TEXT_MUTED)
                self.detail_lbl.configure(text="")
            else:
                self.status_lbl.configure(
                    text=f"Downloading · {job.progress * 100:.0f}%", text_color=t.TEXT)
                bits = [b for b in (job.speed, f"ETA {job.eta}" if job.eta else "") if b]
                self.detail_lbl.configure(text="   ·   ".join(bits))
        elif job.status == "done":
            self.status_lbl.configure(text="✓  Completed", text_color=t.OK)
            self.detail_lbl.configure(text="")
            self.bar.configure(progress_color=t.OK)
            self.action_btn.configure(text="Open", fg_color=t.ACCENT, border_width=0,
                                      text_color=t.ON_ACCENT, hover_color=t.ACCENT_HOVER,
                                      command=self._open)
        elif job.status == "error":
            self.status_lbl.configure(text=f"⚠  {job.message}", text_color=t.ERR)
            self.detail_lbl.configure(text="")
            self.bar.configure(progress_color=t.ERR)
            self.action_btn.configure(text="Failed", state="disabled")
        elif job.status == "cancelled":
            self.status_lbl.configure(text="Cancelled", text_color=t.TEXT_FAINT)
            self.detail_lbl.configure(text="")
            self.bar.configure(progress_color=t.TEXT_FAINT)
            self.action_btn.configure(state="disabled")

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
