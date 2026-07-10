"""Wireless ADB pairing dialog."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from voidremote.ui.theme import Colors


class PairWorker(QThread):
    """Background thread for ADB pairing."""

    success = Signal(str)
    failure = Signal(str)

    def __init__(
        self,
        controller: object,
        host: str,
        port: int,
        code: str,
        parent: Optional[QObject] = None,  # type: ignore[name-defined]
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._host = host
        self._port = port
        self._code = code

    def run(self) -> None:
        try:
            ok = self._controller.pair_device(self._host, self._port, self._code)
            if ok:
                self.success.emit(f"Paired with {self._host}:{self._port}")
            else:
                self.failure.emit("Pairing failed — wrong code or timeout")
        except Exception as exc:
            self.failure.emit(str(exc))


class PairDialog(QDialog):
    """
    Dialog for pairing an Android device via Wireless Debugging.

    Shows setup instructions, input fields, and async pairing progress.
    """

    paired = Signal(str, int)  # host, port

    def __init__(self, controller: object, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._worker: Optional[PairWorker] = None
        self.setWindowTitle("Pair New Device")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 20)

        # Title
        title = QLabel("Pair via Wireless Debugging")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY};"
        )
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "On your Android device:\n"
            "  1. Go to Settings → Developer Options\n"
            "  2. Enable Wireless Debugging\n"
            "  3. Tap 'Pair device with pairing code'\n"
            "  4. Enter the IP, port, and 6-digit code shown below"
        )
        instructions.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; "
            f"background: {Colors.BG_ELEVATED}; border-radius: 6px; padding: 12px;"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._host_edit = QLineEdit()
        self._host_edit.setPlaceholderText("192.168.1.x")
        form.addRow("Device IP:", self._host_edit)

        self._port_edit = QLineEdit()
        self._port_edit.setPlaceholderText("37001")
        self._port_edit.setText("37001")
        form.addRow("Pairing Port:", self._port_edit)

        self._code_edit = QLineEdit()
        self._code_edit.setPlaceholderText("123456")
        self._code_edit.setMaxLength(6)
        form.addRow("6-digit Code:", self._code_edit)

        layout.addLayout(form)

        # Progress
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        # Status label
        self._status = QLabel()
        self._status.setWordWrap(True)
        self._status.hide()
        layout.addWidget(self._status)

        # Buttons
        self._buttons = QDialogButtonBox()
        self._pair_btn = QPushButton("Pair Device")
        self._pair_btn.setObjectName("accent")
        self._pair_btn.clicked.connect(self._start_pairing)
        self._buttons.addButton(self._pair_btn, QDialogButtonBox.ButtonRole.AcceptRole)

        cancel_btn = self._buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.clicked.connect(self.reject)

        layout.addWidget(self._buttons)

    def _start_pairing(self) -> None:
        host = self._host_edit.text().strip()
        port_str = self._port_edit.text().strip()
        code = self._code_edit.text().strip()

        if not host:
            self._show_error("Enter the device IP address.")
            return
        if not port_str.isdigit():
            self._show_error("Port must be a number.")
            return
        if len(code) != 6 or not code.isdigit():
            self._show_error("Pairing code must be exactly 6 digits.")
            return

        port = int(port_str)
        self._pair_btn.setEnabled(False)
        self._progress.show()
        self._status.hide()

        self._worker = PairWorker(self._controller, host, port, code, self)
        self._worker.success.connect(self._on_success)
        self._worker.failure.connect(self._on_failure)
        self._worker.start()

    @Slot(str)
    def _on_success(self, msg: str) -> None:
        self._progress.hide()
        self._status.setText(f"✓ {msg}")
        self._status.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 600;")
        self._status.show()
        host = self._host_edit.text().strip()
        port = int(self._port_edit.text().strip())
        self.paired.emit(host, port)
        self.accept()

    @Slot(str)
    def _on_failure(self, msg: str) -> None:
        self._progress.hide()
        self._pair_btn.setEnabled(True)
        self._show_error(msg)

    def _show_error(self, msg: str) -> None:
        self._status.setText(f"✗ {msg}")
        self._status.setStyleSheet(f"color: {Colors.ERROR};")
        self._status.show()
