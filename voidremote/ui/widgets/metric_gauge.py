"""Circular gauge widget for CPU/RAM/Battery monitoring."""

from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QBrush
from PySide6.QtWidgets import QWidget

from voidremote.ui.theme import Colors


class MetricGauge(QWidget):
    """
    Circular progress gauge for displaying a percentage metric.

    Shows value, label, and color-coded arc.
    """

    def __init__(
        self,
        label: str = "",
        color: str = Colors.ACCENT,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._label = label
        self._color = color
        self._value = 0.0
        self._suffix = "%"
        self.setMinimumSize(100, 100)

    def set_value(self, value: float) -> None:
        self._value = max(0.0, min(100.0, value))
        self.update()

    def set_label(self, label: str) -> None:
        self._label = label
        self.update()

    def set_suffix(self, suffix: str) -> None:
        self._suffix = suffix
        self.update()

    def paintEvent(self, event: object) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        size = min(w, h)
        margin = size * 0.1
        arc_rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)

        # Background track
        pen = QPen(QColor(Colors.BG_ELEVATED))
        pen.setWidth(int(size * 0.08))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(arc_rect, 225 * 16, -270 * 16)

        # Value arc
        if self._value > 0:
            val_color = QColor(self._color)
            val_pen = QPen(val_color)
            val_pen.setWidth(int(size * 0.08))
            val_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(val_pen)
            span = int(-270 * 16 * self._value / 100.0)
            painter.drawArc(arc_rect, 225 * 16, span)

        # Center text — value
        painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY)))
        value_font = QFont("Inter, Segoe UI", int(size * 0.2), QFont.Weight.Bold)
        painter.setFont(value_font)
        center_rect = QRectF(0, h * 0.3, w, h * 0.3)
        painter.drawText(
            center_rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self._value:.0f}{self._suffix}",
        )

        # Label below value
        painter.setPen(QPen(QColor(Colors.TEXT_MUTED)))
        label_font = QFont("Inter, Segoe UI", int(size * 0.1))
        painter.setFont(label_font)
        label_rect = QRectF(0, h * 0.58, w, h * 0.2)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self._label)
