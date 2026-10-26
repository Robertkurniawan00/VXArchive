"""
Archive and Directory Browser Tab Page for VXArchive.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..core.archive_engine import ArchiveEngine, ArchiveItem
from ..core.utils import format_size


class ArchiveTabPage(QWidget):
    item_activated = pyqtSignal(str)

    def __init__(self, initial_path: str = None, parent=None):
        super().__init__(parent)
        self.engine = ArchiveEngine()
        self.current_folder_path = initial_path or os.getcwd()
        self.current_archive_path = None
        self.items = []

        self.history_back = []
        self.history_forward = []

        self._setup_ui()
        if os.path.isfile(self.current_folder_path):
            self.open_archive(self.current_folder_path)
        else:
            self.load_directory(self.current_folder_path)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Address bar
        addr_box = QHBoxLayout()
        self.addr_input = QLineEdit(self.current_folder_path)
        self.addr_input.returnPressed.connect(self._on_address_entered)
        addr_box.addWidget(self.addr_input)
        layout.addLayout(addr_box)

        # File table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Size", "Packed", "Modified", "Attributes"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.itemDoubleClicked.connect(self._on_table_double_clicked)
        layout.addWidget(self.table)

    def _on_address_entered(self):
        p = self.addr_input.text().strip()
        if os.path.isdir(p):
            self.navigate_to_folder(p)
        elif os.path.isfile(p):
            self.open_archive(p)

    def can_go_back(self) -> bool:
        return len(self.history_back) > 0

    def can_go_forward(self) -> bool:
        return len(self.history_forward) > 0

    def navigate_to_folder(self, folder_path: str, record_history: bool = True):
        norm = os.path.abspath(folder_path)
        if not os.path.isdir(norm):
            return
        if record_history and self.current_folder_path:
            self.history_back.append(self.current_folder_path)
            self.history_forward.clear()

        self.current_folder_path = norm
        self.current_archive_path = None
        self.addr_input.setText(norm)
        self.load_directory(norm)

    def go_back(self):
        if self.can_go_back():
            prev = self.history_back.pop()
            self.history_forward.append(self.current_folder_path)
            self.navigate_to_folder(prev, record_history=False)

    def go_forward(self):
        if self.can_go_forward():
            nxt = self.history_forward.pop()
            self.history_back.append(self.current_folder_path)
            self.navigate_to_folder(nxt, record_history=False)

    def load_directory(self, folder_path: str):
        self.table.setRowCount(0)
        try:
            entries = os.listdir(folder_path)
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x.lower()))

            for name in entries:
                fp = os.path.join(folder_path, name)
                is_dir = os.path.isdir(fp)
                sz = format_size(os.path.getsize(fp)) if not is_dir else ""
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(name + ("/" if is_dir else "")))
                self.table.setItem(row, 1, QTableWidgetItem(sz))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(""))
                self.table.setItem(row, 4, QTableWidgetItem("Directory" if is_dir else "File"))
        except Exception:
            pass

    def open_archive(self, archive_path: str):
        self.current_archive_path = archive_path
        self.addr_input.setText(archive_path)
        self.table.setRowCount(0)

        items = self.engine.list_archive_contents(archive_path)
        self.items = items
        for it in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(it.name))
            self.table.setItem(row, 1, QTableWidgetItem(format_size(it.size)))
            self.table.setItem(row, 2, QTableWidgetItem(format_size(it.packed_size)))
            self.table.setItem(row, 3, QTableWidgetItem(it.mtime))
            self.table.setItem(row, 4, QTableWidgetItem(it.attributes))

    def _on_table_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text()

        if self.current_archive_path:
            # Internal archive item
            self.item_activated.emit(name)
        else:
            fp = os.path.join(self.current_folder_path, name.rstrip("/"))
            if os.path.isdir(fp):
                self.navigate_to_folder(fp)
            elif os.path.isfile(fp):
                ext = os.path.splitext(fp)[1].lower()
                if ext in (".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".cab"):
                    self.open_archive(fp)
                else:
                    self.item_activated.emit(fp)
