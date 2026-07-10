"""VoidRemote ADB communication layer."""

from voidremote.adb.client import AdbClient, AdbCommandResult, AdbError, AdbNotFoundError
from voidremote.adb.device_parser import (
    build_device_from_raw,
    parse_battery,
    parse_devices_output,
    parse_ip_address,
    parse_meminfo,
    parse_screen_resolution,
    parse_storage,
    state_from_string,
)

__all__ = [
    "AdbClient",
    "AdbCommandResult",
    "AdbError",
    "AdbNotFoundError",
    "build_device_from_raw",
    "parse_battery",
    "parse_devices_output",
    "parse_ip_address",
    "parse_meminfo",
    "parse_screen_resolution",
    "parse_storage",
    "state_from_string",
]
