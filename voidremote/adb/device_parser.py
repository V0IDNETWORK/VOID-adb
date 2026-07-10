"""
Parses ADB device listing and device property output into typed models.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from voidremote.models.device import (
    BatteryInfo,
    ConnectionType,
    CpuInfo,
    Device,
    DeviceCapability,
    DeviceInfo,
    DeviceState,
    NetworkInfo,
    StorageInfo,
)

logger = logging.getLogger(__name__)

# Regex for parsing `adb devices -l` output lines
_DEVICE_LINE_RE = re.compile(
    r"^(?P<serial>\S+)\s+(?P<state>\w+)(?:\s+(?P<attrs>.*))?$"
)
_ATTR_RE = re.compile(r"(\w+):(\S+)")

# Regex for parsing resolution from `wm size`
_RESOLUTION_RE = re.compile(r"Physical size:\s*(\d+)x(\d+)")
# Regex for parsing density from `wm density`
_DENSITY_RE = re.compile(r"Physical density:\s*(\d+)")
# Regex for parsing IP from `ip addr show wlan0`
_IP_RE = re.compile(r"inet\s+([\d.]+)/")
# Regex for parsing MemTotal from /proc/meminfo
_MEMTOTAL_RE = re.compile(r"MemTotal:\s+(\d+)\s+kB")
_MEMAVAIL_RE = re.compile(r"MemAvailable:\s+(\d+)\s+kB")


def parse_devices_output(raw: str) -> list[dict[str, str]]:
    """
    Parse the output of `adb devices -l` into a list of device dicts.

    Args:
        raw: Raw text output from `adb devices -l`.

    Returns:
        List of dicts with 'serial', 'state', and parsed attribute keys.
    """
    devices: list[dict[str, str]] = []
    lines = raw.strip().splitlines()

    for line in lines[1:]:  # skip "List of devices attached" header
        line = line.strip()
        if not line or line.startswith("*"):
            continue
        m = _DEVICE_LINE_RE.match(line)
        if not m:
            continue
        entry: dict[str, str] = {
            "serial": m.group("serial"),
            "state": m.group("state"),
        }
        attrs_raw = m.group("attrs") or ""
        for km in _ATTR_RE.finditer(attrs_raw):
            entry[km.group(1)] = km.group(2)
        devices.append(entry)

    return devices


def state_from_string(state_str: str) -> DeviceState:
    """Map ADB state string to DeviceState enum."""
    mapping: dict[str, DeviceState] = {
        "device": DeviceState.ONLINE,
        "offline": DeviceState.OFFLINE,
        "unauthorized": DeviceState.UNAUTHORIZED,
        "connecting": DeviceState.CONNECTING,
    }
    return mapping.get(state_str.lower(), DeviceState.UNKNOWN)


def connection_type_from_serial(serial: str) -> ConnectionType:
    """Infer connection type from device serial."""
    if re.match(r"^\d+\.\d+\.\d+\.\d+:\d+$", serial):
        return ConnectionType.WIRELESS
    if re.match(r"^emulator-\d+$", serial):
        return ConnectionType.EMULATOR
    return ConnectionType.USB


def parse_battery(raw: str) -> BatteryInfo:
    """Parse output of `dumpsys battery` into BatteryInfo."""
    info = BatteryInfo()

    def _int(pattern: str) -> int:
        m = re.search(pattern, raw, re.IGNORECASE)
        return int(m.group(1)) if m else 0

    def _bool(pattern: str) -> bool:
        m = re.search(pattern, raw, re.IGNORECASE)
        if not m:
            return False
        return m.group(1).strip().lower() == "true"

    info.level = _int(r"level:\s*(\d+)")
    info.is_charging = _bool(r"status:\s*(\w+)") or "charging" in raw.lower()
    info.is_ac_powered = _bool(r"AC powered:\s*(true|false)")
    info.is_usb_powered = _bool(r"USB powered:\s*(true|false)")
    info.voltage = float(_int(r"voltage:\s*(\d+)"))
    info.temperature = float(_int(r"temperature:\s*(\d+)"))

    health_m = re.search(r"health:\s*(\d+)", raw)
    if health_m:
        health_codes = {1: "unknown", 2: "good", 3: "overheat",
                        4: "dead", 5: "over voltage", 6: "unspecified failure", 7: "cold"}
        info.health = health_codes.get(int(health_m.group(1)), "unknown")

    tech_m = re.search(r"technology:\s*(\S+)", raw)
    if tech_m:
        info.technology = tech_m.group(1)

    return info


def parse_storage(raw_df: str) -> StorageInfo:
    """Parse output of `df /data` or similar into StorageInfo."""
    info = StorageInfo()
    lines = raw_df.strip().splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 6:
            try:
                # Typical: Filesystem 1K-blocks Used Available Use% Mounted
                total_kb = int(parts[1])
                used_kb = int(parts[2])
                avail_kb = int(parts[3])
                mount = parts[5] if len(parts) > 5 else "/data"
                info.total_bytes = total_kb * 1024
                info.used_bytes = used_kb * 1024
                info.available_bytes = avail_kb * 1024
                info.mount_point = mount
                break
            except (ValueError, IndexError):
                continue
    return info


def parse_screen_resolution(wm_size_output: str) -> tuple[int, int]:
    """Parse `wm size` output, return (width, height)."""
    m = _RESOLUTION_RE.search(wm_size_output)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 0, 0


def parse_density(wm_density_output: str) -> int:
    """Parse `wm density` output, return DPI."""
    m = _DENSITY_RE.search(wm_density_output)
    return int(m.group(1)) if m else 0


def parse_ip_address(ip_addr_output: str) -> str:
    """Parse IP from `ip addr show wlan0`."""
    m = _IP_RE.search(ip_addr_output)
    return m.group(1) if m else ""


def parse_meminfo(meminfo: str) -> tuple[int, int]:
    """Parse /proc/meminfo, return (total_bytes, available_bytes)."""
    total_kb = 0
    avail_kb = 0
    tm = _MEMTOTAL_RE.search(meminfo)
    am = _MEMAVAIL_RE.search(meminfo)
    if tm:
        total_kb = int(tm.group(1))
    if am:
        avail_kb = int(am.group(1))
    return total_kb * 1024, avail_kb * 1024


def parse_cpu_abi(getprop_output: str) -> CpuInfo:
    """Build CpuInfo from getprop ro.product.cpu.abi."""
    info = CpuInfo()
    info.abi = getprop_output.strip() or "unknown"
    return info


def build_device_from_raw(
    serial: str,
    state_str: str,
    props: dict[str, str],
    extended_info: Optional[dict[str, str]] = None,
) -> Device:
    """
    Construct a Device object from parsed ADB data.

    Args:
        serial: Device serial.
        state_str: ADB state string.
        props: Dict of getprop values.
        extended_info: Optional additional parsed values.

    Returns:
        Populated Device instance.
    """
    ext = extended_info or {}
    cpu = CpuInfo(
        abi=props.get("ro.product.cpu.abi", "unknown"),
        abi_list=props.get("ro.product.cpu.abilist", "").split(","),
    )

    network = NetworkInfo(
        ip_address=ext.get("ip_address", ""),
        wifi_ssid=ext.get("wifi_ssid", ""),
    )

    battery_raw = ext.get("battery_raw", "")
    battery = parse_battery(battery_raw) if battery_raw else BatteryInfo()

    storage_raw = ext.get("storage_raw", "")
    storage = parse_storage(storage_raw) if storage_raw else StorageInfo()

    width, height = 0, 0
    if "resolution" in ext:
        width, height = parse_screen_resolution(ext["resolution"])

    total_ram, avail_ram = 0, 0
    if "meminfo" in ext:
        total_ram, avail_ram = parse_meminfo(ext["meminfo"])

    info = DeviceInfo(
        serial=serial,
        model=props.get("ro.product.model", "Unknown"),
        manufacturer=props.get("ro.product.manufacturer", "Unknown"),
        brand=props.get("ro.product.brand", "Unknown"),
        product=props.get("ro.product.name", "Unknown"),
        device_name=props.get("ro.product.device", "Unknown"),
        android_version=props.get("ro.build.version.release", "Unknown"),
        sdk_version=int(props.get("ro.build.version.sdk", "0") or "0"),
        build_id=props.get("ro.build.id", "Unknown"),
        build_fingerprint=props.get("ro.build.fingerprint", ""),
        screen_width=width,
        screen_height=height,
        screen_density=parse_density(ext.get("density", "")),
        battery=battery,
        storage=storage,
        cpu=cpu,
        network=network,
        ram_total_bytes=total_ram,
        ram_available_bytes=avail_ram,
    )

    conn_type = connection_type_from_serial(serial)
    host, port = "", 5555
    if conn_type == ConnectionType.WIRELESS and ":" in serial:
        parts = serial.rsplit(":", 1)
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            port = 5555

    # All online devices get base capabilities
    caps: list[DeviceCapability] = []
    if state_str == "device":
        caps = [
            DeviceCapability.SHELL,
            DeviceCapability.FILE_TRANSFER,
            DeviceCapability.INPUT_CONTROL,
            DeviceCapability.PACKAGE_MANAGER,
            DeviceCapability.MONITORING,
        ]
        if info.sdk_version >= 21:
            caps.append(DeviceCapability.SCREEN_MIRROR)

    return Device(
        info=info,
        state=state_from_string(state_str),
        connection_type=conn_type,
        host=host,
        port=port,
        capabilities=caps,
    )
