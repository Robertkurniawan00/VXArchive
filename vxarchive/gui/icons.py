"""
Vector and high-DPI icon engine for VXArchive toolbars and trees.
"""
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt


class IconEngine:
    @staticmethod
    def get_icon(name: str) -> QIcon:
        pix = QPixmap(24, 24)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color_map = {
            "folder": QColor("#eab308"),
            "archive": QColor("#3b82f6"),
            "file": QColor("#94a3b8"),
            "add": QColor("#22c55e"),
            "extract": QColor("#f97316"),
            "test": QColor("#06b6d4"),
            "delete": QColor("#ef4444"),
            "info": QColor("#8b5cf6")
        }
        c = color_map.get(name.lower(), QColor("#64748b"))
        painter.setBrush(c)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(2, 2, 20, 20, 4, 4)
        painter.end()

        return QIcon(pix)
