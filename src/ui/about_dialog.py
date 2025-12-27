"""About dialog for displaying application information."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class AboutDialog(QDialog):
    """Dialog displaying application information."""

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize the About dialog.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.setWindowTitle(f"About {config.app_name}")
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        logger.debug("AboutDialog initialized")

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # App icon placeholder (if available)
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Try to load app icon, use text fallback if not found
        try:
            # Use application icon if available
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is not None and isinstance(app, QApplication) and not app.windowIcon().isNull():
                pixmap = app.windowIcon().pixmap(64, 64)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🌐")
                icon_label.setStyleSheet("font-size: 48px;")
        except Exception:
            icon_label.setText("🌐")
            icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)

        # App name
        name_label = QLabel(config.app_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"Version {config.version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("font-size: 14px; color: #666666;")
        layout.addWidget(version_label)

        # Copyright
        copyright_label = QLabel(f"© {config.copyright_year} {config.organization}")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("font-size: 12px; color: #888888;")
        layout.addWidget(copyright_label)

        # License
        license_label = QLabel(f"Licensed under {config.license_type}")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_label.setStyleSheet("font-size: 12px; color: #888888;")
        layout.addWidget(license_label)

        # GitHub link
        self._github_link = QLabel(f'<a href="{config.github_url}">GitHub Repository</a>')
        self._github_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._github_link.setOpenExternalLinks(True)
        self._github_link.setStyleSheet("font-size: 12px;")
        layout.addWidget(self._github_link)

        layout.addStretch()

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self._close_button = QPushButton("OK")
        self._close_button.setFixedWidth(80)
        self._close_button.clicked.connect(self.accept)
        button_layout.addWidget(self._close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _get_about_text(self) -> str:
        """
        Get the full about text for testing purposes.

        Returns:
            String containing all about information
        """
        return (
            f"{config.app_name} "
            f"Version {config.version} "
            f"Copyright © {config.copyright_year} {config.organization} "
            f"Licensed under {config.license_type} "
            f"{config.github_url}"
        )
