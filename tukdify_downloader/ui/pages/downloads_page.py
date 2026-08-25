"""Downloads page: 4-step simplified workflow, metadata inspector, advanced drawer, and queue."""
from __future__ import annotations

import io
import os
import threading
import urllib.request
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw

from ...core import history as history_store
from ...core import settings as settings_store
from ...core.downloader import DownloadJob, MediaInfo, extract_info
from ...core.manager import DownloadManager
from ...core.platforms import detect_platform, looks_like_url
from .. import theme as t
from ..dialogs import Tooltip, choose_directory, reveal_in_file_manager, short_path

PRIMARY_MODES = ["Best Video (4K/1440p)", "1080p Full HD", "MP3 Audio (320k)"]
ALL_QUALITIES = ["Best", "4K (2160p)", "1440p (2K)", "1080p", "720p", "480p", "360p"]
SUBTITLE_LANGS = ["English (en)", "Spanish (es)", "French (fr)", "German (de)", "Hindi (hi)", "Japanese (ja)", "All Available"]
THUMB_SIZE = (176, 99)   # 16:9 preview
URL_PLACEHOLDER = "Paste any video or playlist link (YouTube, TikTok, Instagram, X, Twitch)…"


class DownloadsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.s = app.settings
        self._info: MediaInfo | None = None
        self._info_token = 0
        self._thumb_img = None
        self.manager = DownloadManager(on_update=self._on_job_update)
        self._cards: dict[str, "JobCard"] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_composer()
        self._build_queue()

    # ======================================================================
    # Composer (4-Step Main Ingestion Flow)
    # ======================================================================
    def _build_composer(self):
        host = ctk.CTkFrame(self, fg_color="transparent")
        host.grid(row=0, column=0, sticky="ew")
        col = t.center_column(host)
        r = 0

        # Step Indicator Header
        head_row = ctk.CTkFrame(col, fg_color="transparent")
        head_row.grid(row=r, column=0, sticky="ew", pady=(20, 8)); r += 1
        ctk.CTkLabel(head_row, text="New Download", font=t.font(16, "bold"),
                     text_color=t.TEXT).pack(side="left")
        self.platform_lbl = ctk.CTkLabel(head_row, text="", font=t.font(12, "bold"),
                                         text_color=t.CYAN)
        self.platform_lbl.pack(side="right")

        # --- STEP 1: URL Composer Bar -------------------------------------
        bar = ctk.CTkFrame(col, fg_color=t.INPUT_BG, corner_radius=12,
                           border_width=1, border_color=t.BORDER)
        bar.grid(row=r, column=0, sticky="ew"); r += 1
        bar.grid_columnconfigure(0, weight=1)

        self._ph_active = False
        self.url_entry = ctk.CTkEntry(
            bar, height=44, border_width=0, fg_color="transparent",
            font=t.font(14), text_color=t.TEXT,
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(16, 6), pady=6)
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)
        self.url_entry.bind("<KeyRelease>", lambda _e: self._on_url_change())
        self.url_entry.bind("<Return>", lambda _e: self._fetch_info())
        self._show_placeholder()

        t.ghost_button(bar, text="Paste", width=68, height=34,
                       command=self._paste).grid(row=0, column=1, padx=4, pady=6)
        self.fetch_btn = t.cyan_button(bar, text="Analyze", width=92, height=34,
                                       command=self._fetch_info)
        self.fetch_btn.grid(row=0, column=2, padx=(4, 6), pady=6)

        # --- STEP 2: Metadata Hero Preview Card ---------------------------
        self.info_card = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=14,
                                      border_width=1, border_color=t.BORDER)
        self.info_card.grid_columnconfigure(1, weight=1)
        self._info_row = r
        self.thumb_lbl = ctk.CTkLabel(self.info_card, text="", width=THUMB_SIZE[0],
                                      height=THUMB_SIZE[1], fg_color=t.INPUT_BG,
                                      corner_radius=10)
        self.thumb_lbl.grid(row=0, column=0, rowspan=3, padx=14, pady=14)

        self.info_title = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                       font=t.font(15, "bold"), text_color=t.TEXT,
                                       justify="left", wraplength=460)
        self.info_title.grid(row=0, column=1, sticky="w", padx=(2, 16), pady=(14, 0))

        self.info_channel = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                         font=t.font(12), text_color=t.TEXT_MUTED)
        self.info_channel.grid(row=1, column=1, sticky="w", padx=(2, 16), pady=(2, 0))

        self.info_meta = ctk.CTkLabel(self.info_card, text="", anchor="w",
                                      font=t.font(12, "bold"), text_color=t.CYAN)
        self.info_meta.grid(row=2, column=1, sticky="w", padx=(2, 16), pady=(4, 14))
        r += 1

        # --- STEP 3: Primary 3-Choice Format Selector --------------------
        self.selector_frame = ctk.CTkFrame(col, fg_color="transparent")
        self.selector_frame.grid(row=r, column=0, sticky="ew", pady=(14, 0)); r += 1
        self.selector_frame.grid_columnconfigure(0, weight=1)

        self.primary_mode_var = ctk.StringVar(value="1080p Full HD")
        self.format_pill = ctk.CTkSegmentedButton(
            self.selector_frame, values=PRIMARY_MODES, height=38,
            variable=self.primary_mode_var, font=t.font(13, "bold"),
            command=lambda _: self._update_cta_label(),
        )
        t.style_segmented(self.format_pill)
        self.format_pill.grid(row=0, column=0, sticky="ew")

        # --- STEP 4: Primary Download CTA Button -------------------------
        self.download_btn = t.primary_button(
            col, text="Download 1080p Video", height=50,
            command=self._start_download, font=t.font(15, "bold"),
        )
        self.download_btn.grid(row=r, column=0, sticky="ew", pady=(14, 8)); r += 1

        # --- Collapsible Advanced Options Drawer ▾ -----------------------
        self.adv_toggle_btn = ctk.CTkButton(
            col, text="Advanced Options ▾", fg_color="transparent",
            hover_color=t.CARD_HOVER, text_color=t.TEXT_MUTED, font=t.font(12),
            height=26, command=self._toggle_advanced_drawer,
        )
        self.adv_toggle_btn.grid(row=r, column=0, pady=(0, 10)); r += 1

        self.adv_drawer = ctk.CTkFrame(col, fg_color=t.CARD_BG, corner_radius=12,
                                       border_width=1, border_color=t.BORDER)
        self.adv_drawer.grid_columnconfigure((0, 1), weight=1)
        self._adv_row = r
        self._adv_expanded = False
        self._build_advanced_drawer_content()

    def _build_advanced_drawer_content(self):
        d = self.adv_drawer
        # Row 1: Specific Quality & Subtitles
        q_box = ctk.CTkFrame(d, fg_color="transparent")
        q_box.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="w")
        ctk.CTkLabel(q_box, text="Resolution Override", font=t.font(11, "bold"),
                     text_color=t.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.custom_quality_var = ctk.StringVar(value=self.s.get("default_quality", "Best"))
        self.custom_quality_menu = ctk.CTkOptionMenu(q_box, values=ALL_QUALITIES, height=32,
                                                     variable=self.custom_quality_var, width=160)
        t.style_optionmenu(self.custom_quality_menu)
        self.custom_quality_menu.pack(anchor="w")

        sub_box = ctk.CTkFrame(d, fg_color="transparent")
        sub_box.grid(row=0, column=1, padx=16, pady=(12, 6), sticky="w")
        ctk.CTkLabel(sub_box, text="Subtitles Language", font=t.font(11, "bold"),
                     text_color=t.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.sub_lang_var = ctk.StringVar(value="English (en)")
        self.sub_menu = ctk.CTkOptionMenu(sub_box, values=SUBTITLE_LANGS, height=32,
                                          variable=self.sub_lang_var, width=160)
        t.style_optionmenu(self.sub_menu)
        self.sub_menu.pack(anchor="w")

        # Row 2: Extras Checkboxes
        extras = ctk.CTkFrame(d, fg_color="transparent")
        extras.grid(row=1, column=0, columnspan=2, padx=16, pady=6, sticky="w")
        self.thumb_var = ctk.BooleanVar(value=self.s.get("write_thumbnail", False))
        self.subs_var = ctk.BooleanVar(value=self.s.get("write_subtitles", False))
        self.meta_var = ctk.BooleanVar(value=self.s.get("embed_metadata", True))

        for txt, var in (("Save Thumbnail", self.thumb_var),
                         ("Download Subtitles", self.subs_var),
                         ("Embed Chapters & Tags", self.meta_var)):
            ctk.CTkCheckBox(extras, text=txt, variable=var, font=t.font(12),
                            checkbox_width=18, checkbox_height=18, corner_radius=4,
                            fg_color=t.ACCENT, text_color=t.TEXT).pack(side="left", padx=(0, 16))

        # Row 3: Destination Folder
        loc_row = ctk.CTkFrame(d, fg_color="transparent")
        loc_row.grid(row=2, column=0, columnspan=2, padx=16, pady=(6, 14), sticky="ew")
        loc_row.grid_columnconfigure(0, weight=1)

        self.folder_var = ctk.StringVar(value=self.s.get("download_dir"))
        self.folder_lbl = ctk.CTkLabel(loc_row, text=self._folder_text(),
                                       font=t.font(12), text_color=t.TEXT_MUTED, anchor="w")
        self.folder_lbl.grid(row=0, column=0, sticky="w")
        Tooltip(self.folder_lbl, lambda: self.folder_var.get())
        t.ghost_button(loc_row, text="Change Folder", width=110, height=28,
                       command=self._choose_folder).grid(row=0, column=1, padx=(8, 0), sticky="e")

    def _toggle_advanced_drawer(self):
        self._adv_expanded = not self._adv_expanded
        if self._adv_expanded:
            self.adv_drawer.grid(row=self._adv_row, column=0, sticky="ew", pady=(0, 12))
            self.adv_toggle_btn.configure(text="Advanced Options ▴")
        else:
            self.adv_drawer.grid_remove()
            self.adv_toggle_btn.configure(text="Advanced Options ▾")

    def _update_cta_label(self):
        mode = self.primary_mode_var.get()
        if "MP3" in mode:
            self.download_btn.configure(text="Download MP3 Audio (320k)")
        elif "4K" in mode:
            self.download_btn.configure(text="Download Best Video (4K/1440p)")
        else:
            self.download_btn.configure(text="Download 1080p Video")

    # ======================================================================
    # Queue Panel
    # ======================================================================
    def _build_queue(self):
        host = ctk.CTkFrame(self, fg_color="transparent")
        host.grid(row=1, column=0, sticky="nsew")
        host.grid_rowconfigure(1, weight=1)
        host.grid_columnconfigure(0, weight=1)

        head = t.center_column(host, row=0)
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text="Download Queue", font=t.font(14, "bold"),
                     text_color=t.TEXT).grid(row=0, column=0, sticky="w", pady=(10, 8))
        self.clear_btn = ctk.CTkButton(head, text="Cancel all", width=84, height=26,
                                       fg_color="transparent", hover_color=t.CARD_HOVER,
                                       text_color=t.TEXT_MUTED, font=t.font(11),
                                       command=self.manager.cancel_all)
        self.clear_btn.grid(row=0, column=1, sticky="e", pady=(10, 8))

        scroll_host = ctk.CTkFrame(host, fg_color="transparent")
        scroll_host.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scroll_host.grid_rowconfigure(0, weight=1)
        scroll_host.grid_columnconfigure(0, weight=1)
        self.queue_scroll = ctk.CTkScrollableFrame(scroll_host, fg_color="transparent")
        self.queue_scroll.grid(row=0, column=0, sticky="nsew")
        self.queue_scroll.grid_columnconfigure(0, weight=1)
        self.queue_frame = t.center_column(self.queue_scroll, gutter=8)

        self.empty_lbl = ctk.CTkLabel(self.queue_frame,
                                      text="No downloads in queue.\nPaste any video link above to get started.",
                                      font=t.font(13), text_color=t.TEXT_FAINT,
                                      justify="center")
        self.empty_lbl.grid(row=0, column=0, pady=32)

    # ======================================================================
    # Helpers & URL Ingestion
    # ======================================================================
    def _folder_text(self) -> str:
        return f"📁  Save to: {short_path(self.folder_var.get() or str(Path.home()))}"

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
            self.platform_lbl.configure(text=f"● {p}" if p else "")
        else:
            self.platform_lbl.configure(text="")
        self.info_card.grid_remove()
        self._info = None

    # -- info fetch (threaded) ---------------------------------------------
    def _fetch_info(self):
        url = self._url_get()
        if not looks_like_url(url):
            self.platform_lbl.configure(text="⚠ Invalid link", text_color=t.ERR)
            return
        self._info_token += 1
        token = self._info_token
        self.fetch_btn.configure(state="disabled", text="…")
        self.info_card.grid(row=self._info_row, column=0, sticky="ew", pady=(12, 0))
        self.info_title.configure(text="Analyzing media streams…")
        self.info_channel.configure(text="")
        self.info_meta.configure(text="")
        self._thumb_img = None
        try:
            self.thumb_lbl.configure(image=None, text="", fg_color=t.INPUT_BG)
        except Exception:
            pass

        def work():
            try:
                info = extract_info(url, playlist=False)
                self.after(0, lambda: self._show_info(info, token))
                if info.thumbnail:
                    self._fetch_thumb(info.thumbnail, token)
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._info_error(msg, token))

        threading.Thread(target=work, daemon=True).start()

    def _fetch_thumb(self, url: str, token: int):
        if not url.startswith("http://") and not url.startswith("https://"):
            return
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img = self._fit_cover(img, THUMB_SIZE)
            self.after(0, lambda: self._set_thumb(img, token))
        except Exception:
            pass

    @staticmethod
    def _fit_cover(img, size):
        tw, th = size
        sw, sh = img.size
        scale = max(tw / sw, th / sh)
        img = img.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
        left = (img.width - tw) // 2
        top = (img.height - th) // 2
        img = img.crop((left, top, left + tw, top + th))
        mask = Image.new("L", size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, th - 1], radius=8, fill=255)
        img.putalpha(mask)
        return img

    def _set_thumb(self, img, token: int):
        if token != self._info_token:
            return
        try:
            self._thumb_img = ctk.CTkImage(light_image=img, dark_image=img, size=THUMB_SIZE)
            self.thumb_lbl.configure(image=self._thumb_img, text="", fg_color="transparent")
        except Exception:
            pass

    def _show_info(self, info: MediaInfo, token: int):
        if token != self._info_token:
            return
        self._info = info
        self.fetch_btn.configure(state="normal", text="Analyze")
        self.info_title.configure(text=info.title)
        self.info_channel.configure(text=info.uploader or "Unknown Creator")
        
        if info.is_playlist:
            meta = f"Playlist · {info.entry_count} Videos"
            # If playlist, offer to open Playlist Picker
            PlaylistPickerModal(self, info, self._on_playlist_download)
        else:
            bits = [f"⏱ {info.duration_str}"]
            if info.view_count:
                bits.append(f"👁 {info.views_str} views")
            if info.qualities:
                bits.append(f"⚡ {info.qualities[0]}")
            meta = "    ·    ".join(bits)
        self.info_meta.configure(text=meta)

    def _info_error(self, msg: str, token: int):
        if token != self._info_token:
            return
        self.fetch_btn.configure(state="normal", text="Analyze")
        self.thumb_lbl.configure(image=None, text="⚠️", font=t.font(20))
        self.info_title.configure(text="Stream Extraction Failed")
        self.info_channel.configure(text="")
        from ...core.downloader import _friendly_error
        self.info_meta.configure(text=_friendly_error(msg))

    def _on_playlist_download(self, items: list[dict], quality: str):
        for item in items:
            url = item.get("url") or item.get("webpage_url")
            if url:
                self._queue_item(url=url, title=item.get("title", ""), quality=quality)

    # -- queue a download ---------------------------------------------------
    def _start_download(self):
        url = self._url_get()
        if not looks_like_url(url):
            self.platform_lbl.configure(text="⚠️ Enter a valid link first", text_color=t.ERR)
            return

        mode_str = self.primary_mode_var.get()
        if "MP3" in mode_str:
            mode = "MP3"
            qual = "320k"
        elif "4K" in mode_str:
            mode = "Video"
            qual = "Best"
        else:
            mode = "Video"
            qual = "1080p"

        # Check if user overrode quality in advanced drawer
        if self._adv_expanded and self.custom_quality_var.get():
            qual = self.custom_quality_var.get().split()[0]

        self._queue_item(
            url=url,
            title=self._info.title if self._info else "",
            mode=mode,
            quality=qual,
        )

    def _queue_item(self, url: str, title: str = "", mode: str = "Video", quality: str = "1080p"):
        job = DownloadJob(
            url=url,
            platform=detect_platform(url),
            mode=mode,
            quality=quality,
            download_dir=self.folder_var.get() or self.s.get("download_dir"),
            naming=self.s.get("naming", "title"),
            write_thumbnail=self.thumb_var.get(),
            write_subtitles=self.subs_var.get(),
            subtitles_lang=self.sub_lang_var.get().split("(")[-1].replace(")", "").strip(),
            embed_metadata=self.meta_var.get(),
            title=title,
        )
        if self.empty_lbl.winfo_ismapped():
            self.empty_lbl.grid_remove()

        card = JobCard(self.queue_frame, job, self.manager)
        card.grid(row=len(self._cards), column=0, sticky="ew", pady=6)
        self._cards[job.id] = card
        self.manager.enqueue(job)

        # Persist last-used directory
        self.s["download_dir"] = job.download_dir
        settings_store.save(self.s)

    def _on_job_update(self, job: DownloadJob):
        self.after(0, lambda: self._apply_update(job))

    def _apply_update(self, job: DownloadJob):
        card = self._cards.get(job.id)
        if card:
            card.refresh()
        if job.status == "done":
            history_store.add(
                title=job.title or job.url,
                url=job.url,
                platform=job.platform,
                mode=job.mode,
                filepath=job.filepath,
                quality=job.quality,
            )


