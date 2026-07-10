"""
VoidRemote GUI application entry point.

Bootstraps QApplication, applies theme, initializes controller,
and launches the main window.
"""

from __future__ import annotations

import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def main() -> None:
    """Launch the VoidRemote GUI application."""
    # Must import PySide6 before any other Qt symbols
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

    from voidremote.config.settings import ensure_dirs, get_settings, LOG_FILE
    from voidremote.utils.logging import setup_logging
    from voidremote.controllers.app_controller import AppController
    from voidremote.ui.theme import apply_dark_theme
    from voidremote.ui.main_window import MainWindow

    ensure_dirs()
    settings = get_settings()

    setup_logging(
        level=settings.logging.level,
        log_file=LOG_FILE if settings.logging.file_enabled else None,
        console=settings.logging.console_enabled,
        console_color=settings.logging.console_color,
    )

    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("VoidRemote")
    app.setApplicationDisplayName("VoidRemote")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("V0IDNETWORK")
    app.setOrganizationDomain("voidNetwork.ir")

    # Apply dark theme
    apply_dark_theme(app)

    # Set default font
    font = QFont(settings.ui.font_family, settings.ui.font_size)
    app.setFont(font)

    # Create controller (no initialize() yet — done lazily in MainWindow)
    controller = AppController(settings)

    window = MainWindow(controller)
    window.show()

    logger.info("VoidRemote GUI started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
