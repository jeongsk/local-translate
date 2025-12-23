"""Splash screen for model loading."""

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SplashScreen(QSplashScreen):
    """Splash screen displayed during model loading."""

    def __init__(self):
        """Initialize splash screen."""
        # Create a simple colored pixmap
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor(30, 30, 30))

        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # Create layout
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Open DeepL")
        title_label.setStyleSheet(
            "color: white; font-size: 32px; font-weight: bold; qproperty-alignment: AlignCenter;"
        )
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("로컬 번역 애플리케이션")
        subtitle_label.setStyleSheet(
            "color: #dcdcdc; font-size: 16px; qproperty-alignment: AlignCenter;"
        )
        layout.addWidget(subtitle_label)

        layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
                color: white;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007aff;
                border-radius: 3px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Status message
        self.status_label = QLabel("초기화 중...")
        self.status_label.setStyleSheet(
            "color: #dcdcdc; font-size: 13px; qproperty-alignment: AlignCenter;"
        )
        layout.addWidget(self.status_label)

        widget.setGeometry(0, 0, 500, 300)

        logger.info("SplashScreen initialized")

    def show_progress(self, percentage: int, message: str) -> None:
        """
        Update progress display.

        Args:
            percentage: Progress percentage (0-100)
            message: Status message
        """
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        # Don't call repaint() - let Qt event loop handle updates
        # Calling repaint() from background thread causes QPainter errors
        logger.debug(f"Splash: {percentage}% - {message}")

    def show_error(self, error_message: str) -> None:
        """
        Display error message.

        Args:
            error_message: Error message to display
        """
        self.status_label.setText(f"❌ 오류: {error_message}")
        self.status_label.setStyleSheet(
            "color: #ff3b30; font-size: 13px; qproperty-alignment: AlignCenter;"
        )
        # Don't call repaint() - let Qt event loop handle updates
        logger.error(f"Splash error: {error_message}")
