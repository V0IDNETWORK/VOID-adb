"""
Real-time device monitoring service.

Polls CPU, RAM, battery, temperature, and network stats at regular
intervals and emits snapshots.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from voidremote.adb.client import AdbClient

logger = logging.getLogger(__name__)


@dataclass
class DeviceSnapshot:
    """Point-in-time device performance metrics."""

    serial: str
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_usage: float = 0.0
    ram_used_mb: float = 0.0
    ram_total_mb: float = 0.0
    battery_level: int = 0
    battery_temperature: float = 0.0
    battery_is_charging: bool = False
    storage_used_gb: float = 0.0
    storage_total_gb: float = 0.0
    fps: float = 0.0

    @property
    def ram_usage_percent(self) -> float:
        if self.ram_total_mb == 0:
            return 0.0
        return (self.ram_used_mb / self.ram_total_mb) * 100.0

    @property
    def storage_usage_percent(self) -> float:
        if self.storage_total_gb == 0:
            return 0.0
        return (self.storage_used_gb / self.storage_total_gb) * 100.0


SnapshotCallback = Callable[[DeviceSnapshot], None]


class MonitorService:
    """
    Polls device metrics at a configurable interval.

    Usage::

        monitor = MonitorService(adb_client)
        monitor.start("serial123", interval=2.0, callback=on_snapshot)
        # ... later ...
        monitor.stop("serial123")
    """

    def __init__(self, adb: AdbClient) -> None:
        self._adb = adb
        self._threads: dict[str, threading.Thread] = {}
        self._stop_events: dict[str, threading.Event] = {}
        self._callbacks: dict[str, list[SnapshotCallback]] = {}

    def start(
        self,
        serial: str,
        interval: float = 2.0,
        callback: Optional[SnapshotCallback] = None,
    ) -> None:
        """Start monitoring a device."""
        if serial in self._threads and self._threads[serial].is_alive():
            logger.warning("Already monitoring %s", serial)
            return
        stop_event = threading.Event()
        self._stop_events[serial] = stop_event
        self._callbacks[serial] = [callback] if callback else []

        thread = threading.Thread(
            target=self._poll_loop,
            args=(serial, interval, stop_event),
            name=f"monitor-{serial}",
            daemon=True,
        )
        self._threads[serial] = thread
        thread.start()
        logger.info("Started monitoring %s (interval=%.1fs)", serial, interval)

    def stop(self, serial: str) -> None:
        """Stop monitoring a device."""
        event = self._stop_events.get(serial)
        if event:
            event.set()
        thread = self._threads.get(serial)
        if thread and thread.is_alive():
            thread.join(timeout=5.0)
        self._threads.pop(serial, None)
        self._stop_events.pop(serial, None)
        self._callbacks.pop(serial, None)
        logger.info("Stopped monitoring %s", serial)

    def stop_all(self) -> None:
        """Stop all monitoring threads."""
        for serial in list(self._threads.keys()):
            self.stop(serial)

    def add_callback(self, serial: str, callback: SnapshotCallback) -> None:
        """Register an additional callback for a monitored device."""
        if serial not in self._callbacks:
            self._callbacks[serial] = []
        self._callbacks[serial].append(callback)

    def _poll_loop(
        self, serial: str, interval: float, stop_event: threading.Event
    ) -> None:
        """Main polling loop running in background thread."""
        while not stop_event.is_set():
            try:
                snapshot = self._collect_snapshot(serial)
                for cb in self._callbacks.get(serial, []):
                    try:
                        cb(snapshot)
                    except Exception as exc:
                        logger.warning("Monitor callback error: %s", exc)
            except Exception as exc:
                logger.debug("Snapshot collection failed for %s: %s", serial, exc)
            stop_event.wait(interval)

    def _collect_snapshot(self, serial: str) -> DeviceSnapshot:
        """Collect all metrics for one snapshot."""
        snapshot = DeviceSnapshot(serial=serial)

        # CPU
        try:
            snapshot.cpu_usage = self._get_cpu_usage(serial)
        except Exception:
            pass

        # RAM
        try:
            total, avail = self._get_ram(serial)
            snapshot.ram_total_mb = total / (1024 * 1024)
            snapshot.ram_used_mb = (total - avail) / (1024 * 1024)
        except Exception:
            pass

        # Battery
        try:
            level, temp, charging = self._get_battery(serial)
            snapshot.battery_level = level
            snapshot.battery_temperature = temp
            snapshot.battery_is_charging = charging
        except Exception:
            pass

        return snapshot

    def _get_cpu_usage(self, serial: str) -> float:
        """Calculate CPU usage percentage from /proc/stat."""
        def read_stat() -> tuple[int, int]:
            out = self._adb.shell(serial, "cat /proc/stat").stdout
            for line in out.splitlines():
                if line.startswith("cpu "):
                    nums = [int(x) for x in line.split()[1:]]
                    total = sum(nums)
                    idle = nums[3] if len(nums) > 3 else 0
                    return total, idle
            return 0, 0

        t1, i1 = read_stat()
        time.sleep(0.2)
        t2, i2 = read_stat()
        dt = t2 - t1
        di = i2 - i1
        if dt == 0:
            return 0.0
        return max(0.0, min(100.0, (1.0 - di / dt) * 100.0))

    def _get_ram(self, serial: str) -> tuple[int, int]:
        """Return (total_bytes, available_bytes) from /proc/meminfo."""
        from voidremote.adb.device_parser import parse_meminfo
        out = self._adb.shell(serial, "cat /proc/meminfo").stdout
        return parse_meminfo(out)

    def _get_battery(self, serial: str) -> tuple[int, float, bool]:
        """Return (level, temperature_c, is_charging)."""
        from voidremote.adb.device_parser import parse_battery
        out = self._adb.shell(serial, "dumpsys battery").stdout
        info = parse_battery(out)
        return info.level, info.temperature_celsius, info.is_charging
