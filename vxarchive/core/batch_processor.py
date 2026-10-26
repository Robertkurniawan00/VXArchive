"""
Batch archive multi-file compression and extraction manager.
"""
import os
from typing import List, Dict, Any


class BatchProcessor:
    """Handles bulk multi-archive operations."""

    def __init__(self, engine):
        self.engine = engine

    def batch_compress_separate(self, source_paths: List[str], output_dir: str,
                                archive_format: str = "zip", password: str = None) -> List[Dict[str, Any]]:
        results = []
        os.makedirs(output_dir, exist_ok=True)
        fmt = archive_format.lower().lstrip(".")

        for src in source_paths:
            base_name = os.path.splitext(os.path.basename(src))[0]
            out_arc = os.path.join(output_dir, f"{base_name}.{fmt}")
            ok, msg = self.engine.create_archive(
                output_archive=out_arc,
                files_to_add=[src],
                archive_format=fmt,
                password=password
            )
            results.append({
                "source": src,
                "archive": out_arc,
                "success": ok,
                "message": msg
            })
        return results

    def batch_extract(self, archive_paths: List[str], base_dest_dir: str,
                      extract_to_subfolders: bool = True, password: str = None) -> List[Dict[str, Any]]:
        results = []
        os.makedirs(base_dest_dir, exist_ok=True)

        for arc in archive_paths:
            if extract_to_subfolders:
                folder_name = os.path.splitext(os.path.basename(arc))[0]
                target = os.path.join(base_dest_dir, folder_name)
            else:
                target = base_dest_dir

            ok, msg = self.engine.extract_archive(arc, target, password=password)
            results.append({
                "archive": arc,
                "destination": target,
                "success": ok,
                "message": msg
            })
        return results
