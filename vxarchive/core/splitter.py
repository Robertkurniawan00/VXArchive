"""
Multi-volume archive splitting, sequence detection, and missing chunk locator.
"""
import os
import re
import shutil
from typing import List, Tuple, Dict, Any, Optional


class VolumeSplitter:
    """Splits large files into multi-part chunk sets and rejoins them."""

    PRESETS = {
        "Discord (25 MB)": 25 * 1024 * 1024,
        "Discord Nitro (500 MB)": 500 * 1024 * 1024,
        "Telegram (2 GB)": 2 * 1024 * 1024 * 1024,
        "FAT32 (4 GB)": 4 * 1024 * 1024 * 1024,
        "DVD-R (4.7 GB)": int(4.7 * 1024 * 1024 * 1024),
        "Custom...": 0
    }

    @staticmethod
    def split_file(source_file: str, chunk_size_bytes: int, output_dir: Optional[str] = None) -> List[str]:
        if not os.path.isfile(source_file) or chunk_size_bytes <= 0:
            return []

        out_folder = output_dir or os.path.dirname(os.path.abspath(source_file))
        os.makedirs(out_folder, exist_ok=True)
        base_name = os.path.basename(source_file)

        created_parts = []
        part_idx = 1
        with open(source_file, "rb") as src:
            while True:
                chunk = src.read(chunk_size_bytes)
                if not chunk:
                    break
                part_name = f"{base_name}.{part_idx:03d}"
                part_path = os.path.join(out_folder, part_name)
                with open(part_path, "wb") as dst:
                    dst.write(chunk)
                created_parts.append(part_path)
                part_idx += 1

        return created_parts

    @staticmethod
    def join_volumes(first_part_path: str, output_file: Optional[str] = None) -> Tuple[bool, str]:
        if not os.path.isfile(first_part_path):
            return False, "First volume part not found"

        folder = os.path.dirname(os.path.abspath(first_part_path))
        base_first = os.path.basename(first_part_path)

        match = re.search(r"^(.*?)\.(\d{3})$", base_first, re.IGNORECASE)
        if not match:
            match = re.search(r"^(.*?)\.part0*1\.(rar|7z)$", base_first, re.IGNORECASE)
            if not match:
                return False, "Unrecognized split volume format"

        if not output_file:
            cleaned_target = match.group(1)
            output_file = os.path.join(folder, cleaned_target)

        all_parts = []
        idx = 1
        while True:
            candidate = os.path.join(folder, f"{match.group(1)}.{idx:03d}")
            if not os.path.isfile(candidate):
                ext = match.group(2) if len(match.groups()) > 1 else "rar"
                candidate = os.path.join(folder, f"{match.group(1)}.part{idx}.{ext}")
                if not os.path.isfile(candidate):
                    break
            all_parts.append(candidate)
            idx += 1

        if not all_parts:
            return False, "No volume parts detected"

        try:
            with open(output_file, "wb") as out_f:
                for p in all_parts:
                    with open(p, "rb") as in_f:
                        while buf := in_f.read(65536):
                            out_f.write(buf)
            return True, f"Successfully joined {len(all_parts)} parts into {output_file}"
        except Exception as e:
            return False, f"Failed to join volumes: {str(e)}"


class MissingPart:
    def __init__(self, part_number: int, expected_name: str):
        self.part_number = part_number
        self.expected_name = expected_name


class VolumeSet:
    def __init__(self, total_parts: int, is_complete: bool, missing_parts: List[MissingPart], parts: List[str]):
        self.total_parts = total_parts
        self.is_complete = is_complete
        self.missing_parts = missing_parts
        self.parts = parts


class MultiVolumeDetector:
    """Detects multi-volume sequence gaps and missing chunks in sets."""

    PATTERNS = [
        r"^(.*?)\.part(\d+)\.(rar|7z|zip)$",
        r"^(.*?)\.(\d{3})$",
        r"^(.*?)\.(r\d{2})$"
    ]

    @staticmethod
    def is_multi_volume_file(filename: str) -> bool:
        base = os.path.basename(filename)
        for pat in MultiVolumeDetector.PATTERNS:
            if re.search(pat, base, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def inspect_volume_set(file_path: str) -> Optional[VolumeSet]:
        if not os.path.isfile(file_path):
            return None

        folder = os.path.dirname(os.path.abspath(file_path))
        base = os.path.basename(file_path)

        m = re.match(r"^(.*?)\.part(\d+)\.(rar|7z|zip)$", base, re.IGNORECASE)
        if m:
            stem, _, ext = m.group(1), m.group(2), m.group(3)
            # Find all parts in folder
            existing = {}
            for f in os.listdir(folder):
                m_sub = re.match(r"^" + re.escape(stem) + r"\.part(\d+)\." + re.escape(ext) + r"$", f, re.IGNORECASE)
                if m_sub:
                    num = int(m_sub.group(1))
                    existing[num] = os.path.join(folder, f)

            if not existing:
                return None

            max_num = max(existing.keys())
            missing = []
            for n in range(1, max_num + 1):
                if n not in existing:
                    exp_name = f"{stem}.part{n}.{ext}"
                    missing.append(MissingPart(n, exp_name))

            return VolumeSet(
                total_parts=max_num,
                is_complete=(len(missing) == 0),
                missing_parts=missing,
                parts=[existing[k] for k in sorted(existing.keys())]
            )

        m2 = re.match(r"^(.*?)\.(\d{3})$", base, re.IGNORECASE)
        if m2:
            stem, _ = m2.group(1), m2.group(2)
            existing = {}
            for f in os.listdir(folder):
                m_sub = re.match(r"^" + re.escape(stem) + r"\.(\d{3})$", f, re.IGNORECASE)
                if m_sub:
                    num = int(m_sub.group(1))
                    existing[num] = os.path.join(folder, f)

            if not existing:
                return None

            max_num = max(existing.keys())
            missing = []
            for n in range(1, max_num + 1):
                if n not in existing:
                    exp_name = f"{stem}.{n:03d}"
                    missing.append(MissingPart(n, exp_name))

            return VolumeSet(
                total_parts=max_num,
                is_complete=(len(missing) == 0),
                missing_parts=missing,
                parts=[existing[k] for k in sorted(existing.keys())]
            )

        return None

    @staticmethod
    def relocate_part(missing_part: MissingPart, chosen_source_path: str, target_folder: str, method: str = "copy") -> Tuple[bool, str]:
        if not os.path.isfile(chosen_source_path):
            return False, "Source missing part not found"

        os.makedirs(target_folder, exist_ok=True)
        dest_path = os.path.join(target_folder, missing_part.expected_name)

        try:
            if method == "copy":
                shutil.copy2(chosen_source_path, dest_path)
            else:
                shutil.move(chosen_source_path, dest_path)
            return True, dest_path
        except Exception as e:
            return False, str(e)
