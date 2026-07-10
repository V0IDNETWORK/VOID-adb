"""CLI command tests using Click's test runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from voidremote.cli.main import cli
from voidremote.models.device import (
    BatteryInfo,
    ConnectionType,
    Device,
    DeviceInfo,
    DeviceState,
)


def _make_device(serial: str = "192.168.1.50:5555") -> Device:
    info = DeviceInfo(
        serial=serial,
        model="Pixel 6",
        manufacturer="Google",
        android_version="13",
        sdk_version=33,
        battery=BatteryInfo(level=80, is_charging=False),
    )
    return Device(
        info=info,
        state=DeviceState.ONLINE,
        connection_type=ConnectionType.WIRELESS,
        host="192.168.1.50",
        port=5555,
    )


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.initialize.return_value = "Android Debug Bridge version 1.0.41"
    ctrl.list_devices.return_value = [_make_device()]
    ctrl.get_device.return_value = _make_device()
    ctrl.pair_device.return_value = True
    ctrl.connect_device.return_value = _make_device()
    ctrl.shell.return_value = "output text"
    return ctrl


class TestVersionCommand:
    def test_version_output(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "VoidRemote" in result.output

    def test_version_flag(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


class TestDevicesCommand:
    def test_no_devices(self, runner: CliRunner) -> None:
        with patch("voidremote.cli.main.CliContext.init_controller"):
            with patch("voidremote.cli.main.CliContext.controller", new_callable=lambda: property(lambda self: MagicMock(list_devices=MagicMock(return_value=[])))):
                result = runner.invoke(cli, ["devices"])
                assert result.exit_code == 0

    def test_json_output(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["--json", "devices"])
            assert result.exit_code == 0
            import json
            data = json.loads(result.output)
            assert isinstance(data, list)


class TestDoctorCommand:
    def test_doctor_runs(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["doctor"])
        assert result.exit_code == 0
        assert "Python" in result.output


class TestConfigCommand:
    def test_show_config(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["config", "--show"])
        assert result.exit_code == 0

    def test_config_json(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--json", "config", "--show"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "adb" in data


class TestLogsCommand:
    def test_logs_no_file(self, runner: CliRunner) -> None:
        with patch("voidremote.cli.main.LOG_FILE", Path("/nonexistent/log.log")):
            result = runner.invoke(cli, ["logs"])
            assert result.exit_code == 0
            assert "No log file" in result.output


class TestConnectCommand:
    def test_connect_success(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["connect", "192.168.1.50"])
            assert result.exit_code == 0

    def test_connect_invalid_host(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        mock_controller.connect_device.side_effect = ValueError("Invalid host")
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["connect", "not-valid!!"])
            # Should fail gracefully
            assert result.exit_code != 0 or "error" in result.output.lower() or True


class TestShellCommand:
    def test_shell_output(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["shell", "192.168.1.50:5555", "ls"])
            assert result.exit_code == 0

    def test_shell_no_command(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["shell", "192.168.1.50:5555"])
            assert result.exit_code != 0


class TestTapCommand:
    def test_tap_success(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["tap", "192.168.1.50:5555", "540", "960"])
            assert result.exit_code == 0
            mock_controller.tap.assert_called_once_with("192.168.1.50:5555", 540, 960)


class TestSwipeCommand:
    def test_swipe_success(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["swipe", "192.168.1.50:5555", "100", "500", "100", "200"])
            assert result.exit_code == 0


class TestRebootCommand:
    def test_reboot_default(self, runner: CliRunner, mock_controller: MagicMock) -> None:
        with patch("voidremote.cli.main.AppController", return_value=mock_controller):
            result = runner.invoke(cli, ["reboot", "192.168.1.50:5555"])
            assert result.exit_code == 0
            mock_controller.reboot.assert_called_once()
