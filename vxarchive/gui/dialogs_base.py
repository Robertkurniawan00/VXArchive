"""
Core modal dialogs for VXArchive: Add, Extract, View, Info, Benchmark, About, Eval, Find, Wizard, Password, Progress, Hash, Duplicates, Batch.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFileDialog, QMessageBox, QWidget, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from ..core.archive_engine import ArchiveEngine
from ..core.benchmark import VXArchiveBenchmark
from ..core.hasher import HashEngine
from ..core.dedup_analyzer import DuplicateAnalyzer
from ..core.utils import format_size


class ArchiveNameAndParametersDialog(QDialog):
    def __init__(self, parent=None, default_archive_name="archive.zip", files_to_add=None):
        super().__init__(parent)
        self.setWindowTitle("Add to Archive")
        self.resize(450, 300)
        self.files_to_add = files_to_add or []

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Archive name:"))
        self.name_input = QLineEdit(default_archive_name)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Archive format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["ZIP", "7Z", "TAR"])
        layout.addWidget(self.format_combo)

        layout.addWidget(QLabel("Compression level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Fast", "Normal", "Maximum", "Ultra"])
        self.level_combo.setCurrentIndex(1)
        layout.addWidget(self.level_combo)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)


class ExtractionPathAndOptionsDialog(QDialog):
    def __init__(self, parent=None, default_dest="C:\\Temp", default_archive=""):
        super().__init__(parent)
        self.setWindowTitle("Extract Archive")
        self.resize(450, 250)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Extract to destination:"))
        self.dest_input = QLineEdit(default_dest)
        layout.addWidget(self.dest_input)

        self.chk_subfolder = QCheckBox("Extract to subfolder")
        self.chk_subfolder.setChecked(True)
        layout.addWidget(self.chk_subfolder)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Extract")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)


class InternalViewerDialog(QDialog):
    def __init__(self, parent=None, title="Viewer", data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"Viewer - {title}")
        self.resize(550, 400)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        try:
            self.text_edit.setPlainText(data.decode("utf-8", errors="ignore"))
        except Exception:
            self.text_edit.setPlainText(str(data))
        layout.addWidget(self.text_edit)


class ArchiveInfoDialog(QDialog):
    def __init__(self, parent=None, info=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Information")
        self.resize(400, 300)
        self.info = info or {}

        layout = QVBoxLayout(self)
        self.table = QTableWidget(len(self.info), 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i, (k, v) in enumerate(self.info.items()):
            self.table.setItem(i, 0, QTableWidgetItem(str(k)))
            self.table.setItem(i, 1, QTableWidgetItem(str(v)))
        layout.addWidget(self.table)


class BenchmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Compression Benchmark")
        self.resize(450, 250)
        self.benchmark = VXArchiveBenchmark()

        layout = QVBoxLayout(self)
        self.lbl_speed = QLabel("Throughput: 0 MB/s")
        layout.addWidget(self.lbl_speed)

        self.btn_toggle = QPushButton("Start Benchmark")
        self.btn_toggle.clicked.connect(self._toggle)
        layout.addWidget(self.btn_toggle)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)

    def _toggle(self):
        if not self.benchmark.running:
            self.benchmark.start()
            self.btn_toggle.setText("Stop Benchmark")
            self.timer.start(100)
        else:
            self.benchmark.stop()
            self.btn_toggle.setText("Start Benchmark")
            self.timer.stop()

    def _update(self):
        self.lbl_speed.setText(f"Throughput: {self.benchmark.speed_mb_per_sec:.2f} MB/s")

    def closeEvent(self, e):
        if self.benchmark.running:
            self.benchmark.stop()
        super().closeEvent(e)


class AboutVXArchiveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About VXArchive")
        self.resize(400, 260)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Show official app icon
        ico_label = QLabel()
        ico_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for cand in [
            os.path.join(base_dir, "vxarchive.ico"),
            os.path.join(os.path.dirname(base_dir), "vxarchive.ico"),
            os.path.join(getattr(sys, "_MEIPASS", ""), "vxarchive.ico") if getattr(sys, "frozen", False) else "",
            os.path.join(os.path.dirname(sys.executable), "vxarchive.ico") if getattr(sys, "frozen", False) else "",
            "vxarchive.ico"
        ]:
            if cand and os.path.isfile(cand):
                pix = QPixmap(cand).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                ico_label.setPixmap(pix)
                self.setWindowIcon(QIcon(cand))
                break
        layout.addWidget(ico_label)

        lbl = QLabel("<h2>VXArchive</h2><p style='color: #94a3b8;'>Modern Dark Glass Archive Manager</p><p>Version 2.0 (Windows 11 Edition)</p>")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)


class EvaluationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VXArchive Evaluation")
        self.resize(360, 180)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Thank you for using VXArchive!"))


class FindFilesDialog(QDialog):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.setWindowTitle("Find Files")
        self.resize(400, 250)
        layout = QVBoxLayout(self)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file names...")
        layout.addWidget(self.search_input)


class WizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Archive Wizard")
        self.resize(450, 300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Step 1: Choose operation"))


class PasswordDialog(QDialog):
    def __init__(self, parent=None, is_prompt_mode=False, archive_name=""):
        super().__init__(parent)
        self.setWindowTitle("Enter Password" if is_prompt_mode else "Password Options")
        self.resize(380, 180)
        self.is_prompt_mode = is_prompt_mode

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter archive password:"))
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pwd_input)

        if is_prompt_mode:
            self.remember_file_chk = QCheckBox("Remember password for this file")
            layout.addWidget(self.remember_file_chk)

            # Generate pattern hint
            from ..core.password_memory import ArchivePasswordMemory
            mem = ArchivePasswordMemory.get_instance()
            cands = mem.extract_pattern_candidates(archive_name)
            pat_text = f"Remember for series ({cands[0]})" if cands else "Remember for series"
            self.remember_pattern_chk = QCheckBox(pat_text)
            layout.addWidget(self.remember_pattern_chk)


class VXArchiveProgressDialog(QDialog):
    def __init__(self, parent=None, title="Operation in Progress", operation_type="Processing"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 160)

        layout = QVBoxLayout(self)
        self.lbl_status = QLabel(f"{operation_type}...")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)


class HashInspectorDialog(QDialog):
    def __init__(self, parent=None, file_path_or_data=b"", display_name="sample.txt"):
        super().__init__(parent)
        self.setWindowTitle(f"Checksum Inspector - {display_name}")
        self.resize(500, 300)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(["Algorithm", "Hash Value"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        import hashlib
        import zlib
        data = file_path_or_data if isinstance(file_path_or_data, bytes) else b""
        crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"
        md5 = hashlib.md5(data).hexdigest().upper()
        sha1 = hashlib.sha1(data).hexdigest().upper()
        sha256 = hashlib.sha256(data).hexdigest().upper()
        sha512 = hashlib.sha512(data).hexdigest().upper()

        algos = [("CRC32", crc), ("MD5", md5), ("SHA-1", sha1), ("SHA-256", sha256), ("SHA-512", sha512)]
        for i, (a, h) in enumerate(algos):
            self.table.setItem(i, 0, QTableWidgetItem(a))
            self.table.setItem(i, 1, QTableWidgetItem(h))
        layout.addWidget(self.table)


class DuplicateAnalyzerDialog(QDialog):
    def __init__(self, parent=None, archive_items=None, title="Duplicate Analyzer"):
        super().__init__(parent)
        self.setWindowTitle(f"Duplicate Analyzer - {title}")
        self.resize(500, 350)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Duplicate Files & Storage Waste:"))
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File Name", "Size", "Duplicate Group"])
        layout.addWidget(self.table)


class BatchManagerDialog(QDialog):
    def __init__(self, parent=None, initial_archives=None, initial_sources=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Multi-Archive Manager")
        self.resize(550, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Batch Archive Processing Queue"))
