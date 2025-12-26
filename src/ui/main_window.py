"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QProgressBar,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QShortcut, QKeySequence

from utils.logger import get_logger
from core.translator import TranslationService
from core.preferences import UserPreferences
from core.config import config
from core.error_handler import ErrorType, TranslationError
from ui.language_selector import LanguageSelector

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main translation application window."""

    def __init__(
        self,
        translation_service: TranslationService,
        preferences: UserPreferences,
        theme_manager=None
    ):
        """
        Initialize main window.

        Args:
            translation_service: Translation service instance
            preferences: User preferences instance
            theme_manager: Theme manager instance (optional)
        """
        super().__init__()
        self.translation_service = translation_service
        self.preferences = preferences
        self.theme_manager = theme_manager
        self.current_task_id = None
        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(lambda: self.status_label.clear())

        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._restore_state()

        logger.info("MainWindow initialized")

    def _setup_ui(self) -> None:
        """Setup user interface."""
        self.setWindowTitle(config.app_name)
        self.setMinimumSize(config.window_min_width, config.window_min_height)
        self.resize(config.window_default_width, config.window_default_height)

        # Setup menu bar
        self._setup_menu_bar()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Language selection row
        lang_layout = QHBoxLayout()

        # Source language selector
        source_lang_label = QLabel("소스 언어:")
        lang_layout.addWidget(source_lang_label)

        self.source_lang_selector = LanguageSelector(
            include_auto=True,
            auto_label="자동 감지"
        )
        lang_layout.addWidget(self.source_lang_selector)

        lang_layout.addStretch()

        # Swap button (for future enhancement)
        self.swap_button = QPushButton("⇄")
        self.swap_button.setToolTip("언어 교환")
        self.swap_button.setMaximumWidth(50)
        lang_layout.addWidget(self.swap_button)

        lang_layout.addStretch()

        # Target language selector
        target_lang_label = QLabel("타겟 언어:")
        lang_layout.addWidget(target_lang_label)

        self.target_lang_selector = LanguageSelector(
            include_auto=False
        )
        lang_layout.addWidget(self.target_lang_selector)

        main_layout.addLayout(lang_layout)

        # Source text input
        source_label = QLabel("원문 (Source Text)")
        main_layout.addWidget(source_label)

        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("번역할 텍스트를 입력하세요...")
        self.source_text.setMinimumHeight(150)
        self.source_text.setAcceptRichText(False)
        main_layout.addWidget(self.source_text)

        # Translate button
        translate_button_layout = QHBoxLayout()
        translate_button_layout.addStretch()

        self.translate_button = QPushButton("번역 (⌘↵)")
        self.translate_button.setToolTip("Cmd+Enter 또는 Ctrl+Enter로 번역 실행")
        self.translate_button.setEnabled(False)
        self.translate_button.setMinimumWidth(140)
        self.translate_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        translate_button_layout.addWidget(self.translate_button)

        main_layout.addLayout(translate_button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Translation result
        result_label = QLabel("번역 결과 (Translation Result)")
        main_layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("번역 결과가 여기에 표시됩니다...")
        self.result_text.setMinimumHeight(150)
        main_layout.addWidget(self.result_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.copy_button = QPushButton("복사 (Copy)")
        self.copy_button.setEnabled(False)
        button_layout.addWidget(self.copy_button)

        self.clear_button = QPushButton("지우기 (Clear)")
        button_layout.addWidget(self.clear_button)

        main_layout.addLayout(button_layout)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Text input changes (for button state management)
        self.source_text.textChanged.connect(self._on_text_changed)

        # Translate button click
        self.translate_button.clicked.connect(self._on_translate_clicked)

        # Language selection changes
        self.source_lang_selector.languageChanged.connect(self._on_language_changed)
        self.target_lang_selector.languageChanged.connect(self._on_language_changed)
        self.swap_button.clicked.connect(self._on_swap_languages)

        # Translation service signals
        self.translation_service.translationStarted.connect(self._on_translation_started)
        self.translation_service.translationProgress.connect(self._on_translation_progress)
        self.translation_service.translationComplete.connect(self._on_translation_complete)
        self.translation_service.translationError.connect(self._on_translation_error)
        self.translation_service.translationRetrying.connect(self._on_translation_retrying)

        # Button clicks
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Cmd/Ctrl+C to copy translation result when result text has focus
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.result_text)
        copy_shortcut.activated.connect(self._on_copy_clicked)

        # Cmd/Ctrl+Enter to trigger translation
        translate_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        translate_shortcut.activated.connect(self._on_translate_clicked)

        # Also support Cmd+Enter on macOS (Ctrl+Return works as Cmd+Return)
        translate_shortcut_alt = QShortcut(QKeySequence("Meta+Return"), self)
        translate_shortcut_alt.activated.connect(self._on_translate_clicked)

        logger.debug("Keyboard shortcuts configured")

    def _setup_menu_bar(self) -> None:
        """Setup menu bar with File and View menus."""
        menubar = self.menuBar()

        # View menu
        view_menu = menubar.addMenu("&View")

        # Dark mode toggle action
        if self.theme_manager:
            self.dark_mode_action = view_menu.addAction("&Dark Mode")
            self.dark_mode_action.setCheckable(True)
            self.dark_mode_action.setChecked(self.theme_manager.is_dark_mode)
            self.dark_mode_action.triggered.connect(self._on_toggle_dark_mode)

        logger.debug("Menu bar configured")

    def _restore_state(self) -> None:
        """Restore window geometry and preferences."""
        geometry = self.preferences.window_geometry
        if geometry:
            self.restoreGeometry(geometry)
            logger.info("Window geometry restored")

        state = self.preferences.window_state
        if state:
            self.restoreState(state)
            logger.info("Window state restored")

        # Restore language preferences
        source_lang = self.preferences.source_language
        target_lang = self.preferences.target_language

        self.source_lang_selector.set_language(source_lang)
        self.target_lang_selector.set_language(target_lang)

        logger.info(f"Language preferences restored: {source_lang} -> {target_lang}")

        # Update swap button state based on restored language
        self._update_swap_button_state()

        # Restore dark mode preference
        if self.theme_manager and hasattr(self, 'dark_mode_action'):
            dark_mode = self.preferences.dark_mode
            self.theme_manager.is_dark_mode = dark_mode
            self.theme_manager.apply_theme()
            self.dark_mode_action.setChecked(dark_mode)
            logger.info(f"Dark mode preference restored: {dark_mode}")

    @Slot()
    def _on_text_changed(self) -> None:
        """Handle source text changes - manages translate button state."""
        text = self.source_text.toPlainText().strip()

        if not text:
            self.result_text.clear()
            self.status_label.clear()
            self.copy_button.setEnabled(False)
            self.translate_button.setEnabled(False)
            return

        # Validate text length
        if len(text) > config.performance.max_text_length:
            self.status_label.setText(
                f"⚠️ 텍스트가 너무 깁니다 ({len(text)} / {config.performance.max_text_length} 자)"
            )
            self.translate_button.setEnabled(False)
            return

        # Enable translate button for valid text
        self.translate_button.setEnabled(True)
        self.status_label.clear()

    @Slot()
    def _on_translate_clicked(self) -> None:
        """Handle translate button click."""
        text = self.source_text.toPlainText().strip()

        if not text:
            return

        # Get selected languages
        source_lang = self.source_lang_selector.get_selected_language()
        target_lang = self.target_lang_selector.get_selected_language()

        # Get target language display name
        target_display_name = self.target_lang_selector.get_language_display_name(target_lang)

        # Submit translation immediately (no debouncing)
        self.current_task_id = self.translation_service.translate(
            text=text, source_lang=source_lang, target_lang=target_display_name, debounce=False
        )
        logger.debug(f"Translation requested: {self.current_task_id}")

    @Slot(str)
    def _on_language_changed(self, language_code: str) -> None:
        """
        Handle language selection change.

        Args:
            language_code: The newly selected language code
        """
        # Save language preferences
        self.preferences.source_language = self.source_lang_selector.get_selected_language()
        self.preferences.target_language = self.target_lang_selector.get_selected_language()

        # Update swap button state
        self._update_swap_button_state()

        logger.info(f"Language changed: {self.preferences.source_language} -> {self.preferences.target_language}")

    def _update_swap_button_state(self) -> None:
        """Update swap button enabled state based on source language."""
        source_lang = self.source_lang_selector.get_selected_language()
        is_auto = source_lang == "auto"

        self.swap_button.setEnabled(not is_auto)
        if is_auto:
            self.swap_button.setToolTip("자동 감지 모드에서는 언어 교환을 할 수 없습니다")
        else:
            self.swap_button.setToolTip("소스 ↔ 타겟 언어 교환")

    @Slot()
    def _on_swap_languages(self) -> None:
        """Swap source and target languages."""
        source_lang = self.source_lang_selector.get_selected_language()
        target_lang = self.target_lang_selector.get_selected_language()

        # Can't swap if source is auto-detect
        if source_lang == "auto":
            logger.warning("Cannot swap languages when source is auto-detect")
            self.status_label.setText("⚠️ 자동 감지 모드에서는 언어 교환을 할 수 없습니다")
            return

        # Swap
        self.source_lang_selector.set_language(target_lang)
        self.target_lang_selector.set_language(source_lang)

        logger.info(f"Languages swapped: {target_lang} <-> {source_lang}")

        # Also swap the text content
        source_text = self.source_text.toPlainText()
        result_text = self.result_text.toPlainText()

        if result_text and result_text != "번역 결과가 여기에 표시됩니다...":
            self.source_text.setPlainText(result_text)
            self.result_text.setPlainText(source_text)

    @Slot(str)
    def _on_translation_started(self, task_id: str) -> None:
        """Handle translation started."""
        if task_id != self.current_task_id:
            return  # Ignore old tasks

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("번역 중...")
        self.copy_button.setEnabled(False)
        self.translate_button.setEnabled(False)
        logger.debug(f"Translation started: {task_id}")

    @Slot(str, int, str)
    def _on_translation_progress(self, task_id: str, percentage: int, message: str) -> None:
        """Handle translation progress."""
        if task_id != self.current_task_id:
            return  # Ignore old tasks

        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)

    @Slot(str, str, str)
    def _on_translation_complete(
        self, task_id: str, source_lang: str, translated_text: str
    ) -> None:
        """Handle translation completion."""
        if task_id != self.current_task_id:
            return  # Ignore old tasks

        self.result_text.setPlainText(translated_text)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✓ 번역 완료 (감지된 언어: {source_lang})")
        self.copy_button.setEnabled(True)
        self.translate_button.setEnabled(True)
        logger.info(f"Translation complete: {task_id}")

    @Slot(str, int, int, int)
    def _on_translation_retrying(
        self, task_id: str, attempt: int, max_attempts: int, delay_ms: int
    ) -> None:
        """Handle translation retry notification."""
        if task_id != self.current_task_id:
            return  # Ignore old tasks

        delay_sec = delay_ms / 1000
        self.status_label.setText(
            f"재시도 중... ({attempt}/{max_attempts}) - {delay_sec:.1f}초 후 재시도"
        )
        self.progress_bar.setFormat(f"재시도 대기 중... ({attempt}/{max_attempts})")
        logger.info(f"Retrying translation: {task_id}, attempt {attempt}/{max_attempts}")

    @Slot(str, object)
    def _on_translation_error(self, task_id: str, error) -> None:
        """Handle translation error with detailed information."""
        if task_id != self.current_task_id:
            return  # Ignore old tasks

        # Handle TranslationError object
        if isinstance(error, TranslationError):
            # Error type icons
            icons = {
                ErrorType.NETWORK: "🌐",
                ErrorType.MEMORY: "💾",
                ErrorType.MODEL: "🤖",
                ErrorType.TIMEOUT: "⏱️",
                ErrorType.VALIDATION: "⚠️",
                ErrorType.UNKNOWN: "❌",
            }
            icon = icons.get(error.error_type, "❌")

            # Detailed error message
            error_text = f"""{icon} 번역 오류

