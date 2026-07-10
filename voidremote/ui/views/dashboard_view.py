"""Dashboard view — device grid with refresh and quick actions."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from voidremote.models.device import Device
from voidremote.ui.theme import Colors
from voidremote.ui.widgets.device_card import DeviceCard


class RefreshWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, controller: object, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self._controller = controller

    def run(self) -> None:
        try:
            devices = self._controller.list_devices(refresh=True)
            self.finished.emit(devices)
        except Exception as exc:
            self.error.emit(str(exc))


class DashboardView(QWidget):
    """
    Main dashboard showing device cards in a responsive grid.

    Signals:
        connect_device(host, port): Request connection to device.
        disconnect_device(serial): Request disconnect.
        mirror_device(serial): Request screen mirror.
        show_device_info(serial): Request info panel.
        pair_device(): Open pair dialog.
    """

    connect_device: Signal = Signal(str, int)
    disconnect_device: Signal = Signal(str)
    mirror_device: Signal = Signal(str)
    show_device_info: Signal = Signal(str)
    pair_device: Signal = Signal()

    def __init__(self, controller: object, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._cards: dict[str, DeviceCard] = {}
        self._worker: Optional[RefreshWorker] = None
        self._build_ui()
        self._auto_refresh = QTimer(self)
        self._auto_refresh.setInterval(5000)
        self._auto_refresh.timeout.connect(self.refresh)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(24, 20, 24, 16)
        header.setSpacing(12)

        title = QLabel("Devices")
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY};"
        )
        header.addWidget(title)
        header.addStretch()

        self._count_label = QLabel("0 devices")
        self._count_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 13px;")
        header.addWidget(self._count_label)

        btn_pair = QPushButton("+ Pair")
        btn_pair.setObjectName("accent")
        btn_pair.setFixedWidth(80)
        btn_pair.clicked.connect(self.pair_device)
        header.addWidget(btn_pair)

        self._btn_refresh = QPushButton("↻ Refresh")
        self._btn_refresh.setFixedWidth(90)
        self._btn_refresh.clicked.connect(self.refresh)
        header.addWidget(self._btn_refresh)

        header_widget = QWidget()
        header_widget.setStyleSheet(
            f"background: {Colors.BG_SURFACE}; border-bottom: 1px solid {Colors.BORDER};"
        )
        header_widget.setLayout(header)
        root.addWidget(header_widget)

        # ── Scroll area with device grid ─────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(f"background: {Colors.BG_BASE};")
        self._grid = QGridLayout(self._grid_container)
        self._grid.setContentsMargins(24, 20, 24, 20)
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self._grid_container)
        root.addWidget(scroll, stretch=1)

        # ── Empty state ──────────────────────────────────
        self._empty_state = QWidget()
        empty_layout = QVBoxLayout(self._empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty_icon = QLabel("📱")
        empty_icon.setStyleSheet("font-size: 56px;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)

        empty_title = QLabel("No devices connected")
        empty_title.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {Colors.TEXT_SECONDARY}; margin-top: 12px;"
        )
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_title)

        empty_hint = QLabel(
            "Enable Wireless Debugging on your Android device,\n"
            "then click '+ Pair' to get started."
        )
        empty_hint.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 13px; margin-top: 6px;")
        empty_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_hint)

        btn_pair2 = QPushButton("Pair New Device")
        btn_pair2.setObjectName("accent")
        btn_pair2.setFixedWidth(160)
        btn_pair2.clicked.connect(self.pair_device)
        btn_pair2_wrap = QHBoxLayout()
        btn_pair2_wrap.addStretch()
        btn_pair2_wrap.addWidget(btn_pair2)
        btn_pair2_wrap.addStretch()
        empty_layout.addLayout(btn_pair2_wrap)

        scroll.setWidget(self._grid_container)

        # Stack grid + empty state inside scroll
        self._stack_widget = QWidget()
        self._stack_widget.setStyleSheet(f"background: {Colors.BG_BASE};")
        stack_layout = QVBoxLayout(self._stack_widget)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.addWidget(self._grid_container)
        stack_layout.addWidget(self._empty_state)

        scroll.setWidget(self._stack_widget)
        self._empty_state.hide()

    def start_auto_refresh(self) -> None:
        self._auto_refresh.start()

    def stop_auto_refresh(self) -> None:
        self._auto_refresh.stop()

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._btn_refresh.setEnabled(False)
        self._btn_refresh.setText("Refreshing…")
        self._worker = RefreshWorker(self._controller, self)
        self._worker.finished.connect(self._on_devices_loaded)
        self._worker.error.connect(self._on_refresh_error)
        self._worker.start()

    @Slot(list)
    def _on_devices_loaded(self, devices: list) -> None:
        self._btn_refresh.setEnabled(True)
        self._btn_refresh.setText("↻ Refresh")
        self._update_grid(devices)
        count = len(devices)
        self._count_label.setText(f"{count} device{'s' if count != 1 else ''}")

    @Slot(str)
    def _on_refresh_error(self, error: str) -> None:
        self._btn_refresh.setEnabled(True)
        self._btn_refresh.setText("↻ Refresh")
        self._count_label.setText(f"Error: {error[:40]}")

    def _update_grid(self, devices: list) -> None:
        existing_serials = set(self._cards.keys())
        new_serials = {d.serial for d in devices}

        # Remove stale cards
        for serial in existing_serials - new_serials:
            card = self._cards.pop(serial)
            self._grid.removeWidget(card)
            card.deleteLater()

        # Add or update cards
        for device in devices:
            if device.serial in self._cards:
                self._cards[device.serial].refresh(device)
            else:
                card = DeviceCard(device)
                card.connect_requested.connect(
                    lambda s: self.connect_device.emit(s.split(":")[0], int(s.split(":")[1]) if ":" in s else 5555)
                )
                card.disconnect_requested.connect(self.disconnect_device)
                card.mirror_requested.connect(self.mirror_device)
                card.info_requested.connect(self.show_device_info)
                self._cards[device.serial] = card

        # Re-layout grid (2 columns)
        for i, (serial, card) in enumerate(self._cards.items()):
            self._grid.addWidget(card, i // 2, i % 2)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        has_devices = bool(self._cards)
        self._grid_container.setVisible(has_devices)
        self._empty_state.setVisible(not has_devices)
