"""
Steganographic secret vault: hides and extracts archives embedded within images.
"""
import os
from typing import Tuple


class ArchiveSteganography:
    """Injects and extracts archives hidden after the end-of-image markers (JPEG, PNG, GIF)."""

    MARKERS = {
        b"\x89PNG\r\n\x1a\n": (b"IEND\xaeB`\x82", 8),   # PNG
        b"\xff\xd8\xff": (b"\xff\xd9", 2),               # JPEG
        b"GIF87a": (b"\x00;", 2),                        # GIF
        b"GIF89a": (b"\x00;", 2)
    }

    ZIP_MAGIC = b"PK\x03\x04"
    SEVENZ_MAGIC = b"7z\xbc\xaf\x27\x1c"
    RAR_MAGIC = b"Rar!\x1a\x07"

    @staticmethod
    def hide_archive_in_image(image_path: str, archive_path: str, output_path: str) -> Tuple[bool, str]:
        if not os.path.isfile(image_path):
            return False, "Carrier image file not found"
        if not os.path.isfile(archive_path):
            return False, "Archive payload file not found"

        try:
            with open(image_path, "rb") as fi:
                img_data = fi.read()
            with open(archive_path, "rb") as fa:
                arc_data = fa.read()

            with open(output_path, "wb") as fo:
                fo.write(img_data)
                fo.write(arc_data)

            return True, f"Stego image successfully created at {output_path}"
        except Exception as e:
            return False, f"Failed to hide archive: {str(e)}"

    @staticmethod
    def detect_hidden_archive(file_path: str) -> Tuple[bool, str, int]:
        """Detects if an image contains an appended archive and returns (has_hidden, format, offset)."""
        if not os.path.isfile(file_path):
            return False, "NONE", -1

        try:
            with open(file_path, "rb") as f:
                data = f.read()

            for magic, (end_sig, end_len) in ArchiveSteganography.MARKERS.items():
                if data.startswith(magic):
                    pos = data.rfind(end_sig)
                    if pos != -1:
                        offset = pos + end_len
                        trailer = data[offset:]
                        if trailer.startswith(ArchiveSteganography.ZIP_MAGIC):
                            return True, "ZIP", offset
                        elif trailer.startswith(ArchiveSteganography.SEVENZ_MAGIC):
                            return True, "7Z", offset
                        elif trailer.startswith(ArchiveSteganography.RAR_MAGIC):
                            return True, "RAR", offset
                        elif len(trailer) > 16:
                            return True, "UNKNOWN", offset

            # General search if no standard image header matched
            for sig, fmt in [(ArchiveSteganography.ZIP_MAGIC, "ZIP"),
                             (ArchiveSteganography.SEVENZ_MAGIC, "7Z"),
                             (ArchiveSteganography.RAR_MAGIC, "RAR")]:
                pos = data.find(sig, 64)
                if pos != -1:
                    return True, fmt, pos

            return False, "NONE", -1
        except Exception:
            return False, "NONE", -1

    @staticmethod
    def extract_hidden_archive(carrier_path: str, output_archive_path: str) -> Tuple[bool, str]:
        has_hidden, fmt, offset = ArchiveSteganography.detect_hidden_archive(carrier_path)
        if not has_hidden or offset <= 0:
            return False, "No hidden archive found in carrier file"

        try:
            with open(carrier_path, "rb") as f:
                f.seek(offset)
                payload = f.read()

            with open(output_archive_path, "wb") as f:
                f.write(payload)

            return True, f"Recovered hidden {fmt} archive to {output_archive_path}"
        except Exception as e:
            return False, f"Failed to extract payload: {str(e)}"
