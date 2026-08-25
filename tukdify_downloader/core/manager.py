"""Background queue that runs downloads one at a time off the UI thread."""
from __future__ import annotations

import queue
import threading
from typing import Callable

from .downloader import DownloadJob, Downloader


class DownloadManager:
    """Serial worker: jobs are processed FIFO on a single background thread.

    The *on_update* callback is invoked (from the worker thread) whenever a
    job changes state — the UI is responsible for marshalling back to the
    main thread (CustomTkinter: use ``widget.after``).
    """

    def __init__(self, on_update: Callable[[DownloadJob], None]):
        self.on_update = on_update
        self._q: "queue.Queue[DownloadJob]" = queue.Queue()
        self.jobs: list[DownloadJob] = []
        self._current: DownloadJob | None = None
        self._worker: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self):
        if self._worker and self._worker.is_alive():
            return
        self._stop.clear()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    def enqueue(self, job: DownloadJob):
        self.jobs.append(job)
        self._q.put(job)
        self.on_update(job)
        self.start()

    def cancel(self, job: DownloadJob):
        job.cancel()
        if job.status == "queued":
            job.status = "cancelled"
            job.message = "Cancelled"
            self.on_update(job)

    def cancel_all(self):
        for job in self.jobs:
            if job.status in ("queued", "downloading"):
                self.cancel(job)

    def _loop(self):
        while not self._stop.is_set():
            try:
                job = self._q.get(timeout=0.5)
            except queue.Empty:
                continue
            if job.status == "cancelled":
                continue
            self._current = job
            Downloader(job, self.on_update).run()
            self._current = None
            self._q.task_done()

    def shutdown(self):
        self._stop.set()
        self.cancel_all()
