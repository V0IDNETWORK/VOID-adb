"""
Shared pytest fixtures for VoidRemote tests.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from voidremote.adb.client import AdbClient, AdbCommandResult
from voidremote.config.settings import AppSettings, AdbSettings, UISettings
from voidremote.controllers.app_controller import AppController
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
from voidremote.services.device_service import DeviceService
from voidremote.services.input_service import InputService


# ── ADB Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def mock_adb() -> MagicMock:
    """Return a MagicMock AdbClient."""
    adb = MagicMock(spec=AdbClient)
    adb.verify_adb.return_value = "Android Debug Bridge version 1.0.41"
    adb.list_devices_raw.return_value = (
        "List of devices attached\n"
        "192.168.1.50:5555\tdevice product:device model:Pixel_6 device:pixel6 transport_id:1\n"
    )
    adb.shell.return_value = AdbCommandResult("", "", 0)
    return adb


@pytest.fixture
def adb_result_ok() -> AdbCommandResult:
    return AdbCommandResult("success", "", 0)


@pytest.fixture
def adb_result_fail() -> AdbCommandResult:
    return AdbCommandResult("", "error: device not found", 1)


# ── Model Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_battery() -> BatteryInfo:
    return BatteryInfo(
        level=75,
        is_charging=True,
        is_ac_powered=False,
        is_usb_powered=True,
        voltage=4200,
        temperature=280,
        health="good",
        technology="Li-ion",
    )


@pytest.fixture
def sample_device_info(sample_battery: BatteryInfo) -> DeviceInfo:
    return DeviceInfo(
        serial="192.168.1.50:5555",
        model="Pixel 6",
        manufacturer="Google",
        brand="google",
        product="pixel6",
        device_name="pixel6",
        android_version="13",
        sdk_version=33,
        build_id="TP1A.220905.004",
        screen_width=1080,
        screen_height=2400,
        screen_density=411,
        battery=sample_battery,
        storage=StorageInfo(
            total_bytes=128 * 1024**3,
            used_bytes=64 * 1024**3,
            available_bytes=64 * 1024**3,
        ),
        cpu=CpuInfo(abi="arm64-v8a", cores=8),
        network=NetworkInfo(ip_address="192.168.1.50"),
        ram_total_bytes=8 * 1024**3,
        ram_available_bytes=4 * 1024**3,
    )


@pytest.fixture
def sample_device(sample_device_info: DeviceInfo) -> Device:
    return Device(
        info=sample_device_info,
        state=DeviceState.ONLINE,
        connection_type=ConnectionType.WIRELESS,
        host="192.168.1.50",
        port=5555,
        is_trusted=True,
        connected_at=datetime.now(),
        capabilities=[
            DeviceCapability.SHELL,
            DeviceCapability.SCREEN_MIRROR,
            DeviceCapability.FILE_TRANSFER,
            DeviceCapability.INPUT_CONTROL,
            DeviceCapability.PACKAGE_MANAGER,
            DeviceCapability.MONITORING,
        ],
    )


# ── Settings Fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def test_settings(tmp_path: Path) -> AppSettings:
    """Return AppSettings pointing to a temp directory."""
    settings = AppSettings()
    settings.adb.path = "adb"
    settings.debug = True
    return settings


# ── Service Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def device_service(mock_adb: MagicMock, tmp_path: Path) -> DeviceService:
    with patch("voidremote.services.device_service.TRUSTED_DEVICES_FILE", tmp_path / "trusted.json"):
        svc = DeviceService(mock_adb)
    return svc


@pytest.fixture
def input_service(mock_adb: MagicMock) -> InputService:
    return InputService(mock_adb)


# ── Controller Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def app_controller(mock_adb: MagicMock, test_settings: AppSettings, tmp_path: Path) -> AppController:
    ctrl = AppController(test_settings)
    ctrl._adb = mock_adb
    ctrl._device_service = DeviceService(mock_adb)
    ctrl._input_service = InputService(mock_adb)
    return ctrl
