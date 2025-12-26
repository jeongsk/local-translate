# LocalTranslate 코드 및 기능 개선 계획

## 분석 요약

| 항목 | 현황 |
|------|------|
| 총 코드 라인 | 3,008 lines |
| 소스 모듈 | 13 files |
| 테스트 커버리지 | 0% (fixtures만 존재) |
| 주요 이슈 | 25+ 개선 포인트 식별 |

---

## 1. 즉시 수정 필요 (Critical)

### 1.1 Bare Exception 처리 수정
**파일**: `src/core/model_manager.py:269`

**현재 코드**:
```python
except:  # 모든 예외를 잡아버림
    stats["allocated_mb"] = 0
```

**수정 방향**:
```python
except (AttributeError, RuntimeError) as e:
    logger.warning(f"Memory stats unavailable: {e}")
    stats["allocated_mb"] = 0
```

**영향도**: 높음 - KeyboardInterrupt 등 시스템 예외도 잡히는 문제

---

### 1.2 Preferences 기본값 오류 수정 ✅ (완료)
**파일**: `src/core/preferences.py:23`

**수정 완료**:
```python
def __init__(self, organization: str = "LocalTranslate", application: str = "LocalTranslate"):
```

---

### 1.3 타입 힌트 오류 수정
**파일**: `src/core/translator.py:156`

**현재 코드**:
```python
progress_callback: Optional[callable] = None,
```

**수정 방향**:
```python
progress_callback: Optional[Callable[[int, str], None]] = None,
```

---

## 2. 테스트 구현 (High Priority)

### 2.1 필수 테스트 파일 생성

| 파일 | 테스트 케이스 수 | 우선순위 |
|------|-----------------|---------|
| `tests/unit/test_translator.py` | 20+ | P0 |
| `tests/unit/test_language_detector.py` | 10+ | P0 |
| `tests/unit/test_model_manager.py` | 15+ | P0 |
| `tests/unit/test_config.py` | 8+ | P1 |
| `tests/unit/test_preferences.py` | 10+ | P1 |
| `tests/integration/test_translation_workflow.py` | 8+ | P1 |
| `tests/ui/test_main_window.py` | 15+ | P2 |

### 2.2 테스트 케이스 목록

#### TranslationService 테스트
```python
# tests/unit/test_translator.py
class TestTranslationService:
    def test_translate_returns_task_id(self): ...
    def test_translate_with_debounce(self): ...
    def test_translate_without_debounce(self): ...
    def test_cancel_task(self): ...
    def test_cancel_all_tasks(self): ...
    def test_translation_signals_emitted(self): ...
    def test_empty_text_raises_error(self): ...
    def test_text_too_long_raises_error(self): ...
    def test_invalid_language_code(self): ...
    def test_auto_detect_language(self): ...
    # ... 등
```

#### LanguageDetector 테스트
```python
# tests/unit/test_language_detector.py
class TestLanguageDetector:
    def test_detect_korean(self): ...
    def test_detect_english(self): ...
    def test_detect_japanese(self): ...
    def test_detect_chinese(self): ...
    def test_detect_with_confidence(self): ...
    def test_detect_mixed_language(self): ...
    def test_detect_empty_string(self): ...
    def test_lingua_to_iso_mapping(self): ...
    # ... 등
```

---

## 3. 코드 품질 개선 (Medium Priority)

### 3.1 입력 검증 강화
**파일**: `src/core/translator.py`

**추가할 검증**:
```python
def translate(
    self,
    text: str,
    source_lang: str = "auto",
    target_lang: str = "Korean",
    debounce: bool = True,
) -> str:
    # 입력 검증 추가
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > config.performance.max_text_length:
        raise ValueError(f"Text exceeds maximum length of {config.performance.max_text_length}")

    if source_lang != "auto" and source_lang not in [lc.value for lc in LanguageCode]:
        raise ValueError(f"Invalid source language: {source_lang}")
```

### 3.2 MainWindow 리팩토링
**현재**: 451줄의 단일 파일

**분리 계획**:
```
src/ui/
├── main_window.py        # 메인 윈도우 (레이아웃만)
├── panels/
│   ├── language_panel.py   # 언어 선택 패널
│   ├── input_panel.py      # 원문 입력 패널
│   ├── output_panel.py     # 번역 결과 패널
│   └── action_panel.py     # 버튼 패널
└── widgets/
    └── translation_progress.py  # 프로그레스 위젯
```

### 3.3 에러 처리 개선
**파일**: `src/ui/main_window.py:390-400`

**현재**:
```python
self.result_text.setPlainText(f"❌ 번역 오류: {error_message}")
```

