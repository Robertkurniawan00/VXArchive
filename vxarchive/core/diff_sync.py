"""
Delta comparison and synchronization between archives and local filesystem folders.
"""
import os
import zipfile
import zlib
from typing import List, Dict, Any


class DiffItem:
    def __init__(self, rel_path: str, status: str, arc_size: int = 0, fs_size: int = 0):
        self.rel_path = rel_path
        self.status = status  # IDENTICAL, MODIFIED, ARCHIVE_ONLY, FOLDER_ONLY
        self.arc_size = arc_size
        self.fs_size = fs_size


class ArchiveDiffSync:
    """Calculates file deltas and synchronizes changes back into archives."""

    def __init__(self, engine=None):
        self.engine = engine

    def compare(self, archive_path: str, folder_path: str) -> List[DiffItem]:
        results = []
        if not os.path.isfile(archive_path) or not os.path.isdir(folder_path):
            return results

        arc_map: Dict[str, Dict[str, Any]] = {}
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as z:
                for info in z.infolist():
                    if not info.is_dir():
                        norm_p = info.filename.replace("\\", "/")
                        arc_map[norm_p] = {
                            "size": info.file_size,
                            "crc": f"{info.CRC & 0xFFFFFFFF:08X}"
                        }
        elif self.engine:
            items = self.engine.list_archive_contents(archive_path)
            for it in items:
                if not it.is_dir:
                    norm_p = it.path.replace("\\", "/")
                    arc_map[norm_p] = {
                        "size": it.size,
                        "crc": it.crc.upper()
                    }

        fs_map: Dict[str, Dict[str, Any]] = {}
        for root, _, files in os.walk(folder_path):
            for f in files:
                fp = os.path.join(root, f)
                rel = os.path.relpath(fp, folder_path).replace("\\", "/")
                sz = os.path.getsize(fp)
                with open(fp, "rb") as fl:
                    crc_val = zlib.crc32(fl.read())
                fs_map[rel] = {
                    "size": sz,
                    "crc": f"{crc_val & 0xFFFFFFFF:08X}"
                }

        all_keys = sorted(set(arc_map.keys()) | set(fs_map.keys()))
        for k in all_keys:
            in_arc = k in arc_map
            in_fs = k in fs_map

            if in_arc and in_fs:
                if arc_map[k]["crc"] == fs_map[k]["crc"]:
                    st = "IDENTICAL"
                else:
                    st = "MODIFIED"
                results.append(DiffItem(k, st, arc_map[k]["size"], fs_map[k]["size"]))
            elif in_arc:
                results.append(DiffItem(k, "ARCHIVE_ONLY", arc_map[k]["size"], 0))
            else:
                results.append(DiffItem(k, "FOLDER_ONLY", 0, fs_map[k]["size"]))

        return results

    def sync_to_archive(self, archive_path: str, folder_path: str, diff_items: List[DiffItem]) -> bool:
        """Pushes folder changes (new & modified files) into the archive."""
        if not os.path.isfile(archive_path) or not os.path.isdir(folder_path):
            return False

        try:
            if zipfile.is_zipfile(archive_path):
                # Append/update files in zip
                with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_DEFLATED) as z:
                    for it in diff_items:
                        if it.status in ("MODIFIED", "FOLDER_ONLY"):
                            fp = os.path.join(folder_path, it.rel_path.replace("/", os.sep))
                            if os.path.isfile(fp):
                                z.write(fp, arcname=it.rel_path)
                return True
            elif self.engine:
                items_to_add = [
                    os.path.join(folder_path, it.rel_path.replace("/", os.sep))
                    for it in diff_items
                    if it.status in ("MODIFIED", "FOLDER_ONLY")
                ]
                if items_to_add:
                    ok, _ = self.engine.add_items_to_archive(archive_path, items_to_add)
                    return ok
                return True
            return False
        except Exception:
            return False
