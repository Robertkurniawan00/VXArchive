"""
Dark glass stylesheet and theme tokens for VXArchive.
"""

DARK_GLASS_STYLE = """
QWidget {
    background-color: #18191c;
    color: #e2e8f0;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #121316;
}

QTabWidget::pane {
    border: 1px solid #2a2d34;
    background-color: #18191c;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1f2126;
    color: #94a3b8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #2a2d34;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #262930;
    color: #ffffff;
    border-bottom: 2px solid #3b82f6;
}

QPushButton {
    background-color: #272a30;
    border: 1px solid #363a45;
    border-radius: 5px;
    padding: 6px 14px;
    color: #f1f5f9;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #32363f;
    border-color: #474c5a;
}

QPushButton:pressed {
    background-color: #1e2025;
}

QLineEdit, QComboBox, QSpinBox {
    background-color: #1e2025;
    border: 1px solid #363a45;
    border-radius: 5px;
    padding: 5px 8px;
    color: #f8fafc;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
}

QTableView, QTreeView, QListWidget {
    background-color: #18191c;
    border: 1px solid #2a2d34;
    border-radius: 6px;
    gridline-color: #23262c;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #1e2025;
    color: #94a3b8;
    padding: 6px;
    border: 1px solid #2a2d34;
    font-weight: bold;
}

QScrollBar:vertical {
    border: none;
    background: #18191c;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #333742;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #474c5a;
}
"""


def apply_dark_glass_theme(app_or_widget):
    app_or_widget.setStyleSheet(DARK_GLASS_STYLE)
