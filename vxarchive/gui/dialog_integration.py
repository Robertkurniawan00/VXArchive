"""
Windows Explorer shell integration configuration dialog.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QCheckBox, QLabel, QPushButton, QGridLayout
)
from ..core.shell_integration import ShellIntegration


class SystemIntegrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Shell Integration")
        self.resize(500, 400)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Context Menu
        tab1 = QWidget()
        t1_layout = QVBoxLayout(tab1)
        self.chk_cascaded = QCheckBox("Cascaded Submenu (Group under VXArchive)")
        self.chk_cascaded.setChecked(True)
        self.chk_cascaded.toggled.connect(self._on_cascaded_toggled)
        t1_layout.addWidget(self.chk_cascaded)

        self.lbl_preview_content = QLabel("Preview: VXArchive > Extract here | Extract to subfolder | Add...")
        t1_layout.addWidget(self.lbl_preview_content)
        self.tabs.addTab(tab1, "Context Menu")

        # Tab 2: File Associations
        tab2 = QWidget()
        t2_layout = QVBoxLayout(tab2)
        grid = QGridLayout()
        self.ext_checkboxes = {}
        for idx, ext in enumerate(ShellIntegration.SUPPORTED_EXTS):
            chk = QCheckBox(ext)
            chk.setChecked(True)
            self.ext_checkboxes[ext] = chk
            grid.addWidget(chk, idx // 3, idx % 3)
        t2_layout.addLayout(grid)

        btn_box = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_all.clicked.connect(self._select_all_exts)
        btn_common = QPushButton("Select Common")
        btn_common.clicked.connect(self._select_common_exts)
        btn_none = QPushButton("Clear All")
        btn_none.clicked.connect(self._clear_all_exts)
        btn_box.addWidget(btn_all)
        btn_box.addWidget(btn_common)
        btn_box.addWidget(btn_none)
        t2_layout.addLayout(btn_box)
        self.tabs.addTab(tab2, "File Associations")

        # Tab 3: Shortcuts & Options
        tab3 = QWidget()
        t3_layout = QVBoxLayout(tab3)
        t3_layout.addWidget(QLabel("Desktop and Start Menu Shortcuts"))
        self.tabs.addTab(tab3, "Shortcuts")

    def _on_cascaded_toggled(self, checked: bool):
        if checked:
            self.lbl_preview_content.setText("Preview: VXArchive > Extract here | Extract to subfolder | Add...")
        else:
            self.lbl_preview_content.setText("Preview: Flat Context Menu entries")

    def _clear_all_exts(self):
        for chk in self.ext_checkboxes.values():
            chk.setChecked(False)

    def _select_common_exts(self):
        self._clear_all_exts()
        for ext in [".zip", ".7z", ".rar"]:
            if ext in self.ext_checkboxes:
                self.ext_checkboxes[ext].setChecked(True)

    def _select_all_exts(self):
        for chk in self.ext_checkboxes.values():
            chk.setChecked(True)

    def _get_current_config(self) -> dict:
        return {
            "cascaded": self.chk_cascaded.isChecked(),
            "extensions": [ext for ext, chk in self.ext_checkboxes.items() if chk.isChecked()],
            "enable_open": True,
            "enable_add_zip": True
        }
