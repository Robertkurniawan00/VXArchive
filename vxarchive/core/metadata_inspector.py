"""
Deep file metadata, EXIF, and binary header inspector.
"""
import os
from typing import Dict, Any
from .utils import format_size


class MetadataInspector:
    """Inspects file payloads and extracts human-readable properties."""

    @staticmethod
    def inspect(filename: str, data: bytes) -> Dict[str, str]:
        meta: Dict[str, str] = {
            "Filename": os.path.basename(filename),
            "File Size": f"{len(data)} bytes ({format_size(len(data))})"
        }

        ext = os.path.splitext(filename)[1].lower()

        if ext in (".txt", ".py", ".md", ".json", ".html", ".css", ".js", ".c", ".cpp", ".h"):
            meta["Category"] = "Text / Source Code"
            try:
                text = data.decode("utf-8", errors="ignore")
                lines = text.splitlines()
                meta["Total Lines"] = str(len(lines))
                meta["Encoding"] = "UTF-8 (Detected)"
            except Exception:
                meta["Total Lines"] = "Unknown"
        elif ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
            meta["Category"] = "Raster Image"
            if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
                import struct
                w, h = struct.unpack(">II", data[16:24])
                meta["Dimensions"] = f"{w} x {h} px"
        elif ext in (".exe", ".dll"):
            meta["Category"] = "Windows Executable Binary"
            if data.startswith(b"MZ"):
                meta["PE Header"] = "Valid DOS/NT Portable Executable"
        else:
            meta["Category"] = "Binary Payload"

        return meta
