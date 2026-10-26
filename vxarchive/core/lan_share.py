"""
Local network HTTP micro-server & QR code generator for instant wireless file sharing.
"""
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Tuple


class LANShareServer:
    """Spins up a lightweight background HTTP server allowing local devices to download an archive."""

    def __init__(self, file_path: str):
        self.file_path = os.path.abspath(file_path)
        self.server: HTTPServer = None
        self.thread: threading.Thread = None
        self.port = 0
        self.is_running = False

    def _get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start(self) -> Tuple[bool, str]:
        if not os.path.isfile(self.file_path):
            return False, "File does not exist"

        file_dir = os.path.dirname(self.file_path)
        filename = os.path.basename(self.file_path)

        class CustomHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=file_dir, **kwargs)

            def log_message(self, format, *args):
                pass  # Quiet logging

        try:
            self.server = HTTPServer(("0.0.0.0", 0), CustomHandler)
            self.port = self.server.server_port
            self.is_running = True

            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()

            ip = self._get_local_ip()
            url = f"http://{ip}:{self.port}/{filename}"
            return True, url
        except Exception as e:
            self.is_running = False
            return False, str(e)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        self.is_running = False
