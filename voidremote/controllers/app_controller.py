"""
Application controller - dependency injection root.

Owns all service instances and provides a unified facade used by
both the CLI and the GUI. This prevents duplication and ensures
a single ADB client is shared across the application.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from voidremote.adb.client import AdbClient, AdbNotFoundError
from voidremote.config.settings import AppSettings, get_settings
from voidremote.models.device import Device, PairingInfo
from voidremote.services.device_service import DeviceService
from voidremote.services.input_service import InputService, KeyCode
from voidremote.services.monitor_service import MonitorService, SnapshotCallback

logger = logging.getLogger(__name__)


class AppController:
    """
    Central application controller.

    Instantiate once at startup, then pass to CLI commands or the GUI.

    Example::

        ctrl = AppController()
        ctrl.initialize()
        devices = ctrl.list_devices()
    """

    def __init__(self, settings: Optional[AppSettings] = None) -> None:
        self._settings = settings or get_settings()
        self._adb = AdbClient(
            adb_path=self._settings.adb.path,
            default_timeout=self._settings.adb.command_timeout,
            server_port=self._settings.adb.server_port,
        )
        self._device_service = DeviceService(self._adb)
        self._input_service = InputService(self._adb)
        self._monitor_service = MonitorService(self._adb)
        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> str:
        """
        Initialize the controller — verify ADB, optionally start server.

        Returns:
            ADB version string.

        Raises:
            AdbNotFoundError: If ADB binary is not available.
        """
        version = self._adb.verify_adb()
        if self._settings.adb.auto_start_server:
            try:
                self._adb.start_server()
            except Exception as exc:
                logger.warning("Failed to start ADB server: %s", exc)
        self._initialized = True
        logger.info("AppController initialized, ADB: %s", version)
        return version

    def shutdown(self) -> None:
        """Graceful shutdown — stop monitors, optionally kill ADB."""
        self._monitor_service.stop_all()
        if self._settings.adb.kill_server_on_exit:
            try:
                self._adb.kill_server()
            except Exception as exc:
                logger.warning("Failed to kill ADB server on exit: %s", exc)
        logger.info("AppController shut down")

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------

    def list_devices(self, refresh: bool = True) -> list[Device]:
        """List connected devices, optionally refreshing first."""
        if refresh:
            return self._device_service.refresh_devices()
        return self._device_service.list_devices()

    def get_device(self, serial: str) -> Optional[Device]:
        """Get a specific device by serial."""
        return self._device_service.get_device(serial)

    def pair_device(self, host: str, port: int, code: str) -> bool:
        """Pair via wireless debugging."""
        return self._device_service.pair_device(host, port, code)

    def connect_device(
        self, host: str, port: int = 5555, remember: bool = True
    ) -> Device:
        """Connect to a wireless device."""
        return self._device_service.connect_device(host, port, remember)

    def disconnect_device(self, serial: str) -> bool:
        """Disconnect a wireless device."""
        return self._device_service.disconnect_device(serial)

    def auto_reconnect(self) -> list[Device]:
        """Reconnect all trusted auto-connect devices."""
        return self._device_service.auto_reconnect_trusted()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def tap(self, serial: str, x: int, y: int) -> None:
        self._input_service.tap(serial, x, y)

    def swipe(
        self,
        serial: str,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration_ms: int = 300,
    ) -> None:
        self._input_service.swipe(serial, x1, y1, x2, y2, duration_ms)

    def type_text(self, serial: str, text: str) -> None:
        self._input_service.type_text(serial, text)

    def key_event(self, serial: str, keycode: int) -> None:
        self._input_service.key_event(serial, keycode)

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def push_file(self, serial: str, local: Path, remote: str) -> None:
        """Push a local file to the device."""
        self._adb.push(serial, local, remote)

    def pull_file(self, serial: str, remote: str, local: Path) -> None:
        """Pull a file from the device."""
        self._adb.pull(serial, remote, local)

    # ------------------------------------------------------------------
    # APK management
    # ------------------------------------------------------------------

    def install_apk(self, serial: str, apk_path: Path, replace: bool = True) -> None:
        """Install an APK."""
        self._adb.install(serial, apk_path, replace=replace)

    def uninstall_app(self, serial: str, package: str) -> None:
        """Uninstall an app package."""
        self._adb.uninstall(serial, package)

    # ------------------------------------------------------------------
    # Screenshot & recording
    # ------------------------------------------------------------------

    def take_screenshot(self, serial: str, output: Path) -> Path:
        """Capture a screenshot and save to output path."""
        output.parent.mkdir(parents=True, exist_ok=True)
        self._adb.screenshot(serial, output)
        return output

    def start_screen_record(
        self, serial: str, remote_path: str = "/sdcard/void_rec.mp4"
    ) -> "subprocess.Popen[bytes]":  # noqa: F821
        return self._adb.screenrecord(serial, remote_path)

    # ------------------------------------------------------------------
    # Shell
    # ------------------------------------------------------------------

    def shell(self, serial: str, command: str) -> str:
        """Run an ADB shell command, return stdout."""
        return self._adb.shell(serial, command).stdout

    # ------------------------------------------------------------------
    # Reboot
    # ------------------------------------------------------------------

    def reboot(self, serial: str, mode: str = "") -> None:
        """Reboot device."""
        self._adb.reboot(serial, mode)

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def start_monitoring(
        self,
        serial: str,
        interval: float = 2.0,
        callback: Optional[SnapshotCallback] = None,
    ) -> None:
        """Start real-time monitoring for a device."""
        self._monitor_service.start(serial, interval, callback)

    def stop_monitoring(self, serial: str) -> None:
        """Stop monitoring a device."""
        self._monitor_service.stop(serial)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def settings(self) -> AppSettings:
        return self._settings

    @property
    def is_initialized(self) -> bool:
        return self._initialized
