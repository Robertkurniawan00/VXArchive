"""
Duplicate payload and junk file analyzer for archive contents.
"""
from typing import List, Dict, Any
from collections import defaultdict


class DuplicateAnalyzer:
    """Analyzes archive items to identify duplicate payloads and operating system junk files."""

    JUNK_NAMES = {
        "thumbs.db", "desktop.ini", ".ds_store", "ehthumbs.db",
        "__macosx", "npm-debug.log", "yarn-error.log"
    }

    @staticmethod
    def analyze_archive_items(items: List[Any]) -> Dict[str, Any]:
        """
        Groups items by size and CRC to find duplicate files and identifies common junk files.
        """
        crc_groups = defaultdict(list)
        junk_items = []
        total_wasted_bytes = 0
        total_duplicate_files = 0

        for item in items:
            if getattr(item, "is_dir", False):
                continue

            name = getattr(item, "name", "").lower()
            if name in DuplicateAnalyzer.JUNK_NAMES or any(name.endswith(j) for j in DuplicateAnalyzer.JUNK_NAMES):
                junk_items.append(item)

            crc = getattr(item, "crc", "").upper()
            size = getattr(item, "size", 0)
            if crc and size > 0:
                key = (size, crc)
                crc_groups[key].append(item)

        duplicate_groups = []
        for (size, crc), group in crc_groups.items():
            if len(group) > 1:
                duplicate_groups.append(group)
                dups_in_group = len(group) - 1
                total_duplicate_files += dups_in_group
                total_wasted_bytes += dups_in_group * size

        return {
            "duplicate_groups_count": len(duplicate_groups),
            "duplicate_groups": duplicate_groups,
            "total_duplicate_files": total_duplicate_files,
            "total_wasted_bytes": total_wasted_bytes,
            "junk_count": len(junk_items),
            "junk_items": junk_items
        }
