"""
QuickLook instant preview dialog.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt


class QuickLookDialog(QDialog):
    def __init__(self, parent=None, title="QuickLook", data=b""):
        super().__init__(parent)
        self.setWindowTitle(f"QuickLook - {title}")
        self.resize(500, 350)
        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        try:
            self.text_edit.setPlainText(data.decode("utf-8", errors="ignore"))
        except Exception:
            self.text_edit.setPlainText(str(data))
        layout.addWidget(self.text_edit)
