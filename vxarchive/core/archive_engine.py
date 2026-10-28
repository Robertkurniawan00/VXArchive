"""
ArchiveItem and ArchiveEngine for listing, creating, extracting, and modifying archives.
"""
import os
import sys
import subprocess
import zipfile
import tarfile
import json
import zlib
from typing import List, Tuple, Optional, Any
from pathlib import Path


class ArchiveItem:
    def __init__(self, path: str = "", name: str = "", is_dir: bool = False,
                 size: int = 0, packed_size: int = 0, mtime: str = "",
                 crc: str = "", attributes: str = ""):
        self.path = path.replace("\\", "/")
        self.name = name or (path.split("/")[-1] if "/" in path else path)
        self.is_dir = is_dir
        self.size = size
        self.packed_size = packed_size
        self.mtime = mtime
        self.crc = crc
        self.attributes = attributes


class ArchiveEngine:
    """Primary unified archive engine supporting ZIP, 7Z, TAR, RAR, and ISO."""

    def __init__(self):
        # Locate bundled 7z or system 7z
        candidates = []
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", "")
            if meipass:
                candidates.append(os.path.join(meipass, "bin", "7z.exe"))
                candidates.append(os.path.join(meipass, "vxarchive", "bin", "7z.exe"))
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, "bin", "7z.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", "bin", "7z.exe"))

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates.append(os.path.join(base_dir, "bin", "7z.exe"))
        candidates.append(os.path.join(os.path.dirname(base_dir), "bin", "7z.exe"))

        self.seven_zip_bin = "7z.exe"
        for cand in candidates:
            if cand and os.path.isfile(cand):
                self.seven_zip_bin = cand
                break

    def list_archive_contents(self, archive_path: str, password: Optional[str] = None) -> List[ArchiveItem]:
        items = []
        if not os.path.isfile(archive_path):
            return items

        # 1. Native zipfile
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    if password:
                        zf.setpassword(password.encode("utf-8"))
                    for info in zf.infolist():
                        is_dir = info.is_dir()
                        p = info.filename.rstrip("/")
                        nm = os.path.basename(p) if not is_dir else os.path.basename(p) + "/"
                        crc_str = f"{info.CRC & 0xFFFFFFFF:08X}"
                        dt = f"{info.date_time[0]}-{info.date_time[1]:02d}-{info.date_time[2]:02d} {info.date_time[3]:02d}:{info.date_time[4]:02d}"
                        items.append(ArchiveItem(
                            path=info.filename,
                            name=nm,
                            is_dir=is_dir,
                            size=info.file_size,
                            packed_size=info.compress_size,
                            mtime=dt,
                            crc=crc_str,
                            attributes="D..." if is_dir else "....A"
                        ))
                return items
            except Exception:
                pass

        # 2. 7z fallback CLI
        try:
            cmd = [self.seven_zip_bin, "l", "-slt", archive_path]
            if password:
                cmd.append(f"-p{password}")
            proc = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            if proc.returncode == 0:
                cur: dict = {}
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        if "Path" in cur and cur.get("Path") != archive_path:
                            is_d = cur.get("Folder", "-") == "+" or cur.get("Attributes", "").startswith("D")
                            p = cur.get("Path", "")
                            nm = os.path.basename(p) if not is_d else os.path.basename(p) + "/"
                            items.append(ArchiveItem(
                                path=p,
                                name=nm,
                                is_dir=is_d,
                                size=int(cur.get("Size", 0)),
                                packed_size=int(cur.get("Packed Size", 0)),
                                mtime=cur.get("Modified", ""),
                                crc=cur.get("CRC", ""),
                                attributes=cur.get("Attributes", "")
                            ))
                        cur = {}
                    elif "=" in line:
                        k, v = line.split("=", 1)
                        cur[k.strip()] = v.strip()
        except Exception:
            pass

        return items

    def create_archive(self, output_archive: str, files_to_add: List[str],
                       archive_format: str = "zip", password: Optional[str] = None,
                       compression_level: int = 5) -> Tuple[bool, str]:
        os.makedirs(os.path.dirname(os.path.abspath(output_archive)), exist_ok=True)
        fmt = archive_format.lower().lstrip(".")

        if fmt == "zip" and not password:
            try:
                with zipfile.ZipFile(output_archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    for item in files_to_add:
                        if os.path.isfile(item):
                            zf.write(item, arcname=os.path.basename(item))
                        elif os.path.isdir(item):
                            for root, _, files in os.walk(item):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    zf.write(fp, arcname=os.path.relpath(fp, os.path.dirname(item)))
                return True, f"Successfully created {output_archive}"
            except Exception as e:
                return False, str(e)

        # Use 7z CLI for general format or password encryption
        try:
            cmd = [self.seven_zip_bin, "a", output_archive]
            if password:
                cmd.append(f"-p{password}")
                cmd.append("-mhe=on")  # encrypt headers
            cmd.extend(files_to_add)
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                return True, f"Successfully created {output_archive}"
            return False, proc.stderr.strip() or "Compression failed"
        except Exception as e:
            return False, str(e)

    def extract_archive(self, archive_path: str, destination_dir: str,
                        password: Optional[str] = None, items: Optional[List[str]] = None) -> Tuple[bool, str]:
        os.makedirs(destination_dir, exist_ok=True)

        if zipfile.is_zipfile(archive_path) and not password:
            try:
                with zipfile.ZipFile(archive_path, "r") as zf:
                    if items:
                        for it in items:
                            zf.extract(it, destination_dir)
                    else:
                        zf.extractall(destination_dir)
                return True, f"Extracted to {destination_dir}"
            except Exception as e:
                return False, str(e)

        # 7z CLI extraction
        try:
            cmd = [self.seven_zip_bin, "x", archive_path, f"-o{destination_dir}", "-y"]
            if password:
                cmd.append(f"-p{password}")
            if items:
                cmd.extend(items)
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                return True, f"Extracted to {destination_dir}"
            return False, proc.stderr.strip() or "Extraction failed"
        except Exception as e:
            return False, str(e)

    def delete_items_from_archive(self, archive_path: str, items_to_delete: List[str]) -> Tuple[bool, str]:
        if not os.path.isfile(archive_path):
            return False, "Archive not found"

        del_set = set(items_to_delete)
        if zipfile.is_zipfile(archive_path):
            try:
                tmp_out = archive_path + ".tmp_del"
                with zipfile.ZipFile(archive_path, "r") as z_in:
                    with zipfile.ZipFile(tmp_out, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
                        for info in z_in.infolist():
                            if info.filename not in del_set and info.filename.rstrip("/") not in del_set:
                                z_out.writestr(info, z_in.read(info.filename))
                os.replace(tmp_out, archive_path)
                return True, "Items deleted successfully"
            except Exception as e:
                return False, str(e)

        return False, "Unsupported archive format for deletion"

    def set_comment(self, archive_path: str, comment: str) -> Tuple[bool, str]:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "a") as z:
                    z.comment = comment.encode("utf-8")
                return True, "Comment set successfully"
            except Exception as e:
                return False, str(e)
        return False, "Unsupported archive format"

    def get_comment(self, archive_path: str) -> str:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    return z.comment.decode("utf-8", errors="ignore")
            except Exception:
                pass
        return ""

    def create_recovery_record(self, archive_path: str, redundancy_percent: int = 5) -> Tuple[bool, str, str]:
        rec_path = archive_path + ".vxrev"
        try:
            with open(archive_path, "rb") as f:
                data = f.read()

            import hashlib
            parity_sha = hashlib.sha256(data).hexdigest()
            slice_count = max(1, len(data) // 65536)

            rec_data = {
                "archive": os.path.basename(archive_path),
                "redundancy_percent": redundancy_percent,
                "parity_sha256": parity_sha,
                "slice_count": slice_count,
                "size": len(data)
            }
            with open(rec_path, "w", encoding="utf-8") as f:
                json.dump(rec_data, f, indent=2)
            return True, "Recovery record created", rec_path
        except Exception as e:
            return False, str(e), ""

    def verify_password(self, archive_path: str, password: str) -> bool:
        if zipfile.is_zipfile(archive_path):
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    pwd_bytes = password.encode("utf-8") if isinstance(password, str) else password
                    z.setpassword(pwd_bytes)
                    infolist = z.infolist()
                    if not infolist:
                        return True
                    z.read(infolist[0].filename)
                    return True
            except Exception:
                pass

        try:
            if self.seven_zip_bin:
                cmd = [self.seven_zip_bin, "t", archive_path, f"-p{password}", "-y"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                return res.returncode == 0
        except Exception:
            pass
        return False

    def find_working_password(self, archive_path: str) -> Optional[Tuple[str, str]]:
        from .password_memory import ArchivePasswordMemory
        mem = ArchivePasswordMemory.get_instance()
        candidates = mem.get_candidates_for_file(archive_path)

        for pwd, reason in candidates:
            if self.verify_password(archive_path, pwd):
                return pwd, reason
        return None
