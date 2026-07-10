"""
Device management service.

Provides high-level operations over the ADB client: device discovery,
pairing, connection, info retrieval, and trusted device persistence.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from voidremote.adb.client import AdbClient, AdbError
from voidremote.adb.device_parser import (
    build_device_from_raw,
    parse_devices_output,
)
from voidremote.config.settings import TRUSTED_DEVICES_FILE
from voidremote.models.device import (
    ConnectionConfig,
    Device,
    DeviceState,
    PairingInfo,
    TrustedDevice,
)
from voidremote.utils.security import validate_host, validate_port

logger = logging.getLogger(__name__)


class DeviceService:
    """
    Orchestrates device discovery, connection, and persistent state.

    This is the primary interface used by both the CLI and GUI to interact
    with Android devices.
    """

    def __init__(self, adb: AdbClient) -> None:
        self._adb = adb
        self._devices: dict[str, Device] = {}
        self._trusted: dict[str, TrustedDevice] = {}
        self._load_trusted_devices()

    # ------------------------------------------------------------------
    # Device discovery
    # ------------------------------------------------------------------

    def refresh_devices(self) -> list[Device]:
        """
        Refresh the list of connected ADB devices.

        Returns:
            List of current Device objects.
        """
        raw = self._adb.list_devices_raw()
        entries = parse_devices_output(raw)
        discovered: dict[str, Device] = {}

        for entry in entries:
            serial = entry["serial"]
            state = entry["state"]
            try:
                device = self._get_device_with_info(serial, state)
                discovered[serial] = device
            except Exception as exc:
                logger.warning("Failed to get info for %s: %s", serial, exc)
                # Still add with minimal info
                existing = self._devices.get(serial)
                if existing:
                    discovered[serial] = existing
                continue

        self._devices = discovered
        logger.debug("Refreshed devices: %d found", len(self._devices))
        return list(self._devices.values())

    def get_device(self, serial: str) -> Optional[Device]:
        """Return device by serial, or None if not found."""
        return self._devices.get(serial)

    def list_devices(self) -> list[Device]:
        """Return currently cached device list."""
        return list(self._devices.values())

    # ------------------------------------------------------------------
    # Pairing & connection
    # ------------------------------------------------------------------

    def pair_device(self, host: str, port: int, code: str) -> bool:
        """
        Pair a device over wireless debugging.

        Args:
            host: Device IP address.
            port: Pairing port (shown in wireless debug settings).
            code: 6-digit pairing code.

        Returns:
            True if pairing succeeded.

        Raises:
            AdbError: If pairing fails.
            ValueError: If parameters are invalid.
        """
        validated_host = validate_host(host)
        validated_port = validate_port(port)
        pairing = PairingInfo(
            host=validated_host,
            port=validated_port,
            pairing_code=code,
        )
        result = self._adb.pair(pairing)
        success = "successfully paired" in result.stdout.lower()
        if success:
            logger.info("Paired successfully with %s:%d", validated_host, validated_port)
        return success

    def connect_device(
        self,
        host: str,
        port: int = 5555,
        remember: bool = True,
    ) -> Device:
        """
        Connect to an Android device over TCP/IP.

        Args:
            host: Device IP address.
            port: ADB TCP port (default 5555).
            remember: Whether to add device to trusted list.

        Returns:
            The connected Device object.

        Raises:
            AdbError: If connection fails.
        """
        validated_host = validate_host(host)
        validated_port = validate_port(port)
        config = ConnectionConfig(host=validated_host, port=validated_port)
        self._adb.connect(config)

        # Refresh to get real device info
        self.refresh_devices()
        serial = f"{validated_host}:{validated_port}"
        device = self._devices.get(serial)

        if device is None:
            raise AdbError(f"Device {serial} not found after connect")

        if remember:
            self._save_trusted(device)

        return device

    def disconnect_device(self, serial: str) -> bool:
        """
        Disconnect a wireless device.

        Args:
            serial: Device serial (host:port format).

        Returns:
            True if disconnect succeeded.
        """
        if ":" not in serial:
            logger.warning("disconnect_device called on USB device %s — skipping", serial)
            return False
        host, port_str = serial.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            port = 5555
        self._adb.disconnect(host, port)
        if serial in self._devices:
            self._devices[serial].state = DeviceState.DISCONNECTED
        return True

    # ------------------------------------------------------------------
    # Device info
    # ------------------------------------------------------------------

    def _get_device_with_info(self, serial: str, state: str) -> Device:
        """Build a Device with extended info from getprop & other sources."""
        props: dict[str, str] = {}
        extended: dict[str, str] = {}

        if state == "device":
            try:
                props = self._fetch_getprop(serial)
            except Exception as exc:
                logger.warning("getprop failed for %s: %s", serial, exc)

            try:
                extended["battery_raw"] = self._adb.shell(
                    serial, "dumpsys battery"
                ).stdout
            except Exception:
                pass

            try:
                extended["resolution"] = self._adb.shell(
                    serial, "wm size"
                ).stdout
            except Exception:
                pass

            try:
                extended["density"] = self._adb.shell(
                    serial, "wm density"
                ).stdout
            except Exception:
                pass

            try:
                extended["meminfo"] = self._adb.shell(
                    serial, "cat /proc/meminfo"
                ).stdout
            except Exception:
                pass

            try:
                extended["ip_address"] = self._parse_ip(serial)
            except Exception:
                pass

            try:
                extended["storage_raw"] = self._adb.shell(
                    serial, "df /data"
                ).stdout
            except Exception:
                pass

        device = build_device_from_raw(serial, state, props, extended)
        return device

    def _fetch_getprop(self, serial: str) -> dict[str, str]:
        """Fetch all device properties via getprop."""
        result = self._adb.shell(serial, "getprop")
        props: dict[str, str] = {}
        for line in result.stdout.splitlines():
            m = __import__("re").match(r"\[([^\]]+)\]:\s*\[([^\]]*)\]", line)
            if m:
                props[m.group(1)] = m.group(2)
        return props

    def _parse_ip(self, serial: str) -> str:
        """Get the device's wlan0 IP address."""
        from voidremote.adb.device_parser import parse_ip_address
        result = self._adb.shell(serial, "ip addr show wlan0")
        return parse_ip_address(result.stdout)

    # ------------------------------------------------------------------
    # Trusted devices
    # ------------------------------------------------------------------

    def _save_trusted(self, device: Device) -> None:
        """Persist a device to the trusted devices store."""
        serial = device.serial
        trusted = TrustedDevice(
            serial=serial,
            host=device.host,
            port=device.port,
            alias=device.alias,
            last_connected=datetime.now(),
        )
        self._trusted[serial] = trusted
        self._persist_trusted()
        logger.debug("Saved trusted device: %s", serial)

    def _load_trusted_devices(self) -> None:
        """Load trusted devices from disk."""
        if not TRUSTED_DEVICES_FILE.exists():
            return
        try:
            data: list[dict] = json.loads(
                TRUSTED_DEVICES_FILE.read_text(encoding="utf-8")
            )
            for entry in data:
                td = TrustedDevice(**entry)
                self._trusted[td.serial] = td
            logger.debug("Loaded %d trusted devices", len(self._trusted))
        except Exception as exc:
            logger.warning("Failed to load trusted devices: %s", exc)

    def _persist_trusted(self) -> None:
        """Write trusted devices to disk."""
        TRUSTED_DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
        entries = []
        for td in self._trusted.values():
            entry = {
                "serial": td.serial,
                "host": td.host,
                "port": td.port,
                "alias": td.alias,
                "last_connected": (
                    td.last_connected.isoformat() if td.last_connected else None
                ),
                "auto_connect": td.auto_connect,
                "tags": td.tags,
            }
            entries.append(entry)
        TRUSTED_DEVICES_FILE.write_text(
            json.dumps(entries, indent=2), encoding="utf-8"
        )

    def list_trusted_devices(self) -> list[TrustedDevice]:
        """Return all trusted devices."""
        return list(self._trusted.values())

    def forget_device(self, serial: str) -> bool:
        """Remove a device from the trusted list."""
        if serial in self._trusted:
            del self._trusted[serial]
            self._persist_trusted()
            return True
        return False

    def auto_reconnect_trusted(self) -> list[Device]:
        """
        Attempt to reconnect all auto_connect trusted devices.

        Returns:
            List of successfully reconnected devices.
        """
        reconnected: list[Device] = []
        for td in self._trusted.values():
            if not td.auto_connect or not td.host:
                continue
            try:
                device = self.connect_device(td.host, td.port, remember=False)
                reconnected.append(device)
                logger.info("Auto-reconnected: %s", td.serial)
            except Exception as exc:
                logger.debug("Auto-reconnect failed for %s: %s", td.serial, exc)
        return reconnected
