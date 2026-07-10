"""
Automation engine — macro recording and playback.

Records sequences of input events and replays them on demand.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class MacroStep:
    """A single recorded automation step."""

    action: str           # tap | swipe | text | keyevent | sleep
    params: dict          # action-specific parameters
    delay_after: float = 0.0  # seconds to wait after this step


@dataclass
class Macro:
    """A recorded sequence of automation steps."""

    name: str
    steps: list[MacroStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""
    repeat: int = 1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "repeat": self.repeat,
            "steps": [asdict(s) for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Macro":
        steps = [MacroStep(**s) for s in data.get("steps", [])]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            created_at=data.get("created_at", ""),
            repeat=data.get("repeat", 1),
            steps=steps,
        )


class MacroRecorder:
    """Records user input actions into a Macro."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._steps: list[MacroStep] = []
        self._last_time: float = time.monotonic()

    def _delay(self) -> float:
        now = time.monotonic()
        delay = now - self._last_time
        self._last_time = now
        return round(delay, 3)

    def record_tap(self, x: int, y: int) -> None:
        self._steps.append(MacroStep("tap", {"x": x, "y": y}, self._delay()))

    def record_swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self._steps.append(MacroStep(
            "swipe", {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "duration_ms": duration_ms},
            self._delay()
        ))

    def record_text(self, text: str) -> None:
        self._steps.append(MacroStep("text", {"text": text}, self._delay()))

    def record_keyevent(self, keycode: int) -> None:
        self._steps.append(MacroStep("keyevent", {"keycode": keycode}, self._delay()))

    def record_sleep(self, seconds: float) -> None:
        self._steps.append(MacroStep("sleep", {"seconds": seconds}, 0.0))

    def finish(self) -> Macro:
        return Macro(name=self._name, steps=self._steps)


class MacroPlayer:
    """Plays back a Macro on a target device."""

    def __init__(self, controller: object) -> None:
        self._controller = controller
        self._running = False

    def play(self, macro: Macro, serial: str, speed: float = 1.0) -> None:
        """
        Execute a macro on the specified device.

        Args:
            macro: The macro to play.
            serial: ADB device serial.
            speed: Playback speed multiplier (1.0 = recorded speed).
        """
        self._running = True
        logger.info("Playing macro '%s' on %s (repeat=%d)", macro.name, serial, macro.repeat)

        for iteration in range(macro.repeat):
            if not self._running:
                break
            logger.debug("Macro iteration %d/%d", iteration + 1, macro.repeat)
            for step in macro.steps:
                if not self._running:
                    break
                if step.delay_after > 0:
                    time.sleep(step.delay_after / speed)
                self._execute_step(step, serial)

        self._running = False
        logger.info("Macro '%s' completed", macro.name)

    def stop(self) -> None:
        self._running = False

    def _execute_step(self, step: MacroStep, serial: str) -> None:
        try:
            if step.action == "tap":
                self._controller.tap(serial, step.params["x"], step.params["y"])
            elif step.action == "swipe":
                self._controller.swipe(
                    serial,
                    step.params["x1"], step.params["y1"],
                    step.params["x2"], step.params["y2"],
                    step.params.get("duration_ms", 300),
                )
            elif step.action == "text":
                self._controller.type_text(serial, step.params["text"])
            elif step.action == "keyevent":
                self._controller.key_event(serial, step.params["keycode"])
            elif step.action == "sleep":
                time.sleep(step.params.get("seconds", 0.5))
        except Exception as exc:
            logger.warning("Macro step '%s' failed: %s", step.action, exc)


class MacroLibrary:
    """Persistent storage for saved macros."""

    def __init__(self, storage_dir: Path) -> None:
        self._dir = storage_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(self, macro: Macro) -> Path:
        safe_name = macro.name.replace(" ", "_").replace("/", "_")
        path = self._dir / f"{safe_name}.json"
        path.write_text(json.dumps(macro.to_dict(), indent=2), encoding="utf-8")
        logger.debug("Saved macro: %s", path)
        return path

    def load(self, name: str) -> Macro:
        safe_name = name.replace(" ", "_").replace("/", "_")
        path = self._dir / f"{safe_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Macro not found: {name!r}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Macro.from_dict(data)

    def list_macros(self) -> list[str]:
        return [p.stem.replace("_", " ") for p in self._dir.glob("*.json")]

    def delete(self, name: str) -> bool:
        safe_name = name.replace(" ", "_").replace("/", "_")
        path = self._dir / f"{safe_name}.json"
        if path.exists():
            path.unlink()
            return True
        return False