**개선**:
```python
def _on_translation_error(self, task_id: str, error_message: str) -> None:
    # 사용자 친화적 에러 메시지
    user_message = self._get_user_friendly_error(error_message)

    self.result_text.setPlainText(
        f"❌ 번역 실패\n\n"
        f"문제: {user_message}\n\n"
        f"해결 방법:\n"
        f"• 텍스트 길이를 확인해 주세요 (최대 2,000자)\n"
        f"• 지원되는 언어인지 확인해 주세요\n"
        f"• '번역' 버튼을 다시 눌러 재시도해 주세요"
    )

    # 재시도 버튼 표시
    self.retry_button.setVisible(True)
```

---

## 4. 성능 최적화 (Medium Priority)

### 4.1 언어 감지 캐시 개선
**파일**: `src/core/language_detector.py:150-158`

**현재**:
```python
@lru_cache(maxsize=1)
def get_language_detector() -> LanguageDetector:
```

**개선**:
```python
@lru_cache(maxsize=128)  # 캐시 크기 증가
def get_language_detector() -> LanguageDetector:
```

**추가**: 텍스트별 감지 결과 캐싱
```python
class LanguageDetector:
    def __init__(self):
        self._detection_cache: Dict[str, str] = {}
        self._cache_max_size = 100

    def detect(self, text: str) -> str:
        cache_key = text[:100]  # 처음 100자로 캐시 키
        if cache_key in self._detection_cache:
            return self._detection_cache[cache_key]

        result = self._do_detection(text)

        if len(self._detection_cache) >= self._cache_max_size:
            self._detection_cache.pop(next(iter(self._detection_cache)))
        self._detection_cache[cache_key] = result

        return result
```

### 4.2 스레드 풀 최적화
**파일**: `src/core/translator.py:47-49`

**현재**:
```python
self.thread_pool.setMaxThreadCount(2)
```

**개선**:
```python
import os
max_threads = min(4, os.cpu_count() or 2)
self.thread_pool.setMaxThreadCount(max_threads)
```

