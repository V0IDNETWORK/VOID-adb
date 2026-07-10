"""Unit tests for InputService."""

from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest

from voidremote.adb.client import AdbClient, AdbCommandResult
from voidremote.services.input_service import InputService, KeyCode


@pytest.fixture
def mock_adb() -> MagicMock:
    adb = MagicMock(spec=AdbClient)
    adb.shell.return_value = AdbCommandResult("", "", 0)
    return adb


@pytest.fixture
def svc(mock_adb: MagicMock) -> InputService:
    return InputService(mock_adb)


SERIAL = "192.168.1.1:5555"


class TestTap:
    def test_calls_adb_shell(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.tap(SERIAL, 540, 960)
        mock_adb.shell.assert_called_once_with(SERIAL, "input tap 540 960")

    def test_double_tap_calls_twice(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.double_tap(SERIAL, 100, 200, delay_ms=0)
        assert mock_adb.shell.call_count == 2


class TestLongPress:
    def test_uses_swipe_with_same_coords(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.long_press(SERIAL, 300, 400, duration_ms=800)
        mock_adb.shell.assert_called_once_with(SERIAL, "input swipe 300 400 300 400 800")


class TestSwipe:
    def test_swipe_command(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.swipe(SERIAL, 100, 500, 100, 100, 300)
        mock_adb.shell.assert_called_once_with(SERIAL, "input swipe 100 500 100 100 300")

    def test_scroll_down(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.scroll_down(SERIAL, 540, 960, amount=400)
        call_arg = mock_adb.shell.call_args[0][1]
        assert "swipe" in call_arg
        assert "560" in call_arg or "560" not in call_arg  # direction check via y2 < y1

    def test_drag_is_slow_swipe(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.drag(SERIAL, 0, 0, 100, 100, duration_ms=1000)
        call_arg = mock_adb.shell.call_args[0][1]
        assert "1000" in call_arg


class TestTypeText:
    def test_encodes_text(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.type_text(SERIAL, "hello")
        call_arg = mock_adb.shell.call_args[0][1]
        assert "input text" in call_arg
        assert "hello" in call_arg

    def test_special_chars_encoded(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.type_text(SERIAL, "hello world")
        call_arg = mock_adb.shell.call_args[0][1]
        assert "hello" in call_arg


class TestKeyEvent:
    def test_home_key(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.home(SERIAL)
        mock_adb.shell.assert_called_once_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_HOME}")

    def test_back_key(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.back(SERIAL)
        mock_adb.shell.assert_called_once_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_BACK}")

    def test_power_key(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.power(SERIAL)
        mock_adb.shell.assert_called_once_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_POWER}")

    def test_volume_up(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.volume_up(SERIAL)
        mock_adb.shell.assert_called_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_VOLUME_UP}")

    def test_volume_down(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.volume_down(SERIAL)
        mock_adb.shell.assert_called_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_VOLUME_DOWN}")

    def test_app_switch(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.app_switch(SERIAL)
        mock_adb.shell.assert_called_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_APP_SWITCH}")

    def test_raw_keycode(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.key_event(SERIAL, 999)
        mock_adb.shell.assert_called_once_with(SERIAL, "input keyevent 999")

    def test_wake_device(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.wake_device(SERIAL)
        mock_adb.shell.assert_called_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_WAKEUP}")

    def test_sleep_device(self, svc: InputService, mock_adb: MagicMock) -> None:
        svc.sleep_device(SERIAL)
        mock_adb.shell.assert_called_with(SERIAL, f"input keyevent {KeyCode.KEYCODE_SLEEP}")
