"""
VoidRemote dark theme and style definitions.

Provides QSS stylesheets, color palettes, and font definitions
for the PySide6 GUI.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


# ------------------------------------------------------------------
# Color Palette
# ------------------------------------------------------------------

class Colors:
    """VoidRemote design system colors."""

    # Backgrounds
    BG_BASE = "#0d1117"
    BG_SURFACE = "#161b22"
    BG_ELEVATED = "#1c2128"
    BG_OVERLAY = "#22272e"

    # Sidebar
    SIDEBAR_BG = "#0d1117"
    SIDEBAR_ACTIVE = "#1c2128"
    SIDEBAR_HOVER = "#161b22"

    # Accent
    ACCENT = "#4f8ef7"
    ACCENT_HOVER = "#6ba3f8"
    ACCENT_PRESSED = "#3a7af5"
    ACCENT_DIM = "rgba(79, 142, 247, 0.15)"

    # Status
    SUCCESS = "#3fb950"
    WARNING = "#d29922"
    ERROR = "#f85149"
    INFO = "#58a6ff"

    # Text
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#484f58"
    TEXT_ON_ACCENT = "#ffffff"

    # Borders
    BORDER = "#30363d"
    BORDER_FOCUS = "#4f8ef7"
    BORDER_SUBTLE = "#21262d"

    # Buttons
    BTN_BG = "#21262d"
    BTN_HOVER = "#30363d"
    BTN_PRESSED = "#1c2128"

    # Device card
    CARD_BG = "#161b22"
    CARD_BORDER = "#30363d"

    # Battery
    BATTERY_FULL = "#3fb950"
    BATTERY_MID = "#d29922"
    BATTERY_LOW = "#f85149"


DARK_STYLESHEET = """
/* ============================================================
   VoidRemote Dark Theme — Qt Style Sheet
   ============================================================ */

* {
    font-family: "Inter", "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT_PRIMARY};
    outline: none;
}

QMainWindow, QDialog, QWidget#MainWidget {{
    background-color: {BG_BASE};
    border: none;
}}

/* ---- Scroll Bars ---- */
QScrollBar:vertical {{
    background: {BG_SURFACE};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_SURFACE};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 4px;
    min-width: 32px;
}}

/* ---- Tool Bar ---- */
QToolBar {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER};
    spacing: 4px;
    padding: 4px 8px;
}}
QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT_SECONDARY};
}}
QToolButton:hover {{
    background: {BTN_HOVER};
    color: {TEXT_PRIMARY};
    border-color: {BORDER};
}}
QToolButton:pressed {{
    background: {BTN_PRESSED};
}}

/* ---- Status Bar ---- */
QStatusBar {{
    background-color: {BG_SURFACE};
    border-top: 1px solid {BORDER};
    color: {TEXT_SECONDARY};
    font-size: 12px;
    padding: 2px 8px;
}}

/* ---- Tab Widget ---- */
QTabWidget::pane {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 8px 18px;
    margin-right: 2px;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT_PRIMARY};
}}

/* ---- Push Button ---- */
QPushButton {{
    background: {BTN_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 16px;
    color: {TEXT_PRIMARY};
    font-weight: 500;
}}
QPushButton:hover {{
    background: {BTN_HOVER};
    border-color: {TEXT_MUTED};
}}
QPushButton:pressed {{
    background: {BTN_PRESSED};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    background: {BG_ELEVATED};
    border-color: {BORDER_SUBTLE};
}}
QPushButton#accent {{
    background: {ACCENT};
    border-color: {ACCENT};
    color: {TEXT_ON_ACCENT};
}}
QPushButton#accent:hover {{
    background: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}
QPushButton#accent:pressed {{
    background: {ACCENT_PRESSED};
}}
QPushButton#danger {{
    background: transparent;
    border-color: {ERROR};
    color: {ERROR};
}}
QPushButton#danger:hover {{
    background: rgba(248, 81, 73, 0.15);
}}

/* ---- Line Edit ---- */
QLineEdit {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_DIM};
}}
QLineEdit:focus {{
    border-color: {BORDER_FOCUS};
    background: {BG_OVERLAY};
}}
QLineEdit:disabled {{
    color: {TEXT_MUTED};
    background: {BG_SURFACE};
}}

/* ---- Combo Box ---- */
QComboBox {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    color: {TEXT_PRIMARY};
}}
QComboBox:hover {{
    border-color: {TEXT_MUTED};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {BG_OVERLAY};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT_DIM};
    outline: none;
}}

/* ---- Spin Box ---- */
QSpinBox, QDoubleSpinBox {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    color: {TEXT_PRIMARY};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {BORDER_FOCUS};
}}

