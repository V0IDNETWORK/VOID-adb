#!/usr/bin/env python3
"""
VoidRemote build script.

Handles wheel building, standalone executable creation, and release packaging.

Usage:
    python scripts/build.py wheel          # Build Python wheel
    python scripts/build.py exe            # Build standalone executable (PyInstaller)
    python scripts/build.py clean          # Remove build artifacts
    python scripts/build.py all            # Build everything
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"  ✗ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    print(f"  ✓ Done")


def cmd_clean() -> None:
    """Remove all build artifacts."""
    print("Cleaning build artifacts…")
    for d in (DIST, BUILD, ROOT / "*.egg-info"):
        for path in ROOT.glob(str(d.relative_to(ROOT))):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed: {path}")
    for pattern in ("**/__pycache__", "**/*.pyc", "**/*.pyo"):
        for p in ROOT.glob(pattern):
            if p.is_dir():
                shutil.rmtree(p)
            elif p.is_file():
                p.unlink()
    print("  ✓ Clean complete")


def cmd_wheel() -> None:
    """Build Python wheel and source distribution."""
    print("Building wheel…")
    run([sys.executable, "-m", "build", "--wheel", "--sdist"])
    wheels = list(DIST.glob("*.whl"))
    if wheels:
        print(f"  ✓ Wheel: {wheels[0].name}")


def cmd_exe() -> None:
    """Build standalone executable using PyInstaller."""
    print("Building standalone executable…")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("  Installing PyInstaller…")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['{ROOT / "voidremote" / "ui" / "app.py"}'],
    pathex=['{ROOT}'],
    binaries=[],
    datas=[
        ('{ROOT / "voidremote" / "assets"}', 'voidremote/assets'),
    ],
    hiddenimports=[
        'voidremote',
        'voidremote.cli',
        'voidremote.ui',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoidRemote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    spec_path = ROOT / "VoidRemote.spec"
    spec_path.write_text(spec_content)
    run([sys.executable, "-m", "PyInstaller", str(spec_path), "--clean", "--noconfirm"])
    print(f"  ✓ Executable in: {DIST}")


def cmd_all() -> None:
    cmd_clean()
    cmd_wheel()
    print("\n✓ All builds complete. Artifacts in:", DIST)


COMMANDS = {
    "clean": cmd_clean,
    "wheel": cmd_wheel,
    "exe": cmd_exe,
    "all": cmd_all,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python build.py [{' | '.join(COMMANDS)}]")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
