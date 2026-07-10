"""
VoidRemote — Basic Usage Examples

Demonstrates programmatic use of VoidRemote as a Python library.
These examples require an ADB-connected Android device.

Usage:
    python examples/basic_usage.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from voidremote.controllers.app_controller import AppController
from voidremote.config.settings import AppSettings
from voidremote.utils.logging import setup_logging

# Set up logging
setup_logging(level="INFO", console=True)
logger = logging.getLogger(__name__)


def example_list_devices(ctrl: AppController) -> None:
    """List all connected devices and print their info."""
    print("\n=== Connected Devices ===")
    devices = ctrl.list_devices(refresh=True)
    if not devices:
        print("No devices connected.")
        return
    for device in devices:
        info = device.info
        print(f"  {info.display_name}")
        print(f"    Serial:   {device.serial}")
        print(f"    Android:  {info.android_version} (SDK {info.sdk_version})")
        print(f"    Battery:  {info.battery.level}%")
        print(f"    IP:       {info.network.ip_address}")
        print(f"    State:    {device.state.value}")


def example_take_screenshot(ctrl: AppController, serial: str) -> None:
    """Take a screenshot and save it to the current directory."""
    print(f"\n=== Screenshot ({serial}) ===")
    output = Path("screenshot_example.png")
    ctrl.take_screenshot(serial, output)
    print(f"  Saved to: {output.resolve()}")


def example_input_control(ctrl: AppController, serial: str) -> None:
    """Demonstrate various input controls."""
    print(f"\n=== Input Control ({serial}) ===")

    # Press Home
    print("  Pressing HOME…")
    ctrl.key_event(serial, 3)

    import time
    time.sleep(0.5)

    # Tap in the center (1080x2400 device)
    print("  Tapping center of screen…")
    ctrl.tap(serial, 540, 1200)
    time.sleep(0.3)

    # Swipe up (scroll down)
    print("  Swiping up…")
    ctrl.swipe(serial, 540, 1600, 540, 400, duration_ms=400)
    time.sleep(0.5)

    print("  Input demonstration complete")


def example_shell_command(ctrl: AppController, serial: str) -> None:
    """Execute shell commands and display output."""
    print(f"\n=== Shell Commands ({serial}) ===")

    commands = [
        ("Android version", "getprop ro.build.version.release"),
        ("Device model", "getprop ro.product.model"),
        ("Uptime", "uptime"),
        ("Free memory (MB)", "free -m | grep Mem"),
    ]

    for label, cmd in commands:
        output = ctrl.shell(serial, cmd).strip()
        print(f"  {label}: {output}")


def example_automation(ctrl: AppController, serial: str) -> None:
    """Record and play a simple macro."""
    from voidremote.core.automation import Macro, MacroPlayer, MacroRecorder, MacroLibrary, MacroStep

    print(f"\n=== Automation ({serial}) ===")

    # Build a macro manually
    macro = Macro(
        name="open_settings",
        description="Opens Android Settings",
        steps=[
            MacroStep("keyevent", {"keycode": 3}, delay_after=0.5),   # Home
            MacroStep("keyevent", {"keycode": 3}, delay_after=0.5),   # Home (double)
            MacroStep("shell_cmd", {"cmd": "am start -a android.settings.SETTINGS"}, delay_after=1.0),
        ]
    )

    # Save to library
    lib_dir = Path("examples/macros")
    lib = MacroLibrary(lib_dir)
    lib.save(macro)
    print(f"  Saved macro '{macro.name}' to {lib_dir}")

    # List saved macros
    print(f"  Saved macros: {lib.list_macros()}")

    # Play it back
    player = MacroPlayer(ctrl)
    print(f"  Playing macro '{macro.name}'…")
    # player.play(macro, serial)  # Uncomment to actually run
    print("  (Playback skipped in example — uncomment to run)")


def example_monitoring(ctrl: AppController, serial: str) -> None:
    """Demonstrate the monitoring service."""
    import time
    from voidremote.services.monitor_service import DeviceSnapshot

    print(f"\n=== Monitoring ({serial}) ===")
    snapshots: list[DeviceSnapshot] = []

    def on_snapshot(snap: DeviceSnapshot) -> None:
        snapshots.append(snap)
        print(
            f"  CPU: {snap.cpu_usage:.1f}%  "
            f"RAM: {snap.ram_used_mb:.0f}/{snap.ram_total_mb:.0f}MB  "
            f"Battery: {snap.battery_level}%  "
            f"Temp: {snap.battery_temperature:.1f}°C"
        )

    ctrl.start_monitoring(serial, interval=2.0, callback=on_snapshot)
    print("  Monitoring for 6 seconds…")
    time.sleep(6)
    ctrl.stop_monitoring(serial)
    print(f"  Collected {len(snapshots)} snapshots")


def main() -> None:
    """Run all examples against the first connected device."""
    settings = AppSettings()
    ctrl = AppController(settings)

    try:
        version = ctrl.initialize()
        print(f"ADB ready: {version}")
    except Exception as exc:
        print(f"ADB initialization failed: {exc}")
        print("Make sure ADB is installed and accessible.")
        return

    devices = ctrl.list_devices(refresh=True)
    example_list_devices(ctrl)

    if not devices:
        print("\nNo devices to demonstrate further examples with.")
        return

    # Use the first available online device
    online = [d for d in devices if d.is_connected]
    if not online:
        print("\nNo online devices found.")
        return

    serial = online[0].serial
    print(f"\nUsing device: {online[0].info.display_name} ({serial})")

    # Run examples
    example_shell_command(ctrl, serial)
    # example_take_screenshot(ctrl, serial)   # Uncomment to run
    # example_input_control(ctrl, serial)     # Uncomment to run
    # example_automation(ctrl, serial)        # Uncomment to run
    # example_monitoring(ctrl, serial)        # Uncomment to run

    ctrl.shutdown()
    print("\n✓ Examples complete")


if __name__ == "__main__":
    main()
