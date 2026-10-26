"""
Pattern-based password auto-unlock and memory engine for archive series.
"""
import os
import re
import json
import fnmatch
from typing import List, Tuple, Optional, Dict
from .utils import get_app_data_dir


class ArchivePasswordMemory:
    """Remembers passwords for specific files, bracket tags, domains, and multi-part sets."""

    _instance = None

    def __init__(self):
        self.file_path = os.path.join(str(get_app_data_dir()), "remembered_passwords.json")
        self.exact_files: Dict[str, str] = {}
        self.patterns: Dict[str, str] = {}
        self.load()

    @classmethod
    def get_instance(cls) -> "ArchivePasswordMemory":
        if cls._instance is None:
            cls._instance = ArchivePasswordMemory()
        return cls._instance

    def load(self):
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.exact_files = data.get("exact_files", {})
                    self.patterns = data.get("patterns", {})
            except Exception:
                self.exact_files = {}
                self.patterns = {}
        else:
            self.exact_files = {}
            self.patterns = {}

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "exact_files": self.exact_files,
                    "patterns": self.patterns
                }, f, indent=2)
        except Exception:
            pass

    def extract_pattern_candidates(self, filename: str) -> List[str]:
        """Extracts candidate wildcard patterns from bracket tags, domain prefixes, and multi-part sets."""
        base_name = os.path.basename(filename)
        candidates = []

        bracket_m = re.match(r"^(\[[^\]]+\])", base_name)
        if bracket_m:
            candidates.append(f"{bracket_m.group(1)}*")

        paren_m = re.match(r"^(\([^\)]+\))", base_name)
        if paren_m:
            candidates.append(f"{paren_m.group(1)}*")

        # Delimiter pattern (e.g. kuyhaa.me_autocad.rar -> kuyhaa.me*)
        delimit_m = re.match(r"^([a-zA-Z0-9.\-]+?)[_ \-]", base_name)
        if delimit_m:
            cand = f"{delimit_m.group(1)}*"
            if cand not in candidates:
                candidates.append(cand)

        part_m = re.sub(r"\.part\d+\.rar$", ".part*.rar", base_name, flags=re.IGNORECASE)
        if part_m != base_name and part_m not in candidates:
            candidates.append(part_m)

        return candidates

    def match_pattern(self, pattern: str, filename: str) -> bool:
        """Tests if a filename matches a given wildcard pattern, preserving bracket tags."""
        base = os.path.basename(filename)
        pat = pattern

        # Custom regex translation treating brackets literally
        regex_pat = "^"
        i = 0
        while i < len(pat):
            c = pat[i]
            if c == "*":
                regex_pat += ".*"
            elif c == "?":
                regex_pat += "."
            elif c in r"[](){}.+^$|\/":
                regex_pat += "\\" + c
            else:
                regex_pat += c
            i += 1
        regex_pat += "$"

        return bool(re.match(regex_pat, base, re.IGNORECASE))

    def remember_password(self, file_path: str, password: str, remember_file: bool = True, pattern: Optional[str] = None):
        """Stores password for exact file path and/or general pattern."""
        if remember_file and file_path:
            norm_path = os.path.abspath(file_path).lower()
            self.exact_files[norm_path] = password

        if pattern:
            self.patterns[pattern] = password

        self.save()

    def get_candidates_for_file(self, file_path: str) -> List[Tuple[str, str]]:
        """Returns ordered list of (password, reason) candidate tuples."""
        results = []
        norm_path = os.path.abspath(file_path).lower()

        if norm_path in self.exact_files:
            results.append((self.exact_files[norm_path], "Exact File Match"))

        base_name = os.path.basename(file_path)
        for pat, pwd in self.patterns.items():
            if self.match_pattern(pat, base_name):
                results.append((pwd, pat))

        from .password_vault import PasswordVault
        vault = PasswordVault.get_instance()
        for item in vault.get_all():
            pwd = item.get("password")
            if pwd and not any(r[0] == pwd for r in results):
                results.append((pwd, f"Vault: {item.get('label')}"))

        return results
