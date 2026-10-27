"""
Dark glass stylesheet and theme tokens for VXArchive.
"""

DARK_GLASS_STYLE = """
QWidget {
    background-color: #121316;
    color: #e2e8f0;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #121316;
}

/* --- Windows 11 Glass Menu Bar --- */
QMenuBar {
    background-color: transparent;
    color: #cbd5e1;
    padding: 3px 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 12.5px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 5px;
    margin-right: 2px;
}

QMenuBar::item:selected {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: rgba(255, 255, 255, 0.12);
}

/* --- Floating Dark Glass Menus --- */
QMenu {
    background-color: #1b1c20;
    border: 1px solid #2d313a;
    border-radius: 8px;
    padding: 5px;
    color: #e2e8f0;
}

QMenu::item {
    padding: 6px 28px 6px 12px;
    border-radius: 5px;
    font-size: 12.5px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #64748b;
}

QMenu::separator {
    height: 1px;
    background-color: #2a2e37;
    margin: 4px 8px;
}

/* --- Modern Glass Action Toolbar --- */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(28, 30, 36, 0.95), stop:1 rgba(22, 23, 28, 0.95));
    border-top: none;
    border-left: none;
    border-right: none;
    border-bottom: 1px solid #262932;
    spacing: 4px;
    padding: 5px 8px;
}

QToolBar::separator {
    width: 1px;
    background-color: #2e333d;
    margin: 4px 6px;
}

QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #ffffff;
}

QToolButton:pressed {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QToolButton:checked {
    background-color: rgba(37, 99, 235, 0.25);
    border: 1px solid #3b82f6;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #252830;
    background-color: #17181c;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1a1c20;
    color: #94a3b8;
    padding: 7px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #252830;
    margin-right: 2px;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #22252c;
    color: #ffffff;
    border-bottom: 2px solid #3b82f6;
}

QTabBar::tab:hover:!selected {
    background-color: #1f2227;
    color: #cbd5e1;
}

/* --- Buttons --- */
QPushButton {
    background-color: #24272f;
    border: 1px solid #353944;
    border-radius: 6px;
    padding: 6px 14px;
    color: #f1f5f9;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2e323c;
    border-color: #474d5c;
}

QPushButton:pressed {
    background-color: #1b1d22;
}

QPushButton:disabled {
    background-color: #18191d;
    border-color: #252830;
    color: #64748b;
}

/* --- Inputs & Dropdowns --- */
QLineEdit, QComboBox, QSpinBox {
    background-color: #1a1c20;
    border: 1px solid #31353f;
    border-radius: 6px;
    padding: 5px 8px;
    color: #f8fafc;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
    background-color: #1f2127;
}

/* --- Tables & Lists --- */
QTableWidget, QTableView, QTreeView, QListWidget {
    background-color: #16171b;
    border: 1px solid #252830;
    border-radius: 6px;
    gridline-color: #202227;
    selection-background-color: #1d4ed8;
    selection-color: #ffffff;
    alternate-background-color: #191a1e;
}

QTableWidget::item, QTableView::item {
    padding: 4px 6px;
    border-bottom: 1px solid #1c1d22;
}

QHeaderView::section {
    background-color: #1b1d22;
    color: #94a3b8;
    padding: 7px;
    border: none;
    border-right: 1px solid #252830;
    border-bottom: 1px solid #252830;
    font-weight: 600;
    font-size: 11.5px;
    text-transform: uppercase;
}

/* --- Status Bar --- */
QStatusBar {
    background-color: #141518;
    color: #64748b;
    border-top: 1px solid #202227;
    padding: 3px 8px;
    font-size: 11.5px;
}

/* --- ScrollBars --- */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #2e323b;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #424754;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


def apply_dark_glass_theme(app_or_widget):
    app_or_widget.setStyleSheet(DARK_GLASS_STYLE)
