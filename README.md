# VXArchive

A modern, high-performance archive manager, compression suite, and shell integration for Windows 10 and 11. Built with PyQt6 and native Windows 11 Desktop Window Manager (DWM) hardware-accelerated Mica materials.

---

## ⚡ Highlights

- **Smart Password Memory & Pattern Auto-Unlock**: Never re-enter passwords for release series. Remembers passwords per-file and recognizes bracket tags (e.g. `[kuyhaa.me]galaxy.rar` and `[kuyhaa.me] milyway.rar`), domain prefixes, and multi-part sets (`.part*.rar`), auto-unlocking subsequent archives in the background (~15ms).
- **Universal Format Support**: Full support for `.rar`, `.7z`, `.zip`, `.tar`, `.gz`, `.bz2`, `.xz`, `.iso`, `.cab`, `.wim`, `.jar`, `.apk`, and multi-part split volumes.
- **Windows 11 Native Mica & Dark Mode**: Authentic DWM Mica Alt / Acrylic materials, dark titlebar caption, native rounded window corners, and subtle accent borders via `dwmapi.dll`.
- **Archive Sanitizer & Smart Layout Optimizer**: Automated detection and removal of cross-platform clutter (macOS `__MACOSX`, `.DS_Store`, Windows `Thumbs.db`, `desktop.ini`, development dependencies `node_modules`, `__pycache__`, `.venv`, and duplicate payloads). Includes anti-mess extraction preventing double `Folder/Folder` nesting and loose desktop flooding.
- **Deep In-Archive Grep**: Search plain text, source code, and regular expressions directly inside compressed archives without extraction.
- **Archive Health Checker & Integrity Self-Test**: Validates CRC32 checksums, stream integrity, and header consistency across entire archives with detailed reporting.
- **DoD 5220.22-M Secure File Shredder**: Permanent 3-pass cryptographic wipe with metadata obfuscation.
- **Multi-Volume Splitter & Missing Chunk Relocator**: Splits large files using presets (Discord, Telegram, FAT32) and detects missing volume sequence chunks.
- **Instant LAN File Transfer**: Micro-server with QR code broadcast for downloading archives across local Wi-Fi without cloud dependencies.
- **Standalone SFX Studio**: Compiles archives into self-extracting standalone Windows `.exe` binaries.
- **Full Windows Explorer Integration**: Cascaded submenus with high-resolution vector icons, file associations, and 1-click system shell integration.
- **Zip Slip & Path Traversal Protection**: Secure extraction path validation preventing arbitrary file overwrite attacks.

---

## Architecture Overview

```
VXArchive/
├── vxarchive/
│   ├── bin/                    # Bundled 64-bit 7z binaries (7z.exe, 7z.dll, 7z.sfx)
│   ├── core/                   # Core business logic and compression engines
│   │   ├── archive_engine.py   # Primary unified archive engine (7z CLI + Python fallback)
│   │   ├── sanitizer.py        # Archive Sanitizer & Anti-Mess layout resolver
│   │   ├── health_checker.py   # Archive integrity and CRC32 verification engine
│   │   ├── archive_grep.py     # In-archive regex & text grep engine
│   │   ├── archive_repair.py   # Corrupt archive header reconstruction engine
│   │   ├── batch_processor.py  # Batch multi-archive extraction & compression
│   │   ├── benchmark.py        # Hardware CPU & compression benchmark
│   │   ├── bookmarks.py        # Project pins and location bookmarks manager
│   │   ├── dedup_analyzer.py   # Duplicate payload and storage waste analyzer
│   │   ├── diff_sync.py        # Archive vs. folder delta comparator and sync
│   │   ├── hasher.py           # Cryptographic hash calculator (SHA256, MD5, CRC32)
│   │   ├── iso_mounter.py      # Windows Virtual Disk Service ISO/VHD mounter
│   │   ├── lan_share.py        # Local network HTTP micro-server & QR code generator
│   │   ├── license_manager.py  # Commercial registration manager
│   │   ├── metadata_inspector.py# Deep file metadata & EXIF inspector
│   │   ├── password_memory.py  # Smart release password memory & pattern matching
│   │   ├── password_vault.py   # Encrypted password vault
│   │   ├── sfx_builder.py      # Standalone self-extracting executable compiler
│   │   ├── shell_integration.py# Windows Explorer context menu & file associations
│   │   ├── shredder.py         # DoD 5220.22-M multi-pass secure file shredder
│   │   ├── splitter.py         # Multi-part volume splitter, detector & merger
│   │   ├── steganography.py    # Steganographic archive embedding in images
│   │   ├── threat_scanner.py   # Double extension & decompression bomb scanner
│   │   ├── transcoder.py       # Direct archive-to-archive format converter
│   │   └── utils.py            # Unified formatting, AppData resolution & path security
│   ├── gui/                    # PyQt6 presentation layer & dialogs
│   │   ├── glass_theme.py      # Dark glass styling tokens and QSS stylesheets
│   │   ├── icons.py            # High-DPI resolution-independent vector icon engine
│   │   ├── mica_effect.py      # Native Windows 11 DWM backdrop API wrapper
│   │   ├── main_window.py      # Main multi-tab application window
│   │   ├── tab_page.py         # Archive & directory browser tab
│   │   └── dialog_*.py         # Dedicated modal dialogs
│   └── main.py                 # Application entry point and CLI handler
├── dist/                       # Compiled standalone Windows executable distribution
├── test_vxarchive.py           # Core engine automated test suite
├── test_gui.py                 # GUI components automated test suite
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── VXArchive.spec              # PyInstaller build specification
```

