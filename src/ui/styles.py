"""Theme management for dark/light mode support."""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QObject, Signal

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ThemeManager(QObject):
    """Manages application theme with dark/light mode support."""

    themeChanged = Signal(bool)  # is_dark_mode

    def __init__(self, app: QApplication):
        """
        Initialize theme manager.

        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app
        self.is_dark_mode = self._detect_dark_mode()

        # Connect to palette changes (macOS system appearance changes)
        self.app.paletteChanged.connect(self._on_system_theme_changed)

        logger.info(f"ThemeManager initialized (dark_mode: {self.is_dark_mode})")

    def _detect_dark_mode(self) -> bool:
        """
        Detect if system is in dark mode.

        Returns:
            True if dark mode, False otherwise
        """
        palette = self.app.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        # Dark mode typically has darker background (lightness < 128)
        is_dark = bg_color.lightness() < 128
        return is_dark

    def _on_system_theme_changed(self, palette: QPalette) -> None:
        """
        Handle system theme changes.

        Args:
            palette: New palette from system
        """
        old_dark = self.is_dark_mode
        self.is_dark_mode = self._detect_dark_mode()

        if old_dark != self.is_dark_mode:
            logger.info(f"System theme changed to: {'dark' if self.is_dark_mode else 'light'}")
            self.apply_theme()
            self.themeChanged.emit(self.is_dark_mode)

    def apply_theme(self) -> None:
        """Apply current theme to the application."""
        if self.is_dark_mode:
            self._apply_dark_palette()
        else:
            self._apply_light_palette()

        # Apply custom stylesheets for specific widgets
        self._apply_custom_styles()

        logger.info(f"Applied {'dark' if self.is_dark_mode else 'light'} theme")

    def _apply_dark_palette(self) -> None:
        """Apply dark mode palette."""
        palette = QPalette()

        # Primary colors
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 150, 255))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(150, 100, 255))

        # Highlights
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(100, 100, 100)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(100, 100, 100)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(100, 100, 100)
        )

        self.app.setPalette(palette)

    def _apply_light_palette(self) -> None:
        """Apply light mode palette."""
        palette = QPalette()

        # Primary colors
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))

        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 100, 255))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(120, 0, 180))

        # Highlights
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Disabled colors
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(150, 150, 150)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(150, 150, 150)
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(150, 150, 150)
        )

        self.app.setPalette(palette)

    def _apply_custom_styles(self) -> None:
        """Apply custom QStyleSheet for specific widgets."""
        if self.is_dark_mode:
            custom_css = """
                QTextEdit, QPlainTextEdit {
                    background-color: #1e1e1e;
                    color: #dcdcdc;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }

                QTextEdit:focus, QPlainTextEdit:focus {
                    border: 1px solid #007aff;
                }

                QPushButton {
                    background-color: #2d2d2d;
                    color: #dcdcdc;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton:hover {
                    background-color: #3c3c3c;
                }

                QPushButton:pressed {
                    background-color: #1e1e1e;
                }

                QProgressBar {
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #1e1e1e;
                }

                QProgressBar::chunk {
                    background-color: #007aff;
                    border-radius: 3px;
                }

                QLabel {
                    color: #dcdcdc;
                }
            """
        else:
            custom_css = """
                QTextEdit, QPlainTextEdit {
                    background-color: #ffffff;
                    color: #1e1e1e;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }

                QTextEdit:focus, QPlainTextEdit:focus {
                    border: 1px solid #007aff;
                }

                QPushButton {
                    background-color: #f0f0f0;
                    color: #1e1e1e;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton:hover {
                    background-color: #e0e0e0;
                }

                QPushButton:pressed {
                    background-color: #d0d0d0;
                }

                QProgressBar {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #f0f0f0;
                }

                QProgressBar::chunk {
                    background-color: #007aff;
                    border-radius: 3px;
                }

                QLabel {
                    color: #1e1e1e;
                }
            """

        self.app.setStyleSheet(custom_css)

    def toggle_theme(self) -> None:
        """Toggle between dark and light modes."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        self.themeChanged.emit(self.is_dark_mode)
        logger.info(f"Toggled theme to: {'dark' if self.is_dark_mode else 'light'}")