class JobCard(ctk.CTkFrame):
    """One compact card in the queue: title, progress, speed/ETA, actions, and ecosystem pills."""

    def __init__(self, master, job: DownloadJob, manager: DownloadManager):
        super().__init__(master, fg_color=t.CARD_BG, corner_radius=12,
                         border_width=1, border_color=t.BORDER)
        self.job = job
        self.manager = manager
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self, text=job.title or job.url, anchor="w", text_color=t.TEXT,
            font=t.font(13, "bold"), wraplength=460, justify="left")
        self.title_lbl.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))

        # Action button on top right
        self.action_btn = ctk.CTkButton(self, text="Cancel", width=76, height=28,
                                        fg_color="transparent", border_width=1,
                                        border_color=t.BORDER, text_color=t.TEXT_MUTED,
                                        hover_color=t.ERR, font=t.font(11, "bold"),
                                        command=self._cancel)
        self.action_btn.grid(row=0, column=1, padx=(8, 16), pady=(12, 0), sticky="e")

        # Progress bar (Technical Cyan)
        self.bar = ctk.CTkProgressBar(self, height=6, corner_radius=3,
                                      progress_color=t.CYAN)
        self.bar.set(0)
        self.bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(8, 6))

        # Status & Metrics Row
        self.status_row = ctk.CTkFrame(self, fg_color="transparent")
        self.status_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 10))
        self.status_row.grid_columnconfigure(0, weight=1)

        self.status_lbl = ctk.CTkLabel(self.status_row, text="Queued", anchor="w",
                                       text_color=t.TEXT_MUTED, font=t.font(11))
        self.status_lbl.grid(row=0, column=0, sticky="w")

        self.detail_lbl = ctk.CTkLabel(self.status_row, text=self._tag(), anchor="e",
                                       text_color=t.TEXT_MUTED, font=t.mono_font(11))
        self.detail_lbl.grid(row=0, column=1, sticky="e")

        # Ecosystem action row (hidden until finished)
        self.eco_row = ctk.CTkFrame(self, fg_color="transparent")
        self.eco_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 10))
        self.eco_row.grid_remove()

        t.violet_button(self.eco_row, text="✂  Edit in Tukdify Clips", height=26,
                        command=self._open_in_clips).pack(side="left", padx=(0, 8))
        t.ghost_button(self.eco_row, text="⚡  Compress", height=26, width=90,
                       command=self._open_in_multicompressor).pack(side="left")

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
            self.status_lbl.configure(text="Queued in line…", text_color=t.TEXT_MUTED)
            self.detail_lbl.configure(text=self._tag())
        elif job.status == "downloading":
            if job.message == "Processing…":
                self.status_lbl.configure(text="Merging streams with FFmpeg…", text_color=t.WARN)
                self.detail_lbl.configure(text="")
            else:
                self.status_lbl.configure(
                    text=f"Downloading · {job.progress * 100:.0f}%", text_color=t.TEXT)
                bits = [b for b in (job.speed, f"ETA {job.eta}" if job.eta else "") if b]
                self.detail_lbl.configure(text="   ·   ".join(bits))
        elif job.status == "done":
            self.status_lbl.configure(text="✓  Download Completed", text_color=t.OK)
            self.detail_lbl.configure(text="")
            self.bar.configure(progress_color=t.OK)
            self.action_btn.configure(text="Reveal", fg_color=t.ACCENT, border_width=0,
                                      text_color=t.ON_ACCENT, hover_color=t.ACCENT_HOVER,
                                      command=self._reveal)
            self.eco_row.grid()
        elif job.status == "error":
            self.status_lbl.configure(text=f"⚠️  {job.message}", text_color=t.ERR)
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

    def _reveal(self):
        reveal_in_file_manager(self.job.filepath or self.job.download_dir)

    def _open_in_clips(self):
        webbrowser.open("https://github.com/Tukdify/Tukdify-clips")

    def _open_in_multicompressor(self):
        webbrowser.open("https://github.com/Tukdify/Tukdify-Multicompressor")


