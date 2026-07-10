"""File manager view for browsing and transferring device files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from voidremote.ui.theme import Colors

logger = logging.getLogger(__name__)


class ListDirWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, controller: object, serial: str, path: str, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._serial = serial
        self._path = path

    def run(self) -> None:
        try:
            raw = self._controller.shell(self._serial, f"ls -la '{self._path}'")
            entries = self._parse_ls(raw)
            self.finished.emit(entries)
        except Exception as exc:
            self.error.emit(str(exc))

    def _parse_ls(self, raw: str) -> list[dict]:
        entries: list[dict] = []
        for line in raw.splitlines():
            parts = line.split(None, 8)
            if len(parts) < 8:
                continue
            perms = parts[0]
            size = parts[4] if len(parts) > 4 else "0"
            name = parts[8] if len(parts) > 8 else parts[-1]
            if name in (".", ".."):
                continue
            entries.append({
                "name": name,
                "is_dir": perms.startswith("d"),
                "size": size,
                "permissions": perms,
            })
        return entries


class TransferWorker(QThread):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)

    def __init__(self, controller: object, serial: str, mode: str,
                 local: str, remote: str, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._serial = serial
        self._mode = mode
        self._local = local
        self._remote = remote

    def run(self) -> None:
        try:
            if self._mode == "push":
                self._controller.push_file(self._serial, Path(self._local), self._remote)
            else:
                self._controller.pull_file(self._serial, self._remote, Path(self._local))
            self.progress.emit(100)
            self.finished.emit()
        except Exception as exc:
            self.error.emit(str(exc))


class FilesView(QWidget):
    """ADB file manager with navigation, upload, and download."""

    def __init__(self, controller: object, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._serial: Optional[str] = None
        self._current_path = "/sdcard"
        self._path_history: list[str] = []
        self._worker: Optional[QThread] = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(24, 16, 24, 12)
        header.setSpacing(10)

        title = QLabel("Files")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        header.addWidget(title)
        header.addStretch()

        header.addWidget(QLabel("Device:"))
        self._device_combo = QComboBox()
        self._device_combo.setMinimumWidth(200)
        self._device_combo.currentTextChanged.connect(self._on_device_changed)
        header.addWidget(self._device_combo)

        header_w = QWidget()
        header_w.setStyleSheet(f"background: {Colors.BG_SURFACE}; border-bottom: 1px solid {Colors.BORDER};")
        header_w.setLayout(header)
        root.addWidget(header_w)

        # ── Path bar ─────────────────────────────────────
        path_bar = QHBoxLayout()
        path_bar.setContentsMargins(16, 8, 16, 8)
        path_bar.setSpacing(8)

        self._back_btn = QPushButton("←")
        self._back_btn.setFixedWidth(36)
        self._back_btn.clicked.connect(self._go_back)
        path_bar.addWidget(self._back_btn)

        self._path_edit = QLineEdit(self._current_path)
        self._path_edit.returnPressed.connect(self._navigate_to_path)
        path_bar.addWidget(self._path_edit, stretch=1)

        btn_go = QPushButton("Go")
        btn_go.setFixedWidth(40)
        btn_go.clicked.connect(self._navigate_to_path)
        path_bar.addWidget(btn_go)

        btn_upload = QPushButton("↑ Upload")
        btn_upload.clicked.connect(self._upload_file)
        path_bar.addWidget(btn_upload)

        btn_download = QPushButton("↓ Download")
        btn_download.clicked.connect(self._download_selected)
        path_bar.addWidget(btn_download)

        btn_refresh = QPushButton("↻")
        btn_refresh.setFixedWidth(36)
        btn_refresh.clicked.connect(self._load_directory)
        path_bar.addWidget(btn_refresh)

        path_bar_w = QWidget()
        path_bar_w.setStyleSheet(f"background: {Colors.BG_ELEVATED}; border-bottom: 1px solid {Colors.BORDER};")
        path_bar_w.setLayout(path_bar)
        root.addWidget(path_bar_w)

        # ── File table ───────────────────────────────────
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Permissions"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.doubleClicked.connect(self._on_double_click)
        root.addWidget(self._table, stretch=1)

        # ── Progress bar ─────────────────────────────────
        self._progress = QProgressBar()
        self._progress.hide()
        root.addWidget(self._progress)

        # ── Status ───────────────────────────────────────
        self._status = QLabel("Select a device to browse files")
        self._status.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; padding: 6px 24px; "
            f"background: {Colors.BG_SURFACE}; border-top: 1px solid {Colors.BORDER};"
        )
        root.addWidget(self._status)

    def set_devices(self, devices: list) -> None:
        current = self._device_combo.currentData()
        self._device_combo.blockSignals(True)
        self._device_combo.clear()
        for d in devices:
            self._device_combo.addItem(f"{d.info.display_name} ({d.serial})", userData=d.serial)
        idx = self._device_combo.findData(current)
        if idx >= 0:
            self._device_combo.setCurrentIndex(idx)
        self._device_combo.blockSignals(False)

    def _on_device_changed(self) -> None:
        self._serial = self._device_combo.currentData()
        if self._serial:
            self._current_path = "/sdcard"
            self._path_edit.setText(self._current_path)
            self._load_directory()

    def _navigate_to_path(self) -> None:
        path = self._path_edit.text().strip()
        if path:
            self._path_history.append(self._current_path)
            self._current_path = path
            self._load_directory()

    def _go_back(self) -> None:
        if self._path_history:
            self._current_path = self._path_history.pop()
            self._path_edit.setText(self._current_path)
            self._load_directory()

    def _load_directory(self) -> None:
        if not self._serial:
            return
        self._table.setRowCount(0)
        self._status.setText(f"Loading {self._current_path}…")
        w = ListDirWorker(self._controller, self._serial, self._current_path, self)
        w.finished.connect(self._on_entries_loaded)
        w.error.connect(lambda e: self._status.setText(f"Error: {e}"))
        self._worker = w
        w.start()

    @Slot(list)
    def _on_entries_loaded(self, entries: list) -> None:
        self._table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            icon = "📁" if entry["is_dir"] else "📄"
            self._table.setItem(row, 0, QTableWidgetItem(f"{icon}  {entry['name']}"))
            self._table.setItem(row, 1, QTableWidgetItem("Directory" if entry["is_dir"] else "File"))
            self._table.setItem(row, 2, QTableWidgetItem(entry["size"]))
            self._table.setItem(row, 3, QTableWidgetItem(entry["permissions"]))
            # Store full entry data
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, entry)  # type: ignore[attr-defined]
        self._status.setText(f"{len(entries)} items in {self._current_path}")

    def _on_double_click(self, index: object) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry and entry.get("is_dir"):
            self._path_history.append(self._current_path)
            self._current_path = f"{self._current_path.rstrip('/')}/{entry['name']}"
            self._path_edit.setText(self._current_path)
            self._load_directory()

    def _upload_file(self) -> None:
        if not self._serial:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select file to upload")
        if not path:
            return
        remote = f"{self._current_path.rstrip('/')}/{Path(path).name}"
        self._progress.setRange(0, 0)
        self._progress.show()
        w = TransferWorker(self._controller, self._serial, "push", path, remote, self)
        w.finished.connect(lambda: (self._progress.hide(), self._load_directory()))
        w.error.connect(lambda e: (self._progress.hide(), self._status.setText(f"Upload error: {e}")))
        self._worker = w
        w.start()

    def _download_selected(self) -> None:
        if not self._serial:
            return
        row = self._table.currentRow()
        if row < 0:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry or entry.get("is_dir"):
            self._status.setText("Select a file to download (not a directory)")
            return
        remote = f"{self._current_path.rstrip('/')}/{entry['name']}"
        local_dir = QFileDialog.getExistingDirectory(self, "Save to folder")
        if not local_dir:
            return
        local = str(Path(local_dir) / entry["name"])
        self._progress.setRange(0, 0)
        self._progress.show()
        w = TransferWorker(self._controller, self._serial, "pull", local, remote, self)
        w.finished.connect(lambda: (self._progress.hide(), self._status.setText(f"Downloaded to {local}")))
        w.error.connect(lambda e: (self._progress.hide(), self._status.setText(f"Download error: {e}")))
        self._worker = w
        w.start()
