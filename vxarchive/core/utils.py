"""
Common utility functions, security guards, and path resolution for VXArchive.
"""
import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """Returns the persistent application data directory for VXArchive in %APPDATA% as a Path object."""
    app_data = os.environ.get("APPDATA")
    if not app_data:
        app_data = os.path.expanduser("~")
    p = Path(app_data) / "VXArchive"
    p.mkdir(parents=True, exist_ok=True)
    return p


def format_size(size_bytes: int) -> str:
    """Formats bytes into human-readable strings (B, KB, MB, GB, TB)."""
    if size_bytes is None:
        return "0 B"
    try:
        size = float(size_bytes)
    except (ValueError, TypeError):
        return "0 B"

    if size < 0:
        return "0 B"

    if size < 1024:
        return f"{int(size)} B"

    for unit in ["KB", "MB", "GB", "TB", "PB"]:
        size /= 1024.0
        if size < 1024.0 or unit == "PB":
            return f"{size:.2f} {unit}"

    return f"{size:.2f} PB"


def format_bytes(size_bytes: int) -> str:
    return format_size(size_bytes)


def is_safe_path(base_dir: str, member_path: str) -> bool:
    """
    Prevents Zip Slip / Path Traversal attacks by validating that the resolved
    target file stays strictly inside base_dir.
    """
    if not base_dir or not member_path:
        return False
    base = os.path.abspath(base_dir)
    target = os.path.abspath(os.path.join(base, member_path))
    return target.startswith(base) and (len(target) == len(base) or target[len(base)] == os.sep)


def is_safe_extraction_path(target_dir: str, member_path: str) -> bool:
    return is_safe_path(target_dir, member_path)


def sanitize_filename(name: str) -> str:
    """Sanitizes filename for safe Windows filesystem storage."""
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip(". ")
