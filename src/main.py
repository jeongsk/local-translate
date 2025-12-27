"""Application entry point."""

import sys
from pathlib import Path

# PyInstaller 호환성: 실행 파일 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 빌드된 경우
    _base_path = Path(sys._MEIPASS)
    # src 디렉토리를 sys.path에 추가
    _src_path = _base_path / 'src'
    if _src_path.exists() and str(_src_path) not in sys.path:
        sys.path.insert(0, str(_src_path))
    if str(_base_path) not in sys.path:
        sys.path.insert(0, str(_base_path))
else:
    # 개발 환경에서 실행되는 경우
    _src_path = Path(__file__).parent
    if str(_src_path) not in sys.path:
        sys.path.insert(0, str(_src_path))

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from core.config import config
from core.history_store import HistoryStore
from core.language_detector import LanguageDetector
from core.model_manager import ModelManager
from core.preferences import UserPreferences
from core.translator import TranslationService
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from ui.styles import ThemeManager
from utils.logger import get_logger, setup_logger

# Setup logging
setup_logger(level="INFO")
logger = get_logger(__name__)


class ModelLoader(QObject):
    """Worker for loading model in background thread."""

    progress = Signal(int, str)
    finished = Signal(bool, str)  # success, message

    def __init__(self, model_manager: ModelManager):
        super().__init__()
        self.model_manager = model_manager

    def run(self) -> None:
        """Load the model."""
        try:
            logger.info("Starting model loading in background...")
            self.model_manager.set_progress_callback(self._on_progress)
            success = self.model_manager.initialize()

            if success:
                self.finished.emit(True, "Model loaded successfully")
            else:
                self.finished.emit(False, "Model loading failed")

        except Exception as e:
            logger.error(f"Model loading error: {e}", exc_info=True)
            self.finished.emit(False, str(e))

    def _on_progress(self, percentage: int, message: str) -> None:
        """Forward progress to UI thread."""
        self.progress.emit(percentage, message)


def main() -> int:
    """
    Main application entry point.

    Returns:
        Exit code
    """
    logger.info("=" * 60)
    logger.info(f"Starting {config.app_name} v{config.version}")
    logger.info("=" * 60)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setOrganizationName(config.organization)

    # Initialize theme manager
    theme_manager = ThemeManager(app)
    theme_manager.apply_theme()

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    splash.show_progress(0, "애플리케이션 초기화 중...")
    app.processEvents()

    # Track resources for cleanup
    model_manager = None
    translation_service = None
    exit_code = 1

    try:
        # Initialize components
        splash.show_progress(5, "사용자 설정 로드 중...")
        preferences = UserPreferences(config.organization, config.app_name)

        splash.show_progress(8, "번역 기록 로드 중...")
        history_store = HistoryStore(preferences._settings)
        history_store.load()
        logger.info(f"History loaded: {history_store.count} entries")

        splash.show_progress(10, "언어 감지기 초기화 중...")
        language_detector = LanguageDetector()

        splash.show_progress(15, "모델 관리자 초기화 중...")
        model_manager = ModelManager()

        # Load model in background (this will take time)
        splash.show_progress(20, "번역 모델 로딩 중 (시간이 걸릴 수 있습니다)...")

        # Create model loader
        loader = ModelLoader(model_manager)
        thread = QThread()
        loader.moveToThread(thread)

        # Connect signals
        def update_progress(p: int, m: str) -> None:
            splash.show_progress(p, m)
            app.processEvents()  # Process events after each update

        loader.progress.connect(update_progress)

        model_loaded = [False, ""]  # [success, message]

        def on_model_loaded(success: bool, message: str) -> None:
            model_loaded[0] = success
            model_loaded[1] = message
            thread.quit()

        loader.finished.connect(on_model_loaded)
        thread.started.connect(loader.run)

        # Start loading
        thread.start()

        # Wait for model to load (with event processing)
        logger.info("Waiting for model loading thread to finish...")
        while thread.isRunning():
            app.processEvents()
            thread.wait(50)  # Shorter wait for more responsive UI

        logger.info(f"Thread finished. Model loaded: {model_loaded}")

        # Check if loading succeeded
        if not model_loaded[0]:
            error_msg = model_loaded[1] or "Unknown error"
            logger.error(f"Model loading failed: {error_msg}")
            splash.show_error(error_msg)
            splash.show()
            app.processEvents()

            # Show error dialog
            QMessageBox.critical(
                None,
                "모델 로딩 실패",
                f"번역 모델을 로드할 수 없습니다:\n\n{error_msg}\n\n"
                f"최소 8GB RAM과 10GB 여유 저장공간이 필요합니다.",
            )
            return 1

        logger.info("Model loaded successfully")

        # Initialize translation service
        splash.show_progress(95, "번역 서비스 초기화 중...")
        logger.info("Creating TranslationService...")
        translation_service = TranslationService(model_manager, language_detector)
        logger.info("TranslationService created")

        # Create main window
        splash.show_progress(98, "메인 윈도우 생성 중...")
        logger.info("Creating MainWindow...")
        window = MainWindow(translation_service, preferences, history_store, theme_manager)
        logger.info("MainWindow created")

        # Show main window and close splash
        splash.show_progress(100, "완료!")
        app.processEvents()

        logger.info("Showing main window...")
        window.show()
        logger.info("Finishing splash screen...")
        splash.finish(window)
        logger.info("Splash screen finished")

        logger.info(f"{config.app_name} started successfully")

        # Run application
        exit_code = app.exec()
        logger.info(f"{config.app_name} exited with code {exit_code}")

    except Exception as e:
        logger.error(f"Application startup error: {e}", exc_info=True)
        splash.show_error(str(e))

        # Show error dialog
        QMessageBox.critical(
            None,
            "시작 오류",
            f"애플리케이션을 시작할 수 없습니다:\n\n{e}",
        )
        exit_code = 1

    finally:
        # Always cleanup resources
        logger.info("Cleaning up resources...")
        if translation_service is not None:
            try:
                translation_service.shutdown()
                logger.info("Translation service shut down")
            except Exception as e:
                logger.error(f"Error shutting down translation service: {e}")

        if model_manager is not None:
            try:
                model_manager.unload()
                logger.info("Model manager unloaded")
            except Exception as e:
                logger.error(f"Error unloading model manager: {e}")

        logger.info("Resource cleanup complete")

    return exit_code


if __name__ == "__main__":
    # PyInstaller frozen 환경에서 multiprocessing 지원
    from multiprocessing import freeze_support
    freeze_support()

    sys.exit(main())
