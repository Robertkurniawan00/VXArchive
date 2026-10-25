# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

---

## Security Guarantees & Built-in Defenses

VXArchive is designed with local data privacy and defensive compression standards:
- **Zip Slip & Path Traversal Protection**: Actively checks and neutralizes malicious relative paths (e.g. `../../evil.exe`).
- **Decompression Bomb Guard**: Analyzes compression ratios before expanding payloads to prevent system memory exhaustion.
- **Local-Only Password Storage**: Remembered archive passwords and vaults are stored exclusively on your local machine (`%APPDATA%\VXArchive`) with obfuscation. No passwords or filenames are ever sent over the internet.
- **Offline LAN Share**: The built-in micro-server operates strictly over the local private subnet (Wi-Fi/LAN) with no cloud relays.

---

## Reporting a Vulnerability

If you discover a security vulnerability within VXArchive, please do not open a public issue. Instead, report it privately via GitHub Security Advisories or email the maintainer. We will address verified security reports promptly.