[원인]
{error.cause}

[해결 방법]
{error.solution}

[상세 정보]
{error.message}"""

            self.result_text.setPlainText(error_text)
            self.status_label.setText(f"{icon} 번역 실패 - {error.cause}")
            logger.error(f"Translation error: {error.error_type.name} - {error.message}")
        else:
            # Fallback for string error messages (backward compatibility)
            self.result_text.setPlainText(f"❌ 번역 오류: {error}")
            self.status_label.setText("번역 실패")
            logger.error(f"Translation error: {error}")

        self.progress_bar.setVisible(False)
        self.copy_button.setEnabled(False)
        self.translate_button.setEnabled(True)

    def _get_user_friendly_error(self, error_message: str) -> str:
        """Convert technical error message to user-friendly message."""
        error_lower = error_message.lower()

        if "memory" in error_lower or "oom" in error_lower:
            return "메모리가 부족합니다. 다른 프로그램을 종료하고 다시 시도해 주세요."
        elif "timeout" in error_lower:
            return "번역 시간이 초과되었습니다. 더 짧은 텍스트로 시도해 주세요."
        elif "model" in error_lower and "load" in error_lower:
            return "번역 모델을 불러올 수 없습니다. 앱을 재시작해 주세요."
        elif "empty" in error_lower:
            return "번역할 텍스트를 입력해 주세요."
        elif "too long" in error_lower:
            return "텍스트가 너무 깁니다. 2,000자 이하로 줄여주세요."
        else:
            return error_message

    @Slot()
    def _on_copy_clicked(self) -> None:
        """Handle copy button click."""
        from PySide6.QtWidgets import QApplication

        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("✓ 클립보드에 복사되었습니다")
            logger.info("Translation result copied to clipboard")

            # Clear status message after 2 seconds
            self.status_timer.start(2000)

    @Slot()
    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self.source_text.clear()
        self.result_text.clear()
        self.status_label.clear()
        self.progress_bar.setVisible(False)
        self.copy_button.setEnabled(False)
        logger.info("Text cleared")

    @Slot(bool)
    def _on_toggle_dark_mode(self, checked: bool) -> None:
        """
        Handle dark mode toggle.

        Args:
            checked: True if dark mode should be enabled
        """
        if self.theme_manager:
            self.theme_manager.is_dark_mode = checked
            self.theme_manager.apply_theme()

            # Save preference
            self.preferences.dark_mode = checked

            logger.info(f"Dark mode {'enabled' if checked else 'disabled'}")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Save window geometry
        self.preferences.window_geometry = self.saveGeometry()
        self.preferences.window_state = self.saveState()
        self.preferences.sync()

        logger.info("Window state saved")
        super().closeEvent(event)
