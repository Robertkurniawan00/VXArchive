"""
Encrypted / persistent password vault for VXArchive.
"""
import os
import json
from typing import List, Dict, Optional
from .utils import get_app_data_dir


class PasswordVault:
    """Manages remembered passwords and encryption keys for automated unpacking."""

    _instance = None

    def __init__(self):
        self.file_path = os.path.join(get_app_data_dir(), "password_vault.json")
        self.items: List[Dict[str, str]] = []
        self.load()

    @classmethod
    def get_instance(cls) -> "PasswordVault":
        if cls._instance is None:
            cls._instance = PasswordVault()
        return cls._instance

    def load(self):
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            except Exception:
                self.items = []
        else:
            self.items = []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.items, f, indent=2)
        except Exception:
            pass

    def add_password(self, label: str, password: str):
        self.remove_password(label)
        self.items.append({"label": label, "password": password})
        self.save()

    def update_password(self, old_label: str, new_label: str, new_password: str):
        found = False
        for item in self.items:
            if item.get("label") == old_label:
                item["label"] = new_label
                item["password"] = new_password
                found = True
                break
        if not found:
            self.add_password(new_label, new_password)
        else:
            self.save()

    def remove_password(self, label: str):
        self.items = [item for item in self.items if item.get("label") != label]
        self.save()

    def get_all(self) -> List[Dict[str, str]]:
        return list(self.items)

    def find_password(self, label: str) -> Optional[str]:
        for item in self.items:
            if item.get("label") == label:
                return item.get("password")
        return None
