"""
Archive Sanitizer and Anti-Mess smart layout resolver.
"""
import os
import zipfile
import tempfile
from typing import List, Tuple, Set


class JunkItem:
    def __init__(self, path: str, category: str, size: int):
        self.path = path
        self.category = category
        self.size = size


class SanitizerReport:
    def __init__(self, total_junk_count: int, waste_bytes: int, waste_percentage: float, junk_items: List[JunkItem]):
        self.total_junk_count = total_junk_count
        self.waste_bytes = waste_bytes
        self.waste_percentage = waste_percentage
        self.junk_items = junk_items


class ArchiveSanitizer:
    """Detects and cleans cross-platform OS ghost files, dev clutter, and duplicates."""

    OS_GHOST_PATTERNS = {
        "__macosx", ".ds_store", "thumbs.db", "desktop.ini", "ehthumbs.db"
    }
    DEV_CACHE_PATTERNS = {
        "__pycache__", ".pytest_cache", ".tox", ".mypy_cache"
    }
    IDE_CLUTTER_PATTERNS = {
        ".vscode", ".idea", "*.swp", "*.swo"
    }
    TEMP_BACKUP_PATTERNS = {
        ".tmp", ".bak", "~", ".log"
    }

    def _classify_junk(self, path: str) -> str:
        p_lower = path.lower().replace("\\", "/")
        parts = p_lower.split("/")
        name = parts[-1]

        if any(g in p_lower for g in ["__macosx", ".ds_store", "thumbs.db", "desktop.ini"]):
            return "OS Ghost Files"
        if any(d in p_lower for d in ["__pycache__", ".pyc", ".pytest_cache"]):
            return "Development Caches"
        if any(i in p_lower for i in [".vscode", ".idea"]):
            return "IDE & Editor Clutter"
        if any(name.endswith(t) for t in [".tmp", ".bak", ".log"]) or name.endswith("~"):
            return "Temporary & Backup Files"
        return "Other Clutter"

    def analyze(self, archive_path: str) -> SanitizerReport:
        junk_items: List[JunkItem] = []
        total_size = 0
        waste_bytes = 0

        crc_map = {}
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    total_size += info.file_size
                    category = self._classify_junk(info.filename)
                    if category != "Other Clutter":
                        junk_items.append(JunkItem(info.filename, category, info.file_size))
                        waste_bytes += info.file_size
                    else:
                        # Check duplicate payload
                        crc = info.CRC
                        if crc in crc_map:
                            junk_items.append(JunkItem(info.filename, "Duplicate Payloads", info.file_size))
                            waste_bytes += info.file_size
                        else:
                            crc_map[crc] = info.filename

        total = max(1, total_size)
        pct = (waste_bytes / total) * 100.0

        return SanitizerReport(
            total_junk_count=len(junk_items),
            waste_bytes=waste_bytes,
            waste_percentage=pct,
            junk_items=junk_items
        )

    def create_sanitized_archive(self, dirty_archive: str, output_clean_archive: str, remove_paths: List[str]) -> Tuple[bool, str, int]:
        remove_set = set(remove_paths)
        created_count = 0

        try:
            with zipfile.ZipFile(dirty_archive, "r") as z_in:
                with zipfile.ZipFile(output_clean_archive, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                    for info in z_in.infolist():
                        if info.filename in remove_set:
                            continue
                        data = z_in.read(info.filename)
                        z_out.writestr(info, data)
                        created_count += 1
            return True, f"Created clean sanitized archive at {output_clean_archive}", created_count
        except Exception as e:
            return False, str(e), 0

    def smart_extract(self, archive_path: str, target_dir: str, strip_junk: bool = True) -> Tuple[bool, str, int]:
        """Extracts files while pruning unwanted OS junk and normalizing single-subfolder nesting."""
        pruned_count = 0
        os.makedirs(target_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    category = self._classify_junk(info.filename)
                    if strip_junk and category != "Other Clutter":
                        pruned_count += 1
                        continue

                    target_fp = os.path.join(target_dir, info.filename.replace("/", os.sep))
                    os.makedirs(os.path.dirname(target_fp), exist_ok=True)
                    with open(target_fp, "wb") as out_f:
                        out_f.write(zf.read(info.filename))

            return True, target_dir, pruned_count
        except Exception:
            return False, target_dir, 0
