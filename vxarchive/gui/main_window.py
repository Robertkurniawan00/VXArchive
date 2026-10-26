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
        self.setWindowTitle("VXArchive - Modern Dark Glass Edition")
        self.resize(1000, 650)

        apply_windows_11_mica(self, backdrop_type="mica_alt", dark_mode=True, rounded_corners=True)
        apply_dark_glass_theme(self)

        self._setup_ui(initial_path or os.getcwd())

    def _setup_ui(self, initial_path: str):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.add_tab(initial_path)
        self._setup_toolbar()
        self.statusBar().showMessage("Ready")

    def _setup_toolbar(self):
        tb = self.addToolBar("Standard")
        tb.setMovable(False)

        self.act_back = QAction("Back", self)
        self.act_back.triggered.connect(self._action_back)
        tb.addAction(self.act_back)

        self.act_forward = QAction("Forward", self)
        self.act_forward.triggered.connect(self._action_forward)
        tb.addAction(self.act_forward)

        tb.addSeparator()

        act_add = QAction("Add", self)
        act_add.triggered.connect(self._action_add)
        tb.addAction(act_add)

        act_extract = QAction("Extract", self)
        act_extract.triggered.connect(self._action_extract)
        tb.addAction(act_extract)

        act_test = QAction("Test", self)
        act_test.triggered.connect(self._action_test)
        tb.addAction(act_test)

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

    def _action_test(self):
        from .dialog_health import ArchiveHealthDialog
        dlg = ArchiveHealthDialog(self)
        dlg.exec()