---

## Requirements

- **Operating System**: Windows 10 (1903+) or Windows 11 (64-bit recommended).
- **Python**: 3.10 or higher.
- **Dependencies**: Listed in `requirements.txt`.

---

## Installation & Running from Source

1. Clone or download the repository:
   ```bash
   git clone https://github.com/username/VXArchive.git
   cd VXArchive
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python vxarchive/main.py
   ```
   Or double-click `run_vxarchive.bat`.

---

## Command Line Interface (CLI)

VXArchive supports direct command-line arguments for system context menus and automation:

| Command | Action |
|---|---|
| `VXArchive.exe <path>` | Opens archive or directory in a new browser tab |
| `VXArchive.exe -xs <archive>` | **Smart Extract (Sanitized)**: Auto-resolves nested folders and strips OS ghosts |
| `VXArchive.exe -x <archive>` | Extracts archive contents to current folder |
| `VXArchive.exe -xd <archive>` | Extracts archive contents into a named subfolder |
| `VXArchive.exe -e <archive>` | Opens interactive extraction destination dialog |
| `VXArchive.exe -a <target>` | Opens Add to Archive dialog |
| `VXArchive.exe -az <target>` | 1-Click quick compression to `.zip` |
| `VXArchive.exe -a7 <target>` | 1-Click high compression to `.7z` |
| `VXArchive.exe -sanitize <archive>` | Opens the Archive Sanitizer dialog |

---

## Windows Explorer Shell Integration

Register VXArchive as the default archiver and enable Explorer right-click cascading menus:

1. Open **Tools > System Integration & File Associations...** inside VXArchive.
2. Select your desired file extensions and context menu entries.
3. Click **Apply Default Integration**.

Alternatively, run:
```cmd
Apply_VXArchive_Integration.bat
```
To remove integration cleanly at any time, run:
```cmd
Remove_System_Integration.bat
```

---

## Building Standalone Executable

To compile a standalone binary (`dist/VXArchive/VXArchive.exe`) with PyInstaller:

```bash
pyinstaller VXArchive.spec --noconfirm
```

Then copy required assets into `dist/VXArchive`:
```bash
python -c "import shutil; shutil.copy('vxarchive.ico', 'dist/VXArchive/vxarchive.ico'); shutil.copytree('vxarchive/bin', 'dist/VXArchive/bin', dirs_exist_ok=True)"
```

---

## Testing

The automated test suite verifies 100% of core engines, security validations, and GUI dialogs:

```bash
python -m unittest test_vxarchive.py test_gui.py
```

Expected result:
```
Ran 67 tests in ~18s
OK
```

---

## Security & Privacy

- **Zip Slip Defense**: Path traversal attacks (e.g. `../../evil.exe`) are actively blocked during extraction.
- **Local Configuration**: Passwords and bookmarks are stored in `%APPDATA%\VXArchive` on the local machine and never transmitted externally.
- **DoD Shredder**: Passes 3 random and complement data sweeps before unlinking disk allocation blocks.
- **Decompression Bomb Guard**: Warns before decompressing files with abnormal compression ratios.

---

## License

This project is licensed under the [MIT License](LICENSE).
