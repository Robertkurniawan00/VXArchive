"""
Windows Virtual Disk Service ISO & VHD image mounting utility.
"""
import os
import subprocess
from typing import Tuple


class IsoMounter:
    """Mounts and unmounts ISO/VHD images using native Windows PowerShell / VDS."""

    @staticmethod
    def mount_image(image_path: str) -> Tuple[bool, str]:
        if not os.path.isfile(image_path):
            return False, f"Image file not found: {image_path}"

        norm = os.path.abspath(image_path)
        ps_cmd = f"Mount-DiskImage -ImagePath '{norm}' -PassThru | Get-Volume"
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if res.returncode == 0:
                return True, f"Mounted {norm} successfully"
            return False, res.stderr.strip() or "Failed to mount disk image"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def dismount_image(image_path: str) -> Tuple[bool, str]:
        if not os.path.isfile(image_path):
            return False, f"Image file not found: {image_path}"

        norm = os.path.abspath(image_path)
        ps_cmd = f"Dismount-DiskImage -ImagePath '{norm}'"
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if res.returncode == 0:
                return True, f"Dismounted {norm} successfully"
            return False, res.stderr.strip() or "Failed to dismount disk image"
        except Exception as e:
            return False, str(e)
