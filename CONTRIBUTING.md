# Contributing to Smart Check-In

Thank you for your interest in contributing to **Smart Check-In: Enhancing College Bus Attendance with RFID**! We welcome contributions that improve hardware driver reliability, enhance software architecture, optimize cloud sync performance, or add documentation.

To ensure a smooth process, please follow these guidelines.

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and professional environment.

---

## How Can I Contribute?

### 1. Reporting Bugs
- Search the open issues to ensure the bug hasn't already been reported.
- If you find a new bug, please open a new issue using our **Bug Report Template**.
- Provide a clear description of the bug, including step-by-step instructions to reproduce it, hardware setup configurations, and software log outputs if applicable.

### 2. Proposing Features
- If you have an idea for a feature or enhancement, open a new issue using our **Feature Request Template**.
- Describe the utility, target hardware modules, and workflow adjustments.

### 3. Submitting Pull Requests (PR)
- Fork the repository and create your branch from `main`.
  ```bash
  git checkout -b feature/your-awesome-feature
  ```
- Write clean, documented Python code. If you are adding hardware support, ensure it includes fallback simulations for non-Raspberry Pi environments.
- Format your code to match the standard Python PEP 8 styling conventions.
- Test your changes:
  - If physical hardware is available, verify with hardware components.
  - If running in emulation, run the script to ensure zero runtime issues.
- Commit your changes with descriptive commit messages:
  ```bash
  git commit -m "feat: add support for LCD backlight auto-timeout"
  ```
- Push to your fork and submit a Pull Request to our main repository. Refer to the **Pull Request Template** when submitting.

---

## Git Commit Style Guide

Please follow this structure for commit messages:
- `feat:` for new features (e.g. adding GSM alerts).
- `fix:` for bug fixes.
- `docs:` for documentation changes.
- `refactor:` for code cleanups without behavioral changes.
- `style:` for formatting and whitespace updates.
- `test:` for adding or updating tests.
