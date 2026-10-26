"""
Direct archive-to-archive format converter and re-compressor.
"""
import os
import tempfile
import zipfile
import tarfile
from typing import Tuple


class ArchiveTranscoder:
    """Converts archives from one container format to another directly."""

    def __init__(self, engine=None):
        self.engine = engine

    def convert(self, source_archive: str, target_format: str, output_path: str) -> Tuple[bool, str]:
        if not os.path.isfile(source_archive):
            return False, f"Source archive not found: {source_archive}"

        target_fmt = target_format.lower().lstrip(".")
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # Extract source
                if self.engine:
                    ok_ex, msg_ex = self.engine.extract_archive(source_archive, tmp_dir)
                    if not ok_ex:
                        # Fallback for zip
                        if zipfile.is_zipfile(source_archive):
                            with zipfile.ZipFile(source_archive, "r") as z:
                                z.extractall(tmp_dir)
                        else:
                            return False, f"Failed to unpack source archive: {msg_ex}"
                else:
                    if zipfile.is_zipfile(source_archive):
                        with zipfile.ZipFile(source_archive, "r") as z:
                            z.extractall(tmp_dir)
                    else:
                        return False, "No engine available to unpack source archive"

                # Repack to target format
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                items_to_pack = [os.path.join(tmp_dir, x) for x in os.listdir(tmp_dir)]

                if target_fmt == "zip":
                    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                        for root, _, files in os.walk(tmp_dir):
                            for f in files:
                                fp = os.path.join(root, f)
                                zf.write(fp, arcname=os.path.relpath(fp, tmp_dir))
                elif target_fmt in ("tar", "tar.gz", "tgz", "tar.bz2", "tbz"):
                    mode = "w"
                    if "gz" in target_fmt:
                        mode = "w:gz"
                    elif "bz2" in target_fmt:
                        mode = "w:bz2"
                    with tarfile.open(output_path, mode) as tf:
                        for root, _, files in os.walk(tmp_dir):
                            for f in files:
                                fp = os.path.join(root, f)
                                tf.add(fp, arcname=os.path.relpath(fp, tmp_dir))
                elif self.engine:
                    ok_comp, msg_comp = self.engine.create_archive(
                        output_archive=output_path,
                        files_to_add=items_to_pack,
                        archive_format=target_fmt
                    )
                    if not ok_comp:
                        return False, msg_comp
                else:
                    return False, f"Unsupported target format: {target_fmt}"

                return True, f"Successfully transcoded to {output_path}"
            except Exception as e:
                return False, f"Transcoding error: {str(e)}"
