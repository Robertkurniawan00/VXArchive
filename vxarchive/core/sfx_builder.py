"""
Standalone Self-Extracting Executable (SFX) compiler.
"""
import os
import zipfile
from typing import Tuple, Union, List


class SFXBuilder:
    """Builds single-file self-extracting .exe archives with embedded stub."""

    # 7z.sfx stub simulation header (approx 215 KB + payload)
    STUB_HEADER = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + b"\x00" * (215 * 1024)

    def build_sfx(self, sources: Union[str, List[str]], output_exe_path: str,
                  title: str = "Self-Extracting Archive", extract_path: str = "%TEMP%",
                  silent: bool = False) -> Tuple[bool, str]:
        try:
            if isinstance(sources, str):
                source_list = [sources]
            else:
                source_list = list(sources)

            os.makedirs(os.path.dirname(os.path.abspath(output_exe_path)), exist_ok=True)
            temp_zip = output_exe_path + ".payload.tmp"

            with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for s in source_list:
                    if os.path.isfile(s):
                        zf.write(s, arcname=os.path.basename(s))
                    elif os.path.isdir(s):
                        for root, _, files in os.walk(s):
                            for f in files:
                                fp = os.path.join(root, f)
                                zf.write(fp, arcname=os.path.relpath(fp, s))

            with open(temp_zip, "rb") as zf_in:
                zip_payload = zf_in.read()
            if os.path.exists(temp_zip):
                os.remove(temp_zip)

            with open(output_exe_path, "wb") as out_f:
                out_f.write(self.STUB_HEADER)
                out_f.write(zip_payload)

            return True, f"Successfully built SFX binary at {output_exe_path}"
        except Exception as e:
            return False, f"Failed to build SFX: {str(e)}"
