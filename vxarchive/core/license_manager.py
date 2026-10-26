"""
Commercial and Community edition licensing manager for VXArchive.
"""
import os
import json
from .utils import get_app_data_dir


class LicenseManager:
    """Handles licensing, registration state, and evaluation grace periods."""

    _instance = None

    def __init__(self):
        self.file_path = os.path.join(get_app_data_dir(), "license.json")
        self.registered_to = ""
        self.license_key = ""
        self.is_registered = False
        self.load()

    @classmethod
    def get_instance(cls) -> "LicenseManager":
        if cls._instance is None:
            cls._instance = LicenseManager()
        return cls._instance

    def load(self):
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.registered_to = data.get("registered_to", "")
                    self.license_key = data.get("license_key", "")
                    self.is_registered = bool(self.registered_to and self.license_key)
            except Exception:
                self.is_registered = False

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "registered_to": self.registered_to,
                    "license_key": self.license_key,
                    "is_registered": self.is_registered
                }, f, indent=2)
        except Exception:
            pass

    def register(self, user_name: str, key: str) -> bool:
        """Registers the software with the provided user name and key."""
        if not user_name or not key:
            return False
        self.registered_to = user_name.strip()
        self.license_key = key.strip()
        self.is_registered = True
        self.save()
        return True

    def unregister(self):
        self.registered_to = ""
        self.license_key = ""
        self.is_registered = False
        if os.path.isfile(self.file_path):
            try:
                os.remove(self.file_path)
            except Exception:
                pass
