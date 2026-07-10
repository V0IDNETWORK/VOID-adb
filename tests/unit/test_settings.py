"""Unit tests for application settings."""

from __future__ import annotations

from pathlib import Path

import pytest

from voidremote.config.settings import AppSettings, AdbSettings, UISettings, MirrorSettings


class TestAdbSettings:
    def test_defaults(self) -> None:
        s = AdbSettings()
        assert s.path == "adb"
        assert s.default_port == 5555
        assert s.auto_start_server is True

    def test_empty_path_becomes_adb(self) -> None:
        s = AdbSettings(path="")
        assert s.path == "adb"

    def test_whitespace_path_becomes_adb(self) -> None:
        s = AdbSettings(path="   ")
        assert s.path == "adb"

    def test_custom_path(self) -> None:
        s = AdbSettings(path="/usr/local/bin/adb")
        assert s.path == "/usr/local/bin/adb"


class TestUISettings:
    def test_defaults(self) -> None:
        s = UISettings()
        assert s.theme == "dark"
        assert s.font_size == 13

    def test_invalid_theme(self) -> None:
        with pytest.raises(Exception):
            UISettings(theme="purple")

    def test_valid_themes(self) -> None:
        for theme in ("dark", "light", "auto"):
            s = UISettings(theme=theme)
            assert s.theme == theme


class TestMirrorSettings:
    def test_defaults(self) -> None:
        s = MirrorSettings()
        assert s.max_fps == 30
        assert s.max_bitrate_mbps == 8
        assert s.stay_awake is True


class TestAppSettings:
    def test_defaults(self) -> None:
        s = AppSettings()
        assert s.app_name == "VoidRemote"
        assert s.version == "1.0.0"
        assert s.debug is False

    def test_nested_adb(self) -> None:
        s = AppSettings()
        assert isinstance(s.adb, AdbSettings)

    def test_nested_ui(self) -> None:
        s = AppSettings()
        assert isinstance(s.ui, UISettings)

    def test_save_and_load(self, tmp_path: Path) -> None:
        s = AppSettings()
        s.debug = True
        s.ui.theme = "light"
        path = tmp_path / "settings.json"
        s.save(path)
        loaded = AppSettings.load(path)
        assert loaded.debug is True
        assert loaded.ui.theme == "light"

    def test_load_missing_file_returns_defaults(self, tmp_path: Path) -> None:
        path = tmp_path / "nonexistent.json"
        s = AppSettings.load(path)
        assert s.app_name == "VoidRemote"

    def test_load_corrupt_file_returns_defaults(self, tmp_path: Path) -> None:
        path = tmp_path / "settings.json"
        path.write_text("not valid json", encoding="utf-8")
        s = AppSettings.load(path)
        assert s.app_name == "VoidRemote"

    def test_reset_to_defaults(self) -> None:
        s = AppSettings()
        s.debug = True
        s.ui.theme = "light"
        s.reset_to_defaults()
        assert s.debug is False
        assert s.ui.theme == "dark"
