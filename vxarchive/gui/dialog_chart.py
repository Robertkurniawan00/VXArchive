"""
Visual storage breakdown chart dialog.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from ..core.utils import format_size


class StorageChartDialog(QDialog):
    def __init__(self, parent=None, items=None):
        super().__init__(parent)
        self.setWindowTitle("Storage Breakdown Chart")
        self.resize(500, 350)
        self.items = items or []

        layout = QVBoxLayout(self)
        self.table = QTableWidget(len(self.items), 2)
        self.table.setHorizontalHeaderLabels(["Name / Category", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        for i, item in enumerate(self.items):
            self.table.setItem(i, 0, QTableWidgetItem(str(item.get("name", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(format_size(item.get("size", 0))))
        layout.addWidget(self.table)
