"""
Cryptographic and integrity hash calculation engine (CRC32, MD5, SHA-1, SHA-256, SHA-512).
"""
import hashlib
import zlib
import os
from typing import Dict, Any


class HashEngine:
    """Calculates and verifies multi-algorithm hashes for files and byte streams."""

    SUPPORTED_ALGOS = ["CRC32", "MD5", "SHA-1", "SHA-256", "SHA-512"]

    @staticmethod
    def calculate_hashes(file_path: str) -> Dict[str, str]:
        """Calculates CRC32, MD5, SHA-1, SHA-256, SHA-512 for a given file."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()
        crc = 0

        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
                sha512.update(chunk)
                crc = zlib.crc32(chunk, crc)

        crc32_hex = f"{crc & 0xFFFFFFFF:08X}"
        return {
            "CRC32": crc32_hex,
            "MD5": md5.hexdigest().upper(),
            "SHA-1": sha1.hexdigest().upper(),
            "SHA-256": sha256.hexdigest().upper(),
            "SHA-512": sha512.hexdigest().upper(),
        }

    @staticmethod
    def compare_hash(expected_hash: str, computed_hashes: Dict[str, str]) -> Dict[str, Any]:
        """Compares an expected hash against computed hashes and detects the matched algorithm."""
        clean_exp = expected_hash.strip().upper()
        detected_algo = None
        matched = False

        length_map = {
            8: "CRC32",
            32: "MD5",
            40: "SHA-1",
            64: "SHA-256",
            128: "SHA-512"
        }
        detected_algo = length_map.get(len(clean_exp))

        for algo, val in computed_hashes.items():
            if val.upper() == clean_exp:
                matched = True
                detected_algo = algo
                break

        return {
            "matched": matched,
            "detected_algo": detected_algo,
            "expected": clean_exp
        }
