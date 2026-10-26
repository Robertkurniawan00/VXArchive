"""
Suspicious threat, deceptive double extension, and decompression bomb scanner.
"""
from typing import List, Dict, Any


class ThreatReport:
    def __init__(self, risk_level: str = "LOW", threats: List[Dict[str, Any]] = None):
        self.risk_level = risk_level  # LOW, MEDIUM, HIGH, CRITICAL
        self.threats = threats or []


class ThreatScanner:
    """Scans archive file lists for malicious patterns, hidden executables, and zip bombs."""

    EXECUTABLE_EXTENSIONS = {
        ".exe", ".bat", ".cmd", ".vbs", ".js", ".jse", ".wsf", ".wsh",
        ".ps1", ".scr", ".pif", ".hta", ".cpl", ".msi", ".jar", ".com"
    }

    DOCUMENT_EXTENSIONS = {
        ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt",
        ".jpg", ".png", ".jpeg", ".mp4", ".mp3", ".zip", ".rar"
    }

    @staticmethod
    def scan_archive_items(items: List[Any]) -> ThreatReport:
        threats = []
        highest_risk = "LOW"
        total_unpacked = 0
        total_packed = 0

        for item in items:
            if getattr(item, "is_dir", False):
                continue

            name = getattr(item, "name", "").lower()
            unpacked = getattr(item, "size", 0)
            packed = getattr(item, "packed_size", 0)
            total_unpacked += unpacked
            total_packed += max(1, packed)

            # Check deceptive double extension
            parts = name.split(".")
            if len(parts) >= 3:
                ext1 = f".{parts[-2]}"
                ext2 = f".{parts[-1]}"
                if ext1 in ThreatScanner.DOCUMENT_EXTENSIONS and ext2 in ThreatScanner.EXECUTABLE_EXTENSIONS:
                    threats.append({
                        "file": getattr(item, "path", name),
                        "type": "Deceptive Double Extension",
                        "severity": "CRITICAL",
                        "description": f"Hidden executable masking as document ({ext1}{ext2})"
                    })
                    highest_risk = "CRITICAL"

            # Check single suspicious executable
            elif any(name.endswith(ex) for ex in ThreatScanner.EXECUTABLE_EXTENSIONS):
                threats.append({
                    "file": getattr(item, "path", name),
                    "type": "Executable File",
                    "severity": "MEDIUM",
                    "description": "Archive contains executable program"
                })
                if highest_risk not in ("CRITICAL", "HIGH"):
                    highest_risk = "MEDIUM"

        # Check for Zip Bomb / Extreme Compression Ratio
        if total_packed > 0:
            ratio = total_unpacked / total_packed
            if ratio > 250 and total_unpacked > 100 * 1024 * 1024:
                threats.append({
                    "file": "Archive Header",
                    "type": "Decompression Bomb / Zip Bomb",
                    "severity": "CRITICAL",
                    "description": f"Abnormal expansion ratio ({ratio:.1f}:1) exceeding 100MB"
                })
                highest_risk = "CRITICAL"

        return ThreatReport(risk_level=highest_risk, threats=threats)
