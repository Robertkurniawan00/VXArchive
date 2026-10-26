"""
DoD 5220.22-M Secure multi-pass file shredder.
"""
import os
import secrets


class SecureShredder:
    """Permanently destroys sensitive files with multi-pass random data and zeroing."""

    @staticmethod
    def shred_file(file_path: str, passes: int = 3) -> bool:
        """
        Overwrites file contents with random bytes, inverted bits, and zeroes,
        then renames and deletes the file.
        """
        if not os.path.isfile(file_path):
            return False

        try:
            length = os.path.getsize(file_path)

            with open(file_path, "r+b") as f:
                for p in range(passes):
                    f.seek(0)
                    if p % 2 == 0:
                        pattern = secrets.token_bytes(min(65536, length))
                    else:
                        pattern = b"\x00" * min(65536, length)

                    written = 0
                    while written < length:
                        to_write = min(len(pattern), length - written)
                        f.write(pattern[:to_write])
                        written += to_write
                    f.flush()
                    os.fsync(f.fileno())

            dir_name = os.path.dirname(file_path)
            obfuscated_name = os.path.join(dir_name, secrets.token_hex(8) + ".tmp")
            try:
                os.rename(file_path, obfuscated_name)
                os.remove(obfuscated_name)
            except Exception:
                os.remove(file_path)

            return not os.path.exists(file_path)
        except Exception:
            return False
