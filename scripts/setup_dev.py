#!/usr/bin/env python3
"""
VoidRemote developer setup script.

Run this once after cloning to set up a complete development environment.

Usage:
    python scripts/setup_dev.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if check and result.returncode != 0:
        print(f"  ✗ Failed (exit {result.returncode})")
        sys.exit(result.returncode)
    return result


def check_python() -> None:
    print("Checking Python version…")
    if sys.version_info < (3, 12):
        print(f"  ✗ Python 3.12+ required, found {sys.version}")
        sys.exit(1)
    print(f"  ✓ Python {sys.version.split()[0]}")


def check_adb() -> None:
    print("Checking ADB…")
    adb = shutil.which("adb")
    if adb:
        result = subprocess.run(["adb", "version"], capture_output=True, text=True)
        print(f"  ✓ {result.stdout.splitlines()[0] if result.stdout else 'ADB found'}")
    else:
        print("  ⚠ ADB not found — install Android Platform Tools")
        print("    https://developer.android.com/tools/releases/platform-tools")


def install_deps() -> None:
    print("Installing dependencies…")
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])
    print("  ✓ All dependencies installed")


def install_precommit() -> None:
    print("Installing pre-commit hooks…")
    result = run([sys.executable, "-m", "pre_commit", "install"], check=False)
    if result.returncode == 0:
        print("  ✓ Pre-commit hooks installed")
    else:
        print("  ⚠ pre-commit not available — skipping hooks")


def run_tests() -> None:
    print("Running test suite…")
    result = run(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--no-header", "-q"],
        check=False,
    )
    if result.returncode == 0:
        print("  ✓ Tests passed")
    else:
        print("  ⚠ Some tests failed — check output above")


def create_dirs() -> None:
    print("Creating local directories…")
    (ROOT / "docs" / "screenshots").mkdir(parents=True, exist_ok=True)
    print("  ✓ Directories ready")


def main() -> None:
    print("=" * 60)
    print("  VoidRemote — Developer Setup")
    print("=" * 60)
    print()

    check_python()
    check_adb()
    create_dirs()
    install_deps()
    install_precommit()
    run_tests()

    print()
    print("=" * 60)
    print("  ✓ Setup complete!")
    print()
    print("  Quick start:")
    print("    voidremote doctor      # Check setup")
    print("    voidremote devices     # List devices")
    print("    voidremote-gui         # Launch GUI")
    print("    pytest tests/ -v       # Run all tests")
    print("=" * 60)


if __name__ == "__main__":
    main()
