"""Unit tests for ADB device output parsing."""

from __future__ import annotations

import pytest

from voidremote.adb.device_parser import (
    connection_type_from_serial,
    parse_battery,
    parse_devices_output,
    parse_ip_address,
    parse_meminfo,
    parse_screen_resolution,
    parse_storage,
    state_from_string,
)
from voidremote.models.device import ConnectionType, DeviceState


class TestParseDevicesOutput:
    SAMPLE_OUTPUT = (
        "List of devices attached\n"
        "192.168.1.50:5555\tdevice product:pixel6 model:Pixel_6 device:pixel6\n"
        "emulator-5554\toffline\n"
        "ABC123XYZ\tunauthorized\n"
    )

    def test_parses_three_devices(self) -> None:
        devices = parse_devices_output(self.SAMPLE_OUTPUT)
        assert len(devices) == 3

    def test_wireless_device(self) -> None:
        devices = parse_devices_output(self.SAMPLE_OUTPUT)
        d = devices[0]
        assert d["serial"] == "192.168.1.50:5555"
        assert d["state"] == "device"
        assert d["model"] == "Pixel_6"

    def test_offline_device(self) -> None:
        devices = parse_devices_output(self.SAMPLE_OUTPUT)
        assert devices[1]["state"] == "offline"

    def test_unauthorized_device(self) -> None:
        devices = parse_devices_output(self.SAMPLE_OUTPUT)
        assert devices[2]["state"] == "unauthorized"

    def test_empty_output(self) -> None:
        devices = parse_devices_output("List of devices attached\n")
        assert devices == []

    def test_skips_daemon_messages(self) -> None:
        output = (
            "List of devices attached\n"
            "* daemon not running; starting now at tcp:5037\n"
            "192.168.1.1:5555\tdevice\n"
        )
        devices = parse_devices_output(output)
        assert len(devices) == 1


class TestStateFromString:
    def test_device(self) -> None:
        assert state_from_string("device") == DeviceState.ONLINE

    def test_offline(self) -> None:
        assert state_from_string("offline") == DeviceState.OFFLINE

    def test_unauthorized(self) -> None:
        assert state_from_string("unauthorized") == DeviceState.UNAUTHORIZED

    def test_unknown(self) -> None:
        assert state_from_string("something_else") == DeviceState.UNKNOWN

    def test_case_insensitive(self) -> None:
        assert state_from_string("DEVICE") == DeviceState.ONLINE


class TestConnectionTypeFromSerial:
    def test_wireless_ip_port(self) -> None:
        assert connection_type_from_serial("192.168.1.1:5555") == ConnectionType.WIRELESS

    def test_emulator(self) -> None:
        assert connection_type_from_serial("emulator-5554") == ConnectionType.EMULATOR

    def test_usb(self) -> None:
        assert connection_type_from_serial("ABC123DEF456") == ConnectionType.USB


class TestParseBattery:
    SAMPLE = """
Current Battery Service state:
  AC powered: false
  USB powered: true
  status: 2
  health: 2
  present: true
  level: 85
  scale: 100
  voltage: 4250
  temperature: 310
  technology: Li-ion
"""

    def test_level(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.level == 85

    def test_usb_powered(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.is_usb_powered is True

    def test_ac_not_powered(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.is_ac_powered is False

    def test_voltage(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.voltage == 4250

    def test_temperature(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.temperature == 310
        assert b.temperature_celsius == pytest.approx(31.0)

    def test_technology(self) -> None:
        b = parse_battery(self.SAMPLE)
        assert b.technology == "Li-ion"

    def test_empty_string(self) -> None:
        b = parse_battery("")
        assert b.level == 0


class TestParseScreenResolution:
    def test_standard(self) -> None:
        w, h = parse_screen_resolution("Physical size: 1080x2400")
        assert w == 1080
        assert h == 2400

    def test_no_match(self) -> None:
        w, h = parse_screen_resolution("no size here")
        assert w == 0
        assert h == 0


class TestParseIpAddress:
    SAMPLE = """
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.50/24 brd 192.168.1.255 scope global dynamic wlan0
"""

    def test_extracts_ip(self) -> None:
        ip = parse_ip_address(self.SAMPLE)
        assert ip == "192.168.1.50"

    def test_no_ip(self) -> None:
        ip = parse_ip_address("no inet here")
        assert ip == ""


class TestParseMeminfo:
    SAMPLE = """
MemTotal:        7959680 kB
MemFree:          890880 kB
MemAvailable:    3981312 kB
Buffers:           50688 kB
"""

    def test_total(self) -> None:
        total, _ = parse_meminfo(self.SAMPLE)
        assert total == 7959680 * 1024

    def test_available(self) -> None:
        _, avail = parse_meminfo(self.SAMPLE)
        assert avail == 3981312 * 1024

    def test_empty(self) -> None:
        total, avail = parse_meminfo("")
        assert total == 0
        assert avail == 0
