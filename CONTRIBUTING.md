# Contributing to VXArchive

Thank you for your interest in contributing to VXArchive! We welcome community contributions, bug reports, and feature proposals.

---

## How to Contribute

### 1. Reporting Bugs
- Search existing issues to ensure the bug hasn't already been reported.
- Open an issue with clear reproduction steps, your Windows version, and sample archive details (without including sensitive passwords/data).

### 2. Suggesting Features
- Open a feature request issue describing the workflow improvement or tool capability.
- Explain why traditional tools like VXArchive or 7-Zip lack this feature and how it benefits users.

### 3. Code Contributions
1. Fork the repository and create a feature branch (`git checkout -b feature/amazing-feature`).
2. Adhere to clean, readable Python code standards without bloated dependencies or AI slop.
3. Ensure all automated tests pass:
   ```bash
   python -m unittest test_vxarchive.py test_gui.py
   ```
4. Commit your changes with clear messages (`git commit -m 'Add: smart pattern extraction for multi-volume archives'`).
5. Push to your branch and submit a Pull Request.

---

## Code of Conduct
Please be polite, constructive, and respectful in all issues and pull requests.
