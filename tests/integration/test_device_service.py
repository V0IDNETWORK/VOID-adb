"""Integration tests for DeviceService."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voidremote.adb.client import AdbClient, AdbCommandResult, AdbError
from voidremote.models.device import ConnectionConfig, Device, DeviceState, PairingInfo
from voidremote.services.device_service import DeviceService


DEVICES_OUTPUT = (
    "List of devices attached\n"
    "192.168.1.50:5555\tdevice product:pixel6 model:Pixel_6 device:pixel6\n"
)


@pytest.fixture
def mock_adb_with_devices() -> MagicMock:
    adb = MagicMock(spec=AdbClient)
    adb.list_devices_raw.return_value = DEVICES_OUTPUT
    # shell returns empty results for all property lookups
    adb.shell.return_value = AdbCommandResult("", "", 0)
    return adb


@pytest.fixture
def svc(mock_adb_with_devices: MagicMock, tmp_path: Path) -> DeviceService:
    with patch("voidremote.services.device_service.TRUSTED_DEVICES_FILE", tmp_path / "trusted.json"):
        service = DeviceService(mock_adb_with_devices)
    return service


class TestDeviceServiceRefresh:
    def test_refresh_returns_devices(self, svc: DeviceService) -> None:
        devices = svc.refresh_devices()
        assert len(devices) == 1

    def test_device_serial(self, svc: DeviceService) -> None:
        devices = svc.refresh_devices()
        assert devices[0].serial == "192.168.1.50:5555"

    def test_device_state_online(self, svc: DeviceService) -> None:
        devices = svc.refresh_devices()
        assert devices[0].state == DeviceState.ONLINE

    def test_empty_output(self, tmp_path: Path) -> None:
        adb = MagicMock(spec=AdbClient)
        adb.list_devices_raw.return_value = "List of devices attached\n"
        adb.shell.return_value = AdbCommandResult("", "", 0)
        with patch("voidremote.services.device_service.TRUSTED_DEVICES_FILE", tmp_path / "t.json"):
            svc = DeviceService(adb)
        devices = svc.refresh_devices()
        assert devices == []

    def test_get_device_after_refresh(self, svc: DeviceService) -> None:
        svc.refresh_devices()
        d = svc.get_device("192.168.1.50:5555")
        assert d is not None


class TestDeviceServicePairing:
    def test_pair_success(self, svc: DeviceService) -> None:
        svc._adb.pair.return_value = AdbCommandResult("Successfully paired", "", 0)
        result = svc.pair_device("192.168.1.50", 37001, "123456")
        assert result is True
        svc._adb.pair.assert_called_once()

    def test_pair_failure(self, svc: DeviceService) -> None:
        svc._adb.pair.return_value = AdbCommandResult("Failed to pair", "error", 1)
        with pytest.raises(AdbError):
            svc.pair_device("192.168.1.50", 37001, "999999")

    def test_pair_invalid_host(self, svc: DeviceService) -> None:
        with pytest.raises(ValueError):
            svc.pair_device("", 37001, "123456")

    def test_pair_invalid_port(self, svc: DeviceService) -> None:
        with pytest.raises(ValueError):
            svc.pair_device("192.168.1.50", 0, "123456")


class TestDeviceServiceConnection:
    def test_connect_success(self, svc: DeviceService, mock_adb_with_devices: MagicMock) -> None:
        mock_adb_with_devices.connect.return_value = AdbCommandResult("connected to 192.168.1.50:5555", "", 0)
        device = svc.connect_device("192.168.1.50", 5555, remember=False)
        assert device.serial == "192.168.1.50:5555"

    def test_connect_saves_trusted(self, svc: DeviceService, mock_adb_with_devices: MagicMock, tmp_path: Path) -> None:
        mock_adb_with_devices.connect.return_value = AdbCommandResult("connected", "", 0)
        svc.connect_device("192.168.1.50", 5555, remember=True)
        assert "192.168.1.50:5555" in svc._trusted

    def test_disconnect_wireless(self, svc: DeviceService) -> None:
        svc.refresh_devices()
        result = svc.disconnect_device("192.168.1.50:5555")
        assert result is True
        svc._adb.disconnect.assert_called_once_with("192.168.1.50", 5555)

    def test_disconnect_usb_skipped(self, svc: DeviceService) -> None:
        result = svc.disconnect_device("ABC123XYZ")
        assert result is False
        svc._adb.disconnect.assert_not_called()


class TestTrustedDevices:
    def test_save_and_load_trusted(self, svc: DeviceService, mock_adb_with_devices: MagicMock) -> None:
        mock_adb_with_devices.connect.return_value = AdbCommandResult("connected", "", 0)
        svc.connect_device("192.168.1.50", 5555, remember=True)
        trusted = svc.list_trusted_devices()
        assert any(t.serial == "192.168.1.50:5555" for t in trusted)

    def test_forget_device(self, svc: DeviceService, mock_adb_with_devices: MagicMock) -> None:
        mock_adb_with_devices.connect.return_value = AdbCommandResult("connected", "", 0)
        svc.connect_device("192.168.1.50", 5555, remember=True)
        result = svc.forget_device("192.168.1.50:5555")
        assert result is True
        assert "192.168.1.50:5555" not in svc._trusted

    def test_forget_nonexistent(self, svc: DeviceService) -> None:
        result = svc.forget_device("nonexistent:5555")
        assert result is False
