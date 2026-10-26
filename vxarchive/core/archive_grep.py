"""
In-archive deep regular expression and plain text grep search engine.
"""
import os
import re
import zipfile
from typing import List


class GrepMatch:
    def __init__(self, file_path: str, line_number: int, line_content: str):
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content


class ArchiveGrepEngine:
    """Scans plain text and source code embedded inside archives without extraction."""

    def search(self, archive_path: str, query: str, is_regex: bool = False, case_sensitive: bool = False) -> List[GrepMatch]:
        results = []
        if not os.path.isfile(archive_path) or not query:
            return results

        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(query if is_regex else re.escape(query), flags)

        try:
            if zipfile.is_zipfile(archive_path):
                with zipfile.ZipFile(archive_path, "r") as z:
                    for info in z.infolist():
                        if info.is_dir() or info.file_size > 10 * 1024 * 1024:
                            continue
                        try:
                            with z.open(info.filename) as f:
                                for line_no, raw_line in enumerate(f, 1):
                                    line_str = raw_line.decode("utf-8", errors="ignore").rstrip("\r\n")
                                    if pattern.search(line_str):
                                        results.append(GrepMatch(info.filename, line_no, line_str))
                        except Exception:
                            pass
        except Exception:
            pass

        return results
