"""
Bookmarks and Project Pinboard Manager for frequently accessed archive paths.
"""
import os
import json
from typing import List, Dict, Any, Optional
from .utils import get_app_data_dir


class BookmarkManager:
    """Stores pinned folders and recent archive hubs."""

    _instance = None

    def __init__(self):
        self.file_path = os.path.join(get_app_data_dir(), "bookmarks.json")
        self.bookmarks: List[Dict[str, Any]] = []
        self.load()

    @classmethod
    def get_instance(cls) -> "BookmarkManager":
        if cls._instance is None:
            cls._instance = BookmarkManager()
        return cls._instance

    def load(self):
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.bookmarks = json.load(f)
            except Exception:
                self.bookmarks = []
        else:
            self.bookmarks = []

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception:
            pass

    def add_bookmark(self, name: str, path: str, tag: str = "General", is_archive: bool = False):
        self.bookmarks.append({
            "name": name,
            "path": path,
            "tag": tag,
            "is_archive": is_archive
        })
        self.save()

    def remove_bookmark(self, index: int):
        if 0 <= index < len(self.bookmarks):
            self.bookmarks.pop(index)
            self.save()

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.bookmarks)
