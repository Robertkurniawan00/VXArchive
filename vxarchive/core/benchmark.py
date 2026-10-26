"""
Hardware multi-core CPU compression & hashing benchmark engine.
"""
import time
import threading
import zlib
import os


class VXArchiveBenchmark:
    """Measures compression throughput (KB/s, MB/s) and integrity checking speed."""

    def __init__(self, multithreading: bool = True, update_interval: float = 0.1):
        self.multithreading = multithreading
        self.update_interval = update_interval
        self.running = False
        self.total_bytes = 0
        self.errors = 0
        self.start_time = 0.0
        self._threads = []
        self._lock = threading.Lock()

    def _worker(self):
        sample_chunk = b"VXArchiveBenchmarkBlockData_0123456789ABCDEF" * 1024  # 44 KB
        while self.running:
            try:
                comp = zlib.compress(sample_chunk, level=6)
                decomp = zlib.decompress(comp)
                if decomp != sample_chunk:
                    with self._lock:
                        self.errors += 1
                with self._lock:
                    self.total_bytes += len(sample_chunk)
            except Exception:
                with self._lock:
                    self.errors += 1

    def start(self):
        self.running = True
        self.total_bytes = 0
        self.errors = 0
        self.start_time = time.time()

        thread_count = os.cpu_count() or 4 if self.multithreading else 1
        self._threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self):
        self.running = False
        for t in self._threads:
            t.join(timeout=0.5)
        self._threads.clear()

    @property
    def speed_mb_per_sec(self) -> float:
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        return (self.total_bytes / (1024 * 1024)) / elapsed
