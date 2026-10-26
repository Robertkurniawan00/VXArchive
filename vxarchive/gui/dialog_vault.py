"""
Password vault management dialog.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel
)
from ..core.password_vault import PasswordVault


class PasswordVaultDialog(QDialog):
    def __init__(self, parent=None, is_select_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Password Vault")
        self.resize(450, 320)
        self.is_select_mode = is_select_mode
        self.vault = PasswordVault.get_instance()

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Label", "Password"])
        layout.addWidget(self.table)
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        for it in self.vault.get_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(it.get("label", "")))
            self.table.setItem(row, 1, QTableWidgetItem("••••••••"))
