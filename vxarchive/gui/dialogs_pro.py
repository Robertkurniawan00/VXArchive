"""
10 Pro modal dialogs for VXArchive: Shredder, Transcoder, Steganography, DiffSync, Splitter, ThreatScanner, Repair, Bookmarks, Iso, Metadata.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QWidget, QTextEdit, QSpinBox
)
from PyQt6.QtCore import Qt


class ShredderDialog(QDialog):
    def __init__(self, parent=None, initial_files=None):
        super().__init__(parent)
        self.setWindowTitle("Secure File Shredder (DoD 5220.22-M)")
        self.resize(450, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Files to permanently destroy:"))
        self.table = QTableWidget(len(initial_files or []), 1)
        layout.addWidget(self.table)


class TranscoderDialog(QDialog):
    def __init__(self, parent=None, initial_archive=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Format Transcoder")
        self.resize(450, 250)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Convert archive to target format:"))


class SteganographyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steganographic Secret Vault")
        self.resize(480, 280)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Hide or Extract Archive within Image"))


class DiffSyncDialog(QDialog):
    def __init__(self, parent=None, initial_archive="", initial_folder=""):
        super().__init__(parent)
        self.setWindowTitle("Smart Archive Diff & Sync")
        self.resize(550, 350)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Archive vs Folder Delta Comparison"))


class VolumeSplitterDialog(QDialog):
    def __init__(self, parent=None, initial_file=""):
        super().__init__(parent)
        self.setWindowTitle("Multi-Volume Splitter & Joiner")
        self.resize(480, 280)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Split large files into chunks:"))


class ThreatScannerDialog(QDialog):
    def __init__(self, parent=None, archive_items=None, archive_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Threat & Decompression Bomb Scanner - {archive_name}")
        self.resize(520, 320)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Security Analysis & Threat Report"))


class ArchiveRepairDialog(QDialog):
    def __init__(self, parent=None, initial_archive=""):
        super().__init__(parent)
        self.setWindowTitle("Archive Integrity Salvager & Repair")
        self.resize(480, 260)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reconstruct damaged archive headers"))


class BookmarkHubDialog(QDialog):
    def __init__(self, parent=None, current_path=""):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks & Project Pinboard")
        self.resize(450, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Pinned folders and project hubs"))


class IsoMounterDialog(QDialog):
    def __init__(self, parent=None, initial_iso=""):
        super().__init__(parent)
        self.setWindowTitle("Virtual Disk / ISO Mounter")
        self.resize(420, 220)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mount ISO or VHD as virtual drive"))


class MetadataInspectorDialog(QDialog):
    def __init__(self, parent=None, file_name="", raw_data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"Metadata Inspector - {file_name}")
        self.resize(460, 320)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        layout.addWidget(self.table)
