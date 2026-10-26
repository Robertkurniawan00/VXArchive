"""
Windows 11 DWM Mica Alt and Dark Mode backdrop effects via dwmapi.dll.
"""
import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QWidget


def apply_windows_11_mica(widget: QWidget, backdrop_type: str = "mica_alt",
                           dark_mode: bool = True, rounded_corners: bool = True) -> bool:
    """Applies Windows 11 DWM backdrop effects (Mica, Mica Alt, Acrylic) to a QWidget."""
    if sys.platform != "win32":
        return False

    try:
        hwnd = int(widget.winId())
        dwmapi = ctypes.windll.dwmapi

        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        dark_val = ctypes.c_int(1 if dark_mode else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark_val),
            ctypes.sizeof(dark_val)
        )

        # DWMWA_WINDOW_CORNER_PREFERENCE = 33 (2 = ROUND)
        if rounded_corners:
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            corner_val = ctypes.c_int(2)
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(corner_val),
                ctypes.sizeof(corner_val)
            )

        # DWMWA_SYSTEMBACKDROP_TYPE = 38 (3 = Acrylic, 2 = Mica, 4 = Mica Alt)
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        backdrop_map = {
            "none": 1,
            "mica": 2,
            "acrylic": 3,
            "mica_alt": 4
        }
        b_val = ctypes.c_int(backdrop_map.get(backdrop_type.lower(), 4))
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(b_val),
            ctypes.sizeof(b_val)
        )
        return True
    except Exception:
        return False
