"""
VXArchive main entry point and command-line handler.
"""
import sys
import os
from .core.archive_engine import ArchiveEngine


def handle_quick_compress(source_path: str, format_ext: str = "zip") -> int:
    """CLI handler for quick single-click compression (-az, -a7)."""
    if not os.path.exists(source_path):
        return 1
    engine = ArchiveEngine()
    base_name = os.path.splitext(os.path.basename(source_path))[0]
    folder = os.path.dirname(os.path.abspath(source_path))
    out_arc = os.path.join(folder, f"{base_name}.{format_ext.lstrip('.')}")
    ok, msg = engine.create_archive(out_arc, [source_path], archive_format=format_ext)
    return 0 if ok else 1


def handle_extract(archive_path: str, into_subfolder: bool = True, destination: str = None) -> int:
    """CLI handler for quick extraction (-x, -xd, -xs)."""
    if not os.path.isfile(archive_path):
        return 1
    engine = ArchiveEngine()
    folder = destination or os.path.dirname(os.path.abspath(archive_path))
    if into_subfolder:
        base_name = os.path.splitext(os.path.basename(archive_path))[0]
        dest_dir = os.path.join(folder, base_name)
    else:
        dest_dir = folder

    ok, msg = engine.extract_archive(archive_path, dest_dir)
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1:
        arg1 = sys.argv[1].lower()
        if arg1 in ("-az", "--zip") and len(sys.argv) > 2:
            sys.exit(handle_quick_compress(sys.argv[2], "zip"))
        elif arg1 in ("-a7", "--7z") and len(sys.argv) > 2:
            sys.exit(handle_quick_compress(sys.argv[2], "7z"))
        elif arg1 in ("-xd", "--subfolder") and len(sys.argv) > 2:
            sys.exit(handle_extract(sys.argv[2], into_subfolder=True))
        elif arg1 in ("-x", "--extract") and len(sys.argv) > 2:
            sys.exit(handle_extract(sys.argv[2], into_subfolder=False))

    from PyQt6.QtWidgets import QApplication
    from .gui.main_window import VXArchiveMainWindow

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    window = VXArchiveMainWindow()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        window.open_path(sys.argv[1])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
