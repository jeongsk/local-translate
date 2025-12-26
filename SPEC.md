# 기능 명세서: 수동 번역 버튼 기능

## 개요

현재 자동 번역 방식(텍스트 입력 시 500ms debouncing 후 자동 번역)을 **수동 번역 버튼 방식**으로 변경합니다.

---

## 현재 동작 방식

### 자동 번역 흐름
```
사용자 텍스트 입력
    ↓
source_text.textChanged 시그널 발생
    ↓
_on_text_changed() 호출
    ↓
TranslationService.translate(debounce=True) 호출
    ↓
500ms debounce 타이머 시작
    ↓
타이머 만료 → 자동 번역 실행
```

### 관련 코드 위치
- `src/ui/main_window.py:155` - `textChanged` 시그널 연결
- `src/ui/main_window.py:226-253` - `_on_text_changed()` 메서드
- `src/ui/main_window.py:271-273` - 언어 변경 시 자동 재번역
- `src/core/translator.py:52-54` - debounce 타이머 설정

---

## 변경 후 동작 방식

### 수동 번역 흐름
```
사용자 텍스트 입력
    ↓
(아무 동작 없음 - 자동 번역 비활성화)
    ↓
사용자가 "번역" 버튼 클릭 또는 단축키(Cmd/Ctrl+Enter) 입력
    ↓
_on_translate_clicked() 호출
    ↓
TranslationService.translate(debounce=False) 호출
    ↓
즉시 번역 실행
```

---

## 상세 변경 사항

### 1. UI 변경 (`src/ui/main_window.py`)

#### 1.1 번역 버튼 추가
- **위치**: 원문 입력 필드(`source_text`) 아래, 프로그레스 바 위
- **버튼 텍스트**: "번역 (Translate)"
- **버튼 스타일**: 기본 액션 버튼 (강조 스타일)

```
┌─────────────────────────────────────────┐
│ 원문 (Source Text)                      │
│ ┌─────────────────────────────────────┐ │
│ │  (입력 텍스트 필드)                  │ │
│ └─────────────────────────────────────┘ │
│                        [번역 (Translate)]│  ← 새로 추가
├─────────────────────────────────────────┤
│ [████████████░░░░░░░░░░░░░░░ 45%]      │
```

#### 1.2 시그널 연결 변경

**제거할 연결:**
```python
# 기존: 텍스트 변경 시 자동 번역
self.source_text.textChanged.connect(self._on_text_changed)
```

**추가할 연결:**
```python
# 신규: 번역 버튼 클릭 시 번역 실행
self.translate_button.clicked.connect(self._on_translate_clicked)
```

#### 1.3 메서드 변경

**`_on_text_changed()` 수정:**
- 번역 실행 로직 제거
- 입력 유효성 검사만 수행 (텍스트 길이 체크)
- 번역 버튼 활성화/비활성화 상태 관리

**`_on_translate_clicked()` 신규 추가:**
- 기존 `_on_text_changed()`의 번역 실행 로직 이동
- `debounce=False`로 즉시 번역 실행

**`_on_language_changed()` 수정:**
- 자동 재번역 로직 제거 (기존 271-273 라인)

#### 1.4 키보드 단축키 추가

| 단축키 | 동작 |
|--------|------|
| `Cmd/Ctrl + Enter` | 번역 실행 |

### 2. TranslationService 변경 (`src/core/translator.py`)

- **변경 없음**: 기존 `translate()` 메서드는 `debounce` 파라미터를 지원하므로 수정 불필요
- UI에서 `debounce=False`로 호출하면 즉시 번역 실행

---

## 세부 구현 사항

### 번역 버튼 상태 관리

| 조건 | 버튼 상태 |
|------|----------|
| 텍스트 없음 | 비활성화 |
| 텍스트 길이 초과 | 비활성화 |
| 번역 진행 중 | 비활성화 |
| 유효한 텍스트 있음 | 활성화 |

### 번역 버튼 스타일

```python
# 강조 스타일 적용 (Primary Action Button)
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
```

---

## 파일 변경 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `src/ui/main_window.py` | 수정 | UI 및 이벤트 핸들러 변경 |

---

## 테스트 시나리오

### 기능 테스트

1. **번역 버튼 클릭**
   - 텍스트 입력 후 번역 버튼 클릭 → 번역 실행 확인

2. **단축키 테스트**
   - 텍스트 입력 후 `Cmd/Ctrl + Enter` → 번역 실행 확인

3. **자동 번역 비활성화 확인**
   - 텍스트 입력 후 대기 → 자동 번역이 실행되지 않음 확인

4. **버튼 상태 테스트**
   - 빈 텍스트: 버튼 비활성화
   - 텍스트 입력: 버튼 활성화
   - 텍스트 삭제: 버튼 비활성화
   - 번역 중: 버튼 비활성화

5. **언어 변경 테스트**
   - 언어 변경 시 자동 재번역이 실행되지 않음 확인

### 회귀 테스트

1. 기존 복사 버튼 동작 확인
2. 기존 지우기 버튼 동작 확인
3. 언어 교환(⇄) 버튼 동작 확인
4. 프로그레스 바 표시 확인
5. 에러 처리 동작 확인

---

## 마이그레이션 고려사항

- 사용자 설정 변경 없음
- 하위 호환성 문제 없음
- 기존 번역 기록/캐시에 영향 없음
