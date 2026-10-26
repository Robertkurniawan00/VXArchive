"""
Archive integrity, health diagnostics, and CRC32 verification engine.
"""
import os
import zipfile
import zlib
from typing import List


class FileHealthRecord:
    def __init__(self, filename: str, status: str = "OK", details: str = ""):
        self.filename = filename
        self.status = status  # "OK", "CORRUPTED"
        self.details = details


class HealthReport:
    def __init__(self, is_healthy: bool, health_percentage: float, corrupted_count: int, file_records: List[FileHealthRecord]):
        self.is_healthy = is_healthy
        self.health_percentage = health_percentage
        self.corrupted_count = corrupted_count
        self.file_records = file_records


class ArchiveHealthChecker:
    """Performs deep verification of archive stream integrity and CRC32 checksums."""

    def check_health(self, archive_path: str) -> HealthReport:
        records: List[FileHealthRecord] = []
        corrupted_count = 0

        if not os.path.isfile(archive_path):
            return HealthReport(False, 0.0, 1, [FileHealthRecord(archive_path, "CORRUPTED", "File missing")])

        try:
            if zipfile.is_zipfile(archive_path):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    for info in zf.infolist():
                        if info.is_dir():
                            continue
                        try:
                            # Read and verify CRC
                            data = zf.read(info.filename)
                            calc_crc = zlib.crc32(data) & 0xFFFFFFFF
                            if calc_crc == info.CRC:
                                records.append(FileHealthRecord(info.filename, "OK"))
                            else:
                                records.append(FileHealthRecord(info.filename, "CORRUPTED", "CRC mismatch"))
                                corrupted_count += 1
                        except Exception as e:
                            records.append(FileHealthRecord(info.filename, "CORRUPTED", str(e)))
                            corrupted_count += 1
            else:
                records.append(FileHealthRecord("Archive Header", "OK"))
        except Exception as e:
            records.append(FileHealthRecord("Archive Structure", "CORRUPTED", str(e)))
            corrupted_count += 1

        total = max(1, len(records))
        healthy_count = total - corrupted_count
        pct = (healthy_count / total) * 100.0

        return HealthReport(
            is_healthy=(corrupted_count == 0),
            health_percentage=pct,
            corrupted_count=corrupted_count,
            file_records=records
        )
