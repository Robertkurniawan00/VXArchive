"""
Main multi-tab application window for VXArchive.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QToolBar, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

from .tab_page import ArchiveTabPage
from .mica_effect import apply_windows_11_mica
from .glass_theme import apply_dark_glass_theme
from .icons import IconEngine


class VXArchiveMainWindow(QMainWindow):
    def __init__(self, initial_path: str = None):
        super().__init__()
        self.setWindowTitle("VXArchive")
        self.resize(1020, 660)

        # Apply application & window icon
        self._init_window_icon()

        apply_windows_11_mica(self, backdrop_type="mica_alt", dark_mode=True, rounded_corners=True)
        apply_dark_glass_theme(self)

        self._setup_ui(initial_path or os.getcwd())

    def _init_window_icon(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(base_dir, "vxarchive.ico"),
            os.path.join(os.path.dirname(base_dir), "vxarchive.ico"),
            os.path.join(getattr(sys, "_MEIPASS", ""), "vxarchive.ico") if getattr(sys, "frozen", False) else "",
            os.path.join(os.path.dirname(sys.executable), "vxarchive.ico") if getattr(sys, "frozen", False) else "",
            "vxarchive.ico"
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                self.setWindowIcon(QIcon(c))
                break

    def _setup_ui(self, initial_path: str):
        self._setup_menu_bar()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.add_tab(initial_path)
        self._setup_toolbar()
        self.statusBar().showMessage("Ready")

    def _setup_menu_bar(self):
        mb = self.menuBar()

        # --- File Menu ---
        file_menu = mb.addMenu("&File")
        
        act_new_tab = QAction("New Tab", self)
        act_new_tab.setShortcut("Ctrl+T")
        act_new_tab.triggered.connect(lambda: self.add_tab(self.current_tab.current_folder_path if self.current_tab else os.getcwd()))
        file_menu.addAction(act_new_tab)

        act_open = QAction("Open Archive...", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self._action_open_file)
        file_menu.addAction(act_open)

        file_menu.addSeparator()

        act_close_tab = QAction("Close Tab", self)
        act_close_tab.setShortcut("Ctrl+W")
        act_close_tab.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(act_close_tab)

        file_menu.addSeparator()

        act_exit = QAction("Exit", self)
        act_exit.setShortcut("Alt+F4")
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- Commands Menu ---
        cmd_menu = mb.addMenu("&Commands")

        act_cmd_add = QAction("Add files to archive...", self)
        act_cmd_add.setShortcut("Alt+A")
        act_cmd_add.triggered.connect(self._action_add)
        cmd_menu.addAction(act_cmd_add)

        act_cmd_extract = QAction("Extract to specified folder...", self)
        act_cmd_extract.setShortcut("Alt+E")
        act_cmd_extract.triggered.connect(self._action_extract)
        cmd_menu.addAction(act_cmd_extract)

        act_cmd_test = QAction("Test archived files", self)
        act_cmd_test.setShortcut("Alt+T")
        act_cmd_test.triggered.connect(self._action_test)
        cmd_menu.addAction(act_cmd_test)

        cmd_menu.addSeparator()

        act_cmd_chart = QAction("Storage Donut Chart...", self)
        act_cmd_chart.triggered.connect(self._action_chart)
        cmd_menu.addAction(act_cmd_chart)

        act_cmd_threat = QAction("Threat & Ransomware Scanner...", self)
        act_cmd_threat.triggered.connect(self._action_threat_scanner)
        cmd_menu.addAction(act_cmd_threat)

        act_cmd_sanitizer = QAction("Archive Sanitizer (Purge Bloat)...", self)
        act_cmd_sanitizer.triggered.connect(self._action_sanitizer)
        cmd_menu.addAction(act_cmd_sanitizer)

        act_cmd_metadata = QAction("Metadata Inspector...", self)
        act_cmd_metadata.triggered.connect(self._action_metadata)
        cmd_menu.addAction(act_cmd_metadata)

        # --- Tools Menu ---
        tools_menu = mb.addMenu("&Tools")

        act_tool_vault = QAction("Password Vault...", self)
        act_tool_vault.setShortcut("Ctrl+P")
        act_tool_vault.triggered.connect(self._action_vault)
        tools_menu.addAction(act_tool_vault)

        act_tool_transcoder = QAction("Archive Converter / Transcoder...", self)
        act_tool_transcoder.triggered.connect(self._action_transcoder)
        tools_menu.addAction(act_tool_transcoder)

        act_tool_repair = QAction("Repair Corrupted Archive...", self)
        act_tool_repair.setShortcut("Alt+R")
        act_tool_repair.triggered.connect(self._action_repair)
        tools_menu.addAction(act_tool_repair)

        act_tool_splitter = QAction("Split / Merge Volumes...", self)
        act_tool_splitter.triggered.connect(self._action_splitter)
        tools_menu.addAction(act_tool_splitter)

        act_tool_shredder = QAction("Secure File Shredder (DoD 5220.22-M)...", self)
        act_tool_shredder.triggered.connect(self._action_shredder)
        tools_menu.addAction(act_tool_shredder)

        tools_menu.addSeparator()

        act_tool_grep = QAction("Deep Archive Grep Search...", self)
        act_tool_grep.setShortcut("Ctrl+Shift+F")
        act_tool_grep.triggered.connect(self._action_grep)
        tools_menu.addAction(act_tool_grep)

        act_tool_duplicates = QAction("Duplicate File Analyzer...", self)
        act_tool_duplicates.triggered.connect(self._action_duplicates)
        tools_menu.addAction(act_tool_duplicates)

        act_tool_stego = QAction("Steganography Studio (Carrier Injection)...", self)
        act_tool_stego.triggered.connect(self._action_steganography)
        tools_menu.addAction(act_tool_stego)

        act_tool_sfx = QAction("SFX Studio (Executable Generator)...", self)
        act_tool_sfx.triggered.connect(self._action_sfx)
        tools_menu.addAction(act_tool_sfx)

        act_tool_lan = QAction("LAN Archive Share (QR Code & HTTP)...", self)
        act_tool_lan.triggered.connect(self._action_lan_share)
        tools_menu.addAction(act_tool_lan)

        act_tool_diff = QAction("Diff Sync Engine...", self)
        act_tool_diff.triggered.connect(self._action_diff_sync)
        tools_menu.addAction(act_tool_diff)

        tools_menu.addSeparator()

        act_tool_batch = QAction("Batch Archive Manager...", self)
        act_tool_batch.triggered.connect(self._action_batch)
        tools_menu.addAction(act_tool_batch)

        act_tool_integration = QAction("Windows Shell Integration Settings...", self)
        act_tool_integration.triggered.connect(self._action_integration)
        tools_menu.addAction(act_tool_integration)

        act_tool_benchmark = QAction("Hardware Speed Benchmark...", self)
        act_tool_benchmark.setShortcut("Alt+B")
        act_tool_benchmark.triggered.connect(self._action_benchmark)
        tools_menu.addAction(act_tool_benchmark)

        # --- Favorites Menu ---
        fav_menu = mb.addMenu("&Favorites")

        act_fav_hub = QAction("Bookmark Hub...", self)
        act_fav_hub.setShortcut("Ctrl+D")
        act_fav_hub.triggered.connect(self._action_bookmarks)
        fav_menu.addAction(act_fav_hub)

        # --- Help Menu ---
        help_menu = mb.addMenu("&Help")

        act_about = QAction("About VXArchive...", self)
        act_about.triggered.connect(self._action_about)
        help_menu.addAction(act_about)

        act_license = QAction("License & Registration...", self)
        act_license.triggered.connect(self._action_eval)
        help_menu.addAction(act_license)

    def _setup_toolbar(self):
        from PyQt6.QtCore import QSize
        tb = self.addToolBar("Standard")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Back & Forward Navigation
        self.act_back = QAction(IconEngine.get_icon("back", 20), "Back", self)
        self.act_back.setToolTip("Back to previous folder (Alt+Left)")
        self.act_back.triggered.connect(self._action_back)
        tb.addAction(self.act_back)

        self.act_forward = QAction(IconEngine.get_icon("forward", 20), "Forward", self)
        self.act_forward.setToolTip("Forward to next folder (Alt+Right)")
        self.act_forward.triggered.connect(self._action_forward)
        tb.addAction(self.act_forward)

        tb.addSeparator()

        # Core Archive Commands
        act_add = QAction(IconEngine.get_icon("add", 20), "Add", self)
        act_add.setToolTip("Add files to archive (Alt+A)")
        act_add.triggered.connect(self._action_add)
        tb.addAction(act_add)

        act_extract = QAction(IconEngine.get_icon("extract", 20), "Extract", self)
        act_extract.setToolTip("Extract files to folder (Alt+E)")
        act_extract.triggered.connect(self._action_extract)
        tb.addAction(act_extract)

        act_test = QAction(IconEngine.get_icon("test", 20), "Test", self)
        act_test.setToolTip("Test archive integrity (Alt+T)")
        act_test.triggered.connect(self._action_test)
        tb.addAction(act_test)

        act_view = QAction(IconEngine.get_icon("view", 20), "View", self)
        act_view.setToolTip("QuickLook instant file preview (Spacebar)")
        act_view.triggered.connect(self._action_view)
        tb.addAction(act_view)

        act_delete = QAction(IconEngine.get_icon("delete", 20), "Delete", self)
        act_delete.setToolTip("Delete selected items (Del)")
        act_delete.triggered.connect(self._action_delete_selected)
        tb.addAction(act_delete)

        tb.addSeparator()

        # Pro Tools Quick Bar
        act_repair = QAction(IconEngine.get_icon("repair", 20), "Repair", self)
        act_repair.setToolTip("Salvage and repair damaged archive (Alt+R)")
        act_repair.triggered.connect(self._action_repair)
        tb.addAction(act_repair)

        act_vault = QAction(IconEngine.get_icon("vault", 20), "Vault", self)
        act_vault.setToolTip("Encrypted Password Vault (Ctrl+P)")
        act_vault.triggered.connect(self._action_vault)
        tb.addAction(act_vault)

        act_chart = QAction(IconEngine.get_icon("chart", 20), "Chart", self)
        act_chart.setToolTip("Storage Donut Chart visualization")
        act_chart.triggered.connect(self._action_chart)
        tb.addAction(act_chart)

        tb.addSeparator()

        act_refresh = QAction(IconEngine.get_icon("refresh", 20), "Refresh", self)
        act_refresh.setToolTip("Reload directory or archive (F5)")
        act_refresh.triggered.connect(self._action_refresh)
        tb.addAction(act_refresh)

    @property
    def current_tab(self) -> ArchiveTabPage:
        return self.tabs.currentWidget()

    def add_tab(self, folder_or_archive: str) -> int:
        tab = ArchiveTabPage(folder_or_archive, parent=self)
        title = os.path.basename(folder_or_archive) or "Home"
        idx = self.tabs.addTab(tab, title)
        self.tabs.setCurrentIndex(idx)
        return idx

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            w = self.tabs.widget(index)
            self.tabs.removeTab(index)
            if w:
                w.deleteLater()

    def open_path(self, path: str):
        if os.path.exists(path):
            self.add_tab(path)

    def _action_back(self):
        if self.current_tab:
            self.current_tab.go_back()

    def _action_forward(self):
        if self.current_tab:
            self.current_tab.go_forward()

    def _action_add(self):
        from .dialog_add import ArchiveNameAndParametersDialog
        dlg = ArchiveNameAndParametersDialog(self)
        dlg.exec()

    def _action_extract(self):
        from .dialog_extract import ExtractionPathAndOptionsDialog
        dlg = ExtractionPathAndOptionsDialog(self)
        dlg.exec()

    def _action_view(self):
        if self.current_tab:
            self.current_tab.show_quicklook_for_selection()

    def _action_delete_selected(self):
        if not self.current_tab:
            return
        selected = self.current_tab.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Delete", "Please select an item to delete.")
            return
        row = selected[0].row()
        name_item = self.current_tab.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text().rstrip("/")
        ret = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to permanently delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret == QMessageBox.StandardButton.Yes:
            if self.current_tab.current_archive_path:
                self.current_tab.engine.delete_items_from_archive(self.current_tab.current_archive_path, [name])
                self.current_tab.open_archive(self.current_tab.current_archive_path)
            else:
                target = os.path.join(self.current_tab.current_folder_path, name)
                if os.path.isfile(target):
                    os.remove(target)
                elif os.path.isdir(target):
                    import shutil
                    shutil.rmtree(target, ignore_errors=True)
                self.current_tab.load_directory(self.current_tab.current_folder_path)

    def _action_refresh(self):
        if self.current_tab:
            if self.current_tab.current_archive_path:
                self.current_tab.open_archive(self.current_tab.current_archive_path)
            else:
                self.current_tab.load_directory(self.current_tab.current_folder_path)

    def _action_test(self):
        from .dialog_health import ArchiveHealthDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = ArchiveHealthDialog(self, archive_path=archive_path)
        dlg.exec()

    def _action_open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Archive", "",
            "Archive Files (*.zip *.rar *.7z *.tar *.gz *.bz2 *.xz *.iso *.cab *.wim);;All Files (*.*)"
        )
        if path:
            self.open_path(path)

    def _action_chart(self):
        from .dialog_chart import StorageChartDialog
        items = []
        if self.current_tab and self.current_tab.items:
            items = [{"name": it.name, "size": it.size} for it in self.current_tab.items]
        dlg = StorageChartDialog(self, items=items)
        dlg.exec()

    def _action_threat_scanner(self):
        from .dialog_threat_scanner import ThreatScannerDialog
        items = self.current_tab.items if self.current_tab else []
        name = self.current_tab.current_archive_path if self.current_tab else "sample.zip"
        dlg = ThreatScannerDialog(self, archive_items=items, archive_name=name)
        dlg.exec()

    def _action_sanitizer(self):
        from .dialog_sanitizer import ArchiveSanitizerDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = ArchiveSanitizerDialog(self, archive_path=archive_path)
        dlg.exec()

    def _action_metadata(self):
        from .dialog_metadata import MetadataInspectorDialog
        name = self.current_tab.current_archive_path if self.current_tab else "Archive"
        dlg = MetadataInspectorDialog(self, file_name=name, raw_data=b"VXArchive Metadata Payload")
        dlg.exec()

    def _action_vault(self):
        from .dialog_vault import PasswordVaultDialog
        dlg = PasswordVaultDialog(self, is_select_mode=False)
        dlg.exec()

    def _action_transcoder(self):
        from .dialog_transcoder import TranscoderDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = TranscoderDialog(self, initial_archive=archive_path)
        dlg.exec()

    def _action_repair(self):
        from .dialog_repair import ArchiveRepairDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = ArchiveRepairDialog(self, initial_archive=archive_path)
        dlg.exec()

    def _action_splitter(self):
        from .dialog_splitter import VolumeSplitterDialog
        initial_file = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = VolumeSplitterDialog(self, initial_file=initial_file)
        dlg.exec()

    def _action_shredder(self):
        from .dialog_shredder import ShredderDialog
        dlg = ShredderDialog(self)
        dlg.exec()

    def _action_grep(self):
        from .dialog_grep import DeepGrepDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = DeepGrepDialog(self, archive_path=archive_path)
        dlg.exec()

    def _action_duplicates(self):
        from .dialog_duplicates import DuplicateAnalyzerDialog
        folder = self.current_tab.current_folder_path if self.current_tab else os.getcwd()
        dlg = DuplicateAnalyzerDialog(self, initial_folder=folder)
        dlg.exec()

    def _action_steganography(self):
        from .dialog_steganography import SteganographyDialog
        dlg = SteganographyDialog(self)
        dlg.exec()

    def _action_sfx(self):
        from .dialog_sfx import SFXStudioDialog
        source = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = SFXStudioDialog(self, initial_source=source)
        dlg.exec()

    def _action_lan_share(self):
        from .dialog_lan_share import LANShareDialog
        fp = self.current_tab.current_archive_path if self.current_tab else ""
        dlg = LANShareDialog(self, file_path=fp)
        dlg.exec()

    def _action_diff_sync(self):
        from .dialog_diff_sync import DiffSyncDialog
        archive_path = self.current_tab.current_archive_path if self.current_tab else ""
        folder = self.current_tab.current_folder_path if self.current_tab else os.getcwd()
        dlg = DiffSyncDialog(self, initial_archive=archive_path, initial_folder=folder)
        dlg.exec()

    def _action_batch(self):
        from .dialog_batch import BatchManagerDialog
        dlg = BatchManagerDialog(self)
        dlg.exec()

    def _action_integration(self):
        from .dialog_integration import SystemIntegrationDialog
        dlg = SystemIntegrationDialog(self)
        dlg.exec()

    def _action_benchmark(self):
        from .dialog_benchmark import BenchmarkDialog
        dlg = BenchmarkDialog(self)
        dlg.exec()

    def _action_bookmarks(self):
        from .dialog_bookmarks import BookmarkHubDialog
        path = self.current_tab.current_folder_path if self.current_tab else os.getcwd()
        dlg = BookmarkHubDialog(self, current_path=path)
        dlg.exec()

    def _action_about(self):
        from .dialog_about import AboutVXArchiveDialog
        dlg = AboutVXArchiveDialog(self)
        dlg.exec()

    def _action_eval(self):
        from .dialog_eval import EvaluationDialog
        dlg = EvaluationDialog(self)
        dlg.exec()