### 4.3 모델 로딩 타임아웃 추가
**파일**: `src/core/model_manager.py`

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def initialize(self, timeout: int = 300) -> bool:  # 5분 타임아웃
    """Initialize with timeout."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(self._do_initialize)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.error("Model loading timed out")
            raise RuntimeError("Model loading timed out after {timeout}s")
```

---

## 5. UI/UX 개선 (Medium Priority)

### 5.1 프로그레스 피드백 개선
**현재 진행률**: 10% → 20% → 50% → 100% (4단계)

**개선된 진행률**:
| 단계 | 진행률 | 메시지 |
|------|-------|--------|
| 언어 감지 시작 | 10% | "언어 감지 중..." |
| 언어 감지 완료 | 20% | "언어 감지 완료: {lang}" |
| 토큰화 | 30% | "입력 텍스트 처리 중..." |
| 모델 추론 시작 | 40% | "번역 모델 실행 중..." |
| 모델 추론 중 | 60% | "번역 생성 중..." |
| 디코딩 | 80% | "번역 결과 처리 중..." |
| 완료 | 100% | "번역 완료!" |

### 5.2 단축키 표시 개선
**파일**: `src/ui/main_window.py:122`

**현재**:
```python
self.translate_button = QPushButton("번역 (Translate)")
```

**개선**:
```python
self.translate_button = QPushButton("번역 (⌘⏎)")
self.translate_button.setToolTip("Cmd+Enter 또는 Ctrl+Enter로 번역")
```

### 5.3 언어 교환 버튼 상태 관리
**파일**: `src/ui/main_window.py`

```python
def _update_swap_button_state(self) -> None:
    """Update swap button enabled state based on source language."""
    source_lang = self.source_lang_selector.get_selected_language()
    is_auto = source_lang == "auto"

    self.swap_button.setEnabled(not is_auto)
    if is_auto:
        self.swap_button.setToolTip("자동 감지 모드에서는 언어 교환을 할 수 없습니다")
    else:
        self.swap_button.setToolTip("소스 ↔ 타겟 언어 교환")
```

### 5.4 번역 기록 기능 추가
**새 파일**: `src/core/history.py`

```python
@dataclass
class TranslationRecord:
    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: datetime
    duration_ms: int

class TranslationHistory:
    def __init__(self, max_size: int = 50):
        self.records: List[TranslationRecord] = []
        self.max_size = max_size

    def add(self, record: TranslationRecord) -> None: ...
    def get_recent(self, count: int = 10) -> List[TranslationRecord]: ...
    def search(self, query: str) -> List[TranslationRecord]: ...
    def clear(self) -> None: ...
```

---

## 6. 리소스 관리 개선 (High Priority)

### 6.1 예외 시 리소스 정리
**파일**: `src/main.py`

```python
def main() -> int:
    model_manager = None
    translation_service = None

    try:
        # ... 초기화 코드 ...
        model_manager = ModelManager()
        translation_service = TranslationService(model_manager, language_detector)
        # ... 나머지 코드 ...

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1

    finally:
        # 항상 리소스 정리
        if translation_service:
            translation_service.shutdown()
        if model_manager:
            model_manager.unload()
        logger.info("Resources cleaned up")
```

### 6.2 스레드 완료 대기 개선
**파일**: `src/main.py:139-141`

**현재** (폴링 방식):
```python
while thread.isRunning():
    app.processEvents()
    thread.wait(50)
```

**개선** (시그널 방식):
```python
from PySide6.QtCore import QEventLoop

loop = QEventLoop()
thread.finished.connect(loop.quit)
thread.start()

# 타임아웃 설정
QTimer.singleShot(config.performance.model_load_timeout * 1000, loop.quit)
loop.exec()

if thread.isRunning():
    logger.error("Model loading timed out")
    thread.terminate()
    return 1
```

---

## 7. 보안 강화 (Low Priority)

### 7.1 Rate Limiting 추가
**새 파일**: `src/utils/rate_limiter.py`

```python
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()

    def is_allowed(self) -> bool:
        now = time()
        # 윈도우 밖의 요청 제거
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

### 7.2 로그 디렉토리 권한 확인
**파일**: `src/utils/logger.py`

```python
def setup_logger(level: str = "INFO") -> None:
    log_dir = Path.home() / ".local_translate" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 권한 확인 및 설정
    import stat
    current_mode = log_dir.stat().st_mode
    if current_mode & stat.S_IRWXO:  # 다른 사용자 접근 가능
        log_dir.chmod(stat.S_IRWXU)  # 소유자만 접근
        logger.warning("Fixed log directory permissions")
```

---

## 8. 로깅 및 모니터링 개선 (Low Priority)

### 8.1 구조화된 로깅
**파일**: `src/utils/logger.py`

```python
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(self, event: str, **kwargs) -> None:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **kwargs
        }
        self.logger.info(json.dumps(log_data))

# 사용 예시
logger.log_event("translation_completed",
    task_id=task_id,
    duration_ms=elapsed_ms,
    source_lang=source_lang,
    target_lang=target_lang,
    text_length=len(text)
)
```

### 8.2 성능 메트릭 추가
**새 파일**: `src/utils/metrics.py`

```python
from dataclasses import dataclass, field
from typing import List
from statistics import mean, stdev

@dataclass
class TranslationMetrics:
    translation_times: List[float] = field(default_factory=list)
    detection_times: List[float] = field(default_factory=list)
    error_count: int = 0
    success_count: int = 0

    def add_translation(self, duration: float, success: bool) -> None:
        if success:
            self.translation_times.append(duration)
            self.success_count += 1
        else:
            self.error_count += 1

    def get_stats(self) -> dict:
        return {
            "avg_translation_time": mean(self.translation_times) if self.translation_times else 0,
            "std_translation_time": stdev(self.translation_times) if len(self.translation_times) > 1 else 0,
            "success_rate": self.success_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0,
            "total_translations": self.success_count + self.error_count
        }
```

---

## 9. 향후 기능 추가 계획 (Backlog)

### 9.1 배치 번역
- CSV/TXT 파일 가져오기
- 여러 텍스트 동시 번역
- 결과 내보내기

### 9.2 CLI 인터페이스
```bash
localtranslate "Hello, world!" --target ko
localtranslate --file input.txt --output output.txt --target ja
```

### 9.3 시스템 통합
- macOS Services 메뉴 통합
- 글로벌 단축키 지원
- 메뉴바 앱 모드

### 9.4 번역 즐겨찾기
- 자주 사용하는 번역 저장
- 템플릿 관리
- 태그 및 검색

### 9.5 번역 품질 피드백
- 번역 결과 평가 (좋음/나쁨)
- 개선 제안 수집
- 모델 fine-tuning 데이터 수집 (선택적)

---

## 실행 우선순위

### Phase 1: 버그 수정 및 안정화 (1주)
- [ ] Bare except 수정
- [ ] Preferences 기본값 수정
- [ ] 타입 힌트 오류 수정
- [ ] 리소스 정리 코드 추가

### Phase 2: 테스트 구현 (2주)
- [ ] unit/test_translator.py
- [ ] unit/test_language_detector.py
- [ ] unit/test_model_manager.py
- [ ] integration/test_translation_workflow.py

### Phase 3: UX 개선 (1주)
- [ ] 프로그레스 피드백 개선
- [ ] 에러 메시지 개선
- [ ] 단축키 표시
- [ ] 언어 교환 버튼 상태

### Phase 4: 성능 최적화 (1주)
- [ ] 캐시 최적화
- [ ] 스레드 풀 설정
- [ ] 타임아웃 추가

### Phase 5: 추가 기능 (Ongoing)
- [ ] 번역 기록
- [ ] 구조화된 로깅
- [ ] 성능 메트릭
- [ ] CLI 인터페이스

---

## 참고 자료

- [PySide6 문서](https://doc.qt.io/qtforpython/)
- [Transformers 문서](https://huggingface.co/docs/transformers)
- [pytest 문서](https://docs.pytest.org/)
- [Ruff 규칙](https://docs.astral.sh/ruff/rules/)