class PlaylistPickerModal(ctk.CTkToplevel):
    """Interactive modal allowing users to inspect and select specific playlist videos."""

    def __init__(self, master, info: MediaInfo, on_download: Callable[[list[dict], str], None]):
        super().__init__(master)
        self.info = info
        self.on_download = on_download
        self.title("Select Playlist Videos - Tukdify")
        self.geometry("560x620")
        self.configure(fg_color=t.APP_BG)
        self.attributes("-topmost", True)
        self.transient(master)
        self.after(50, self._safe_focus_and_grab)

        self._checks: list[tuple[dict, ctk.BooleanVar]] = []
        self._build_ui()

    def _safe_focus_and_grab(self):
        try:
            if self.winfo_exists():
                self.focus()
                self.grab_set()
        except Exception:
            pass

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(header, text=self.info.title, font=t.font(16, "bold"),
                     text_color=t.TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text=f"{self.info.entry_count} Videos found in playlist",
                     font=t.font(12, "bold"), text_color=t.ACCENT).pack(anchor="w")

        # Toolbar
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(4, 8))
        t.ghost_button(bar, text="Select All", width=80, height=28,
                       command=self._select_all).pack(side="left", padx=(0, 6))
        t.ghost_button(bar, text="Clear All", width=80, height=28,
                       command=self._clear_all).pack(side="left")

        # Scrollable items
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        for i, entry in enumerate(self.info.entries):
            row = ctk.CTkFrame(scroll, fg_color=t.CARD_BG, corner_radius=8,
                               border_width=1, border_color=t.BORDER)
            row.pack(fill="x", pady=3)
            row.grid_columnconfigure(1, weight=1)

            var = ctk.BooleanVar(value=True)
            self._checks.append((entry, var))

            ctk.CTkCheckBox(row, text="", variable=var, width=20, height=20,
                            fg_color=t.ACCENT, corner_radius=4).grid(row=0, column=0, padx=(10, 6), pady=8)
            title = entry.get("title") or f"Video {i+1}"
            ctk.CTkLabel(row, text=title, font=t.font(12, "bold"), text_color=t.TEXT,
                         anchor="w", wraplength=400, justify="left").grid(row=0, column=1, sticky="w", pady=8)

        # Footer CTA
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=16)
        t.primary_button(footer, text="Download Selected Videos", height=42,
                         command=self._submit).pack(fill="x")

    def _select_all(self):
        for _, var in self._checks:
            var.set(True)

    def _clear_all(self):
        for _, var in self._checks:
            var.set(False)

    def _submit(self):
        selected = [entry for entry, var in self._checks if var.get()]
        self.destroy()
        if selected:
            self.on_download(selected, "1080p")

