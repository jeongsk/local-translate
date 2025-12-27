"""Update dialog for displaying update check results."""

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
from core.update_checker import UpdateCheckResult, UpdateStatus
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateDialog(QDialog):
    """Dialog displaying update check results."""

    def __init__(self, check_result: UpdateCheckResult, parent: QWidget | None = None):
        """
        Initialize the Update dialog.

        Args:
            check_result: Update check result
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self._check_result = check_result
        self.setWindowTitle("업데이트 확인")
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()
        logger.debug(f"UpdateDialog initialized with status: {self._check_result.status}")

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Status icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setText(self._get_status_icon())
        layout.addWidget(icon_label)

        # Message
        self._message_label = QLabel()
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet("font-size: 14px;")
        self._message_label.setText(self._get_message())
        layout.addWidget(self._message_label)

        # Download link (only visible when update is available)
        self._download_link = QLabel()
        self._download_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._download_link.setOpenExternalLinks(True)
        self._download_link.setStyleSheet("font-size: 12px;")

        if self._check_result.is_update_available and self._check_result.download_url:
            self._download_link.setText(
                f'<a href="{self._check_result.download_url}">다운로드 페이지 열기</a>'
            )
            self._download_link.setVisible(True)
        else:
            self._download_link.setVisible(False)

        layout.addWidget(self._download_link)

        layout.addStretch()

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("확인")
        close_button.setFixedWidth(80)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _get_status_icon(self) -> str:
        """Get the status icon based on result status."""
        icons = {
            UpdateStatus.UP_TO_DATE: "✅",
            UpdateStatus.UPDATE_AVAILABLE: "🎉",
            UpdateStatus.ERROR: "❌",
            UpdateStatus.RATE_LIMITED: "⚠️",
            UpdateStatus.CHECKING: "🔄",
        }
        return icons.get(self._check_result.status, "ℹ️")

    def _get_message(self) -> str:
        """Get the message based on result status."""
        if self._check_result.status == UpdateStatus.UP_TO_DATE:
            return f"{config.app_name} {self._check_result.current_version}은(는)\n이미 최신 버전입니다."

        elif self._check_result.status == UpdateStatus.UPDATE_AVAILABLE:
            latest = self._check_result.latest_release
            if latest:
                return (
                    f"새로운 버전이 있습니다!\n\n"
                    f"현재 버전: {self._check_result.current_version}\n"
                    f"최신 버전: {latest.version}"
                )
            return "새로운 버전이 있습니다!"

        elif self._check_result.status == UpdateStatus.ERROR:
            return (
                f"업데이트 확인 중 오류가 발생했습니다.\n\n{self._check_result.error_message or ''}"
            )

        elif self._check_result.status == UpdateStatus.RATE_LIMITED:
            return "업데이트 확인 요청 한도를 초과했습니다.\n\n" "잠시 후 다시 시도해주세요."

        return "업데이트 확인 중..."
