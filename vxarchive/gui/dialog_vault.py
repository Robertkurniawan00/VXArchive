"""
Password vault management dialog for VXArchive.
Provides features to view, add, edit, delete, and copy stored archive credentials.
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QHeaderView, QAbstractItemView, QMessageBox, QMenu,
    QApplication
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QAction
from ..core.password_vault import PasswordVault


class PasswordEntryDialog(QDialog):
    """Modal dialog for creating or editing a stored password entry."""

    def __init__(self, parent=None, mode="add", label="", password=""):
        super().__init__(parent)
        self.mode = mode
        title = "Add Password to Vault" if mode == "add" else "Edit Vault Entry"
        self.setWindowTitle(title)
        self.setFixedSize(420, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        # Label Field
        layout.addWidget(QLabel("Label / Archive Pattern:"))
        self.txt_label = QLineEdit(label)
        self.txt_label.setPlaceholderText("e.g. project_backup.zip, enc_test.zip, or kuyhaa.me")
        layout.addWidget(self.txt_label)

        # Password Field
        layout.addWidget(QLabel("Password:"))
        pwd_layout = QHBoxLayout()
        pwd_layout.setSpacing(6)
        self.txt_password = QLineEdit(password)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Enter archive decryption password")
        pwd_layout.addWidget(self.txt_password)

        self.btn_toggle_eye = QPushButton("👁")
        self.btn_toggle_eye.setToolTip("Show / Hide Password")
        self.btn_toggle_eye.setFixedWidth(38)
        self.btn_toggle_eye.clicked.connect(self._toggle_password_visibility)
        pwd_layout.addWidget(self.btn_toggle_eye)
        layout.addLayout(pwd_layout)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        btn_box.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_save)
        btn_box.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)

        layout.addLayout(btn_box)

    def _toggle_password_visibility(self):
        if self.txt_password.echoMode() == QLineEdit.EchoMode.Password:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

    def _on_save(self):
        lbl = self.txt_label.text().strip()
        pwd = self.txt_password.text()
        if not lbl:
            QMessageBox.warning(self, "Validation Error", "Please provide a label or file pattern.")
            self.txt_label.setFocus()
            return
        if not pwd:
            QMessageBox.warning(self, "Validation Error", "Password cannot be empty.")
            self.txt_password.setFocus()
            return
        self.accept()

    def get_data(self):
        return self.txt_label.text().strip(), self.txt_password.text()


class PasswordVaultDialog(QDialog):
    """
    Password Vault management dialog.
    Supports viewing, adding, editing, deleting, and copying passwords.
    """

    def __init__(self, parent=None, is_select_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Password Vault")
        self.resize(540, 380)
        self.is_select_mode = is_select_mode
        self.selected_password = ""
        self.vault = PasswordVault.get_instance()

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # Description Label
        lbl_hint = QLabel("Saved passwords for automatic decryption and extraction:")
        lbl_hint.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(lbl_hint)

        # Password Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["LABEL", "PASSWORD"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 160)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self._on_double_click)
        self.table.itemSelectionChanged.connect(self._update_button_states)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

        # Bottom Button Bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        # Add Button
        self.btn_add = QPushButton("Add")
        self.btn_add.setToolTip("Add a new password to the vault")
        self.btn_add.clicked.connect(self._action_add)
        btn_bar.addWidget(self.btn_add)

        # Edit Button
        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setToolTip("Edit the selected password entry")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self._action_edit)
        btn_bar.addWidget(self.btn_edit)

        # Delete Button
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setToolTip("Delete the selected password entry")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._action_delete)
        btn_bar.addWidget(self.btn_delete)

        # Copy Password Button
        self.btn_copy = QPushButton("Copy Password")
        self.btn_copy.setToolTip("Copy selected password to clipboard")
        self.btn_copy.setEnabled(False)
        self.btn_copy.clicked.connect(self._action_copy)
        btn_bar.addWidget(self.btn_copy)

        btn_bar.addStretch()

        if self.is_select_mode:
            self.btn_select = QPushButton("Use Password")
            self.btn_select.setEnabled(False)
            self.btn_select.setDefault(True)
            self.btn_select.clicked.connect(self._action_select)
            btn_bar.addWidget(self.btn_select)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.reject if self.is_select_mode else self.accept)
        btn_bar.addWidget(self.btn_close)

        layout.addLayout(btn_bar)

        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        items = self.vault.get_all()
        for it in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            label = it.get("label", "")
            password = it.get("password", "")

            item_lbl = QTableWidgetItem(label)
            item_lbl.setData(Qt.ItemDataRole.UserRole, {"label": label, "password": password})
            self.table.setItem(row, 0, item_lbl)

            item_pwd = QTableWidgetItem("••••••••")
            item_pwd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_pwd)

        self._update_button_states()

    def _update_button_states(self):
        has_sel = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has_sel)
        self.btn_delete.setEnabled(has_sel)
        self.btn_copy.setEnabled(has_sel)
        if hasattr(self, "btn_select"):
            self.btn_select.setEnabled(has_sel)

    def _get_selected_entry(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def _action_add(self):
        dlg = PasswordEntryDialog(self, mode="add")
        if dlg.exec() == QDialog.DialogCode.Accepted:
            label, password = dlg.get_data()
            self.vault.add_password(label, password)
            self._refresh()
            # Select the newly added row
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 0)
                if item and item.text() == label:
                    self.table.selectRow(r)
                    break

    def _action_edit(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        old_label = entry.get("label", "")
        old_pwd = entry.get("password", "")

        dlg = PasswordEntryDialog(self, mode="edit", label=old_label, password=old_pwd)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_label, new_pwd = dlg.get_data()
            self.vault.update_password(old_label, new_label, new_pwd)
            self._refresh()
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 0)
                if item and item.text() == new_label:
                    self.table.selectRow(r)
                    break

    def _action_delete(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        label = entry.get("label", "")
        reply = QMessageBox.question(
            self,
            "Delete Entry",
            f"Are you sure you want to delete '{label}' from the password vault?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.vault.remove_password(label)
            self._refresh()

    def _action_copy(self):
        entry = self._get_selected_entry()
        if not entry:
            return
        pwd = entry.get("password", "")
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(pwd)
            self.btn_copy.setText("Copied!")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_copy.setText("Copy Password"))

    def _action_select(self):
        entry = self._get_selected_entry()
        if entry:
            self.selected_password = entry.get("password", "")
            self.accept()

    def _on_double_click(self, item):
        if self.is_select_mode:
            self._action_select()
        else:
            self._action_edit()

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        entry = self._get_selected_entry()

        act_add = menu.addAction("Add New Entry...")
        act_add.triggered.connect(self._action_add)

        if entry:
            act_edit = menu.addAction("Edit Entry...")
            act_edit.triggered.connect(self._action_edit)

            act_copy = menu.addAction("Copy Password")
            act_copy.triggered.connect(self._action_copy)

            menu.addSeparator()
            act_del = menu.addAction("Delete Entry")
            act_del.triggered.connect(self._action_delete)

            if self.is_select_mode:
                menu.addSeparator()
                act_select = menu.addAction("Use This Password")
                act_select.triggered.connect(self._action_select)

        menu.exec(self.table.viewport().mapToGlobal(pos))
