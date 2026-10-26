"""
Specialized dialogs: Grep, SFX, LAN Share, Missing Volume, Health, Diagnostic, Sanitizer.
"""
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QWidget
)
from PyQt6.QtCore import Qt


class DeepGrepDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Deep In-Archive Grep Search")
        self.resize(550, 350)
        layout = QVBoxLayout(self)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter text or regex query...")
        layout.addWidget(self.query_input)


class SFXStudioDialog(QDialog):
    def __init__(self, parent=None, initial_source=""):
        super().__init__(parent)
        self.setWindowTitle("Standalone SFX Studio")
        self.resize(480, 260)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Compile standalone .exe extractor"))


class LANShareDialog(QDialog):
    def __init__(self, parent=None, file_path=""):
        super().__init__(parent)
        self.setWindowTitle("Instant LAN Wireless Transfer")
        self.resize(450, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Scan QR code or open URL on mobile device"))


class MissingVolumeDialog(QDialog):
    def __init__(self, parent=None, volume_set=None, initial_file=""):
        super().__init__(parent)
        self.setWindowTitle("Missing Volume Chunk Locator")
        self.resize(500, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Missing split volume parts detected"))


class ArchiveHealthDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Health Diagnostic")
        self.resize(550, 350)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Status", "File", "Size", "CRC", "Offset", "Health"])
        layout.addWidget(self.table)


class ExtractionDiagnosticDialog(QDialog):
    def __init__(self, parent=None, archive_path="", dest_dir="", error_message=""):
        super().__init__(parent)
        self.setWindowTitle("Extraction Diagnostic")
        self.resize(550, 350)
        self.error_items = []

        # Parse error_message for ERROR: Data Error : filename
        for line in error_message.splitlines():
            line = line.strip()
            m = re.search(r"ERROR:\s*([^:]+)\s*:\s*(.+)$", line)
            if m:
                self.error_items.append({
                    "type": m.group(1).strip(),
                    "file": m.group(2).strip()
                })

        layout = QVBoxLayout(self)
        self.table = QTableWidget(len(self.error_items), 2)
        self.table.setHorizontalHeaderLabels(["Damaged File", "Error Reason"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for i, item in enumerate(self.error_items):
            self.table.setItem(i, 0, QTableWidgetItem(item["file"]))
            self.table.setItem(i, 1, QTableWidgetItem(item["type"]))
        layout.addWidget(self.table)


class ArchiveSanitizerDialog(QDialog):
    def __init__(self, parent=None, archive_path=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Sanitizer & Anti-Mess Optimizer")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Action", "Filename", "Category", "Size", "Waste %"])
        layout.addWidget(self.table)

        btn_box = QHBoxLayout()
        self.btn_purge = QPushButton("Clean & Purge Junk")
        self.btn_smart_extract = QPushButton("Smart Extract (Sanitized)")
        btn_box.addWidget(self.btn_purge)
        btn_box.addWidget(self.btn_smart_extract)
        layout.addLayout(btn_box)