/* ---- Check Box ---- */
QCheckBox {{
    spacing: 8px;
    color: {TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG_ELEVATED};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ---- Radio Button ---- */
QRadioButton {{
    spacing: 8px;
    color: {TEXT_PRIMARY};
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {BG_ELEVATED};
}}
QRadioButton::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ---- Progress Bar ---- */
QProgressBar {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 11px;
    height: 8px;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 3px;
}}

/* ---- Slider ---- */
QSlider::groove:horizontal {{
    background: {BG_ELEVATED};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 14px;
    height: 14px;
    border-radius: 7px;
    margin: -5px 0;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

/* ---- List / Tree / Table Widgets ---- */
QListWidget, QTreeWidget, QTableWidget {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    alternate-background-color: {BG_ELEVATED};
    gridline-color: {BORDER_SUBTLE};
    outline: none;
}}
QListWidget::item, QTreeWidget::item, QTableWidget::item {{
    padding: 6px 8px;
    border: none;
}}
QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
    background: {ACCENT_DIM};
    color: {TEXT_PRIMARY};
    border-radius: 4px;
}}
QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
    background: {BG_ELEVATED};
}}
QHeaderView::section {{
    background: {BG_OVERLAY};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    padding: 6px 12px;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ---- Group Box ---- */
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 600;
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {TEXT_SECONDARY};
}}

/* ---- Splitter ---- */
QSplitter::handle {{
    background: {BORDER};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

/* ---- Menu ---- */
QMenuBar {{
    background: {BG_SURFACE};
    border-bottom: 1px solid {BORDER};
    color: {TEXT_SECONDARY};
    padding: 2px;
}}
QMenuBar::item {{
    padding: 6px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {BTN_HOVER};
    color: {TEXT_PRIMARY};
}}
QMenu {{
    background: {BG_OVERLAY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 18px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {ACCENT_DIM};
    color: {TEXT_PRIMARY};
}}
QMenu::separator {{
    background: {BORDER};
    height: 1px;
    margin: 4px 8px;
}}

/* ---- Tooltip ---- */
QToolTip {{
    background: {BG_OVERLAY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    padding: 6px 10px;
    font-size: 12px;
}}

/* ---- Text Edit / Plain Text Edit ---- */
QTextEdit, QPlainTextEdit {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_DIM};
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas", monospace;
    font-size: 13px;
}}
QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {BORDER_FOCUS};
}}

/* ---- Sidebar List ---- */
QListWidget#Sidebar {{
    background: {SIDEBAR_BG};
    border: none;
    border-right: 1px solid {BORDER};
    border-radius: 0;
    padding: 8px 0;
}}
QListWidget#Sidebar::item {{
    padding: 10px 16px;
    border-radius: 0;
    margin: 1px 8px;
    border-radius: 6px;
    color: {TEXT_SECONDARY};
}}
QListWidget#Sidebar::item:selected {{
    background: {SIDEBAR_ACTIVE};
    color: {TEXT_PRIMARY};
}}
QListWidget#Sidebar::item:hover:!selected {{
    background: {SIDEBAR_HOVER};
    color: {TEXT_PRIMARY};
}}

/* ---- Device Cards ---- */
QFrame#DeviceCard {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    padding: 16px;
}}
QFrame#DeviceCard:hover {{
    border-color: {ACCENT};
}}

/* ---- Log View ---- */
QTextEdit#LogView {{
    background: {BG_BASE};
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
    color: {TEXT_SECONDARY};
    border: none;
    padding: 12px;
}}
""".format(**{k: v for k, v in Colors.__dict__.items() if not k.startswith("_")})


def apply_dark_theme(app: QApplication) -> None:
    """Apply the VoidRemote dark theme to a QApplication."""
    app.setStyleSheet(DARK_STYLESHEET)

    # Also set QPalette for native widgets
    palette = QPalette()
    bg = QColor(Colors.BG_BASE)
    surface = QColor(Colors.BG_SURFACE)
    text = QColor(Colors.TEXT_PRIMARY)
    text_dim = QColor(Colors.TEXT_SECONDARY)
    accent = QColor(Colors.ACCENT)
    border = QColor(Colors.BORDER)

    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, surface)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.BG_ELEVATED))
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, QColor(Colors.BTN_BG))
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_ON_ACCENT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.BG_OVERLAY))
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.PlaceholderText, text_dim)
    palette.setColor(QPalette.ColorRole.Link, accent)
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(Colors.ACCENT_PRESSED))

    app.setPalette(palette)
