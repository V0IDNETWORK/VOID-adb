"""Unit tests for automation/macro engine."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from voidremote.core.automation import Macro, MacroLibrary, MacroPlayer, MacroRecorder, MacroStep


class TestMacroRecorder:
    def test_record_tap(self) -> None:
        rec = MacroRecorder("test")
        rec.record_tap(100, 200)
        macro = rec.finish()
        assert len(macro.steps) == 1
        assert macro.steps[0].action == "tap"
        assert macro.steps[0].params == {"x": 100, "y": 200}

    def test_record_swipe(self) -> None:
        rec = MacroRecorder("test")
        rec.record_swipe(0, 500, 0, 100, 300)
        macro = rec.finish()
        step = macro.steps[0]
        assert step.action == "swipe"
        assert step.params["x1"] == 0
        assert step.params["y2"] == 100

    def test_record_text(self) -> None:
        rec = MacroRecorder("test")
        rec.record_text("hello")
        macro = rec.finish()
        assert macro.steps[0].params["text"] == "hello"

    def test_record_keyevent(self) -> None:
        rec = MacroRecorder("test")
        rec.record_keyevent(3)
        macro = rec.finish()
        assert macro.steps[0].params["keycode"] == 3

    def test_multiple_steps(self) -> None:
        rec = MacroRecorder("multi")
        rec.record_tap(100, 200)
        rec.record_text("search")
        rec.record_keyevent(66)
        macro = rec.finish()
        assert len(macro.steps) == 3

    def test_macro_name(self) -> None:
        rec = MacroRecorder("my macro")
        macro = rec.finish()
        assert macro.name == "my macro"


class TestMacro:
    def test_to_dict_roundtrip(self) -> None:
        macro = Macro(name="test", steps=[
            MacroStep("tap", {"x": 1, "y": 2}, 0.1),
            MacroStep("text", {"text": "hello"}, 0.5),
        ])
        d = macro.to_dict()
        restored = Macro.from_dict(d)
        assert restored.name == macro.name
        assert len(restored.steps) == 2
        assert restored.steps[0].action == "tap"
        assert restored.steps[1].params["text"] == "hello"

    def test_repeat_default(self) -> None:
        m = Macro(name="x")
        assert m.repeat == 1

    def test_from_dict_missing_steps(self) -> None:
        m = Macro.from_dict({"name": "empty"})
        assert m.steps == []


class TestMacroPlayer:
    def test_plays_tap(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        macro = Macro(name="t", steps=[MacroStep("tap", {"x": 10, "y": 20}, 0.0)])
        player.play(macro, "serial123")
        ctrl.tap.assert_called_once_with("serial123", 10, 20)

    def test_plays_swipe(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        macro = Macro(name="s", steps=[
            MacroStep("swipe", {"x1": 0, "y1": 500, "x2": 0, "y2": 100, "duration_ms": 300}, 0.0)
        ])
        player.play(macro, "serial123")
        ctrl.swipe.assert_called_once()

    def test_plays_text(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        macro = Macro(name="t", steps=[MacroStep("text", {"text": "hello"}, 0.0)])
        player.play(macro, "serial123")
        ctrl.type_text.assert_called_once_with("serial123", "hello")

    def test_plays_keyevent(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        macro = Macro(name="k", steps=[MacroStep("keyevent", {"keycode": 3}, 0.0)])
        player.play(macro, "serial123")
        ctrl.key_event.assert_called_once_with("serial123", 3)

    def test_stop_halts_playback(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        player._running = True
        player.stop()
        assert player._running is False

    def test_step_error_does_not_crash(self) -> None:
        ctrl = MagicMock()
        ctrl.tap.side_effect = Exception("ADB error")
        player = MacroPlayer(ctrl)
        macro = Macro(name="t", steps=[MacroStep("tap", {"x": 0, "y": 0}, 0.0)])
        # Should not raise
        player.play(macro, "serial123")

    def test_repeat(self) -> None:
        ctrl = MagicMock()
        player = MacroPlayer(ctrl)
        macro = Macro(name="r", repeat=3, steps=[MacroStep("tap", {"x": 0, "y": 0}, 0.0)])
        player.play(macro, "serial123")
        assert ctrl.tap.call_count == 3


class TestMacroLibrary:
    def test_save_and_load(self, tmp_path: Path) -> None:
        lib = MacroLibrary(tmp_path)
        macro = Macro(name="test macro", steps=[MacroStep("tap", {"x": 1, "y": 2}, 0.0)])
        lib.save(macro)
        loaded = lib.load("test macro")
        assert loaded.name == "test macro"
        assert loaded.steps[0].params["x"] == 1

    def test_list_macros(self, tmp_path: Path) -> None:
        lib = MacroLibrary(tmp_path)
        lib.save(Macro(name="macro one"))
        lib.save(Macro(name="macro two"))
        names = lib.list_macros()
        assert len(names) == 2

    def test_delete(self, tmp_path: Path) -> None:
        lib = MacroLibrary(tmp_path)
        lib.save(Macro(name="delete me"))
        result = lib.delete("delete me")
        assert result is True
        assert "delete me" not in lib.list_macros()

    def test_delete_nonexistent(self, tmp_path: Path) -> None:
        lib = MacroLibrary(tmp_path)
        result = lib.delete("ghost")
        assert result is False

    def test_load_nonexistent_raises(self, tmp_path: Path) -> None:
        lib = MacroLibrary(tmp_path)
        with pytest.raises(FileNotFoundError):
            lib.load("nonexistent")
