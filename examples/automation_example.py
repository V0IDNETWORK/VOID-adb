"""
VoidRemote — Automation / Macro Example

Demonstrates recording and playing back an automation script.

Usage:
    python examples/automation_example.py <device_serial>
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from voidremote.config.settings import AppSettings
from voidremote.controllers.app_controller import AppController
from voidremote.core.automation import Macro, MacroLibrary, MacroPlayer, MacroStep
from voidremote.utils.logging import setup_logging

setup_logging(level="INFO")


def build_whatsapp_search_macro() -> Macro:
    """
    Example macro: open WhatsApp and search for a contact.
    Adjust coordinates for your screen resolution.
    """
    return Macro(
        name="whatsapp_open_search",
        description="Opens WhatsApp and taps the search icon",
        repeat=1,
        steps=[
            # Press Home first
            MacroStep("keyevent", {"keycode": 3}, delay_after=0.5),
            # Open WhatsApp (replace with actual coordinates or use am start)
            MacroStep("tap", {"x": 540, "y": 1200}, delay_after=1.0),
            # Tap search icon (top-right area — adjust for your device)
            MacroStep("tap", {"x": 950, "y": 120}, delay_after=0.5),
            # Type a name
            MacroStep("text", {"text": "Alice"}, delay_after=0.3),
        ],
    )


def main() -> None:
    serial = sys.argv[1] if len(sys.argv) > 1 else None

    ctrl = AppController(AppSettings())
    try:
        ctrl.initialize()
    except Exception as exc:
        print(f"ADB error: {exc}")
        sys.exit(1)

    if serial is None:
        devices = ctrl.list_devices(refresh=True)
        online = [d for d in devices if d.is_connected]
        if not online:
            print("No online devices found.")
            sys.exit(1)
        serial = online[0].serial

    print(f"Target device: {serial}")

    lib_dir = Path("examples/macros")
    lib = MacroLibrary(lib_dir)

    # Build and save macro
    macro = build_whatsapp_search_macro()
    saved_path = lib.save(macro)
    print(f"Macro saved: {saved_path}")

    # List macros
    print(f"Available macros: {lib.list_macros()}")

    # Load and play
    loaded = lib.load(macro.name)
    print(f"Playing macro '{loaded.name}' ({len(loaded.steps)} steps)…")

    player = MacroPlayer(ctrl)
    # Uncomment to actually execute:
    # player.play(loaded, serial, speed=1.0)
    print("(Dry run — uncomment player.play() to execute)")

    ctrl.shutdown()


if __name__ == "__main__":
    main()
