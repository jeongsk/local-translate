# Quickstart: About 및 Update Check 메뉴

**Feature Branch**: `003-about-update-menu`
**Date**: 2025-12-27

## Prerequisites

- Python 3.11+
- 기존 local-translate 프로젝트 설치 완료
- 인터넷 연결 (Update Check 기능 테스트 시)

## Quick Test

### 1. About 대화상자 테스트

```python
# tests/unit/test_about_dialog.py
import pytest
from PySide6.QtWidgets import QApplication
from ui.about_dialog import AboutDialog
from core.config import config

def test_about_dialog_shows_version(qapp):
    dialog = AboutDialog()
    assert config.version in dialog.version_label.text()

def test_about_dialog_has_github_link(qapp):
    dialog = AboutDialog()
    assert "github.com" in dialog.github_link.text()
```

### 2. Update Checker 테스트

```python
# tests/unit/test_update_checker.py
import pytest
from unittest.mock import patch, MagicMock
from core.update_checker import UpdateChecker, UpdateStatus

def test_check_for_updates_returns_up_to_date():
    """현재 버전이 최신일 때 UP_TO_DATE 반환."""
    mock_response = {
        "tag_name": "v0.1.2",
        "html_url": "https://github.com/...",
        "prerelease": False,
        "draft": False,
    }

    with patch("core.update_checker.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_response).encode()
        )

        checker = UpdateChecker(current_version="0.1.2")
        result = checker.check()

        assert result.status == UpdateStatus.UP_TO_DATE

def test_check_for_updates_returns_available():
    """새 버전이 있을 때 UPDATE_AVAILABLE 반환."""
    mock_response = {
        "tag_name": "v1.0.0",
        "html_url": "https://github.com/...",
        "prerelease": False,
        "draft": False,
    }

    with patch("core.update_checker.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = (
            json.dumps(mock_response).encode()
        )

        checker = UpdateChecker(current_version="0.1.2")
        result = checker.check()

        assert result.status == UpdateStatus.UPDATE_AVAILABLE
        assert result.latest_release.version == "1.0.0"
```

### 3. 버전 비교 테스트

```python
# tests/unit/test_version.py
import pytest
from utils.version import compare_versions, normalize_version

@pytest.mark.parametrize("v1,v2,expected", [
    ("0.1.0", "0.1.1", -1),
    ("1.0.0", "0.9.9", 1),
    ("1.0.0", "1.0.0", 0),
    ("v1.0.0", "1.0.0", 0),
])
def test_compare_versions(v1, v2, expected):
    result = compare_versions(v1, v2)
    assert result == expected

def test_normalize_version_strips_v_prefix():
    assert normalize_version("v1.2.3") == "1.2.3"
    assert normalize_version("1.2.3") == "1.2.3"
```

## Running Tests

```bash
# 단위 테스트만 실행
pytest tests/unit/test_about_dialog.py tests/unit/test_update_checker.py tests/unit/test_version.py -v

# 통합 테스트 포함
pytest tests/ -m "not slow" -v

# 커버리지 확인
pytest tests/unit/ --cov=src/core/update_checker --cov=src/ui/about_dialog --cov=src/utils/version --cov-report=term-missing
```

## Manual Testing Checklist

### About 대화상자
- [ ] LocalTranslate 메뉴 → About LocalTranslate 클릭
- [ ] 앱 이름, 버전 정보 표시 확인
- [ ] 저작권 및 라이선스 정보 표시 확인
- [ ] GitHub 링크 클릭 → 브라우저에서 열리는지 확인
- [ ] ESC 또는 닫기 버튼으로 대화상자 닫히는지 확인

### Update Check
- [ ] Help 메뉴 → Check for Updates... 클릭
- [ ] 진행 표시(스피너/상태) 확인
- [ ] 최신 버전일 때 "최신 버전입니다" 메시지 확인
- [ ] (테스트용) 버전을 낮게 설정 후 업데이트 가능 메시지 확인
- [ ] 오프라인 상태에서 오류 메시지 확인
- [ ] 다운로드 링크 클릭 → GitHub 릴리스 페이지 열리는지 확인

## Key Files

| File | Purpose |
|------|---------|
| `src/core/config.py` | AppConfig에 새 필드 추가 |
| `src/core/update_checker.py` | GitHub API 연동 및 버전 확인 |
| `src/ui/about_dialog.py` | About 대화상자 UI |
| `src/ui/update_dialog.py` | 업데이트 결과 대화상자 UI |
| `src/ui/main_window.py` | 메뉴 항목 추가 |
| `src/utils/version.py` | 버전 비교 유틸리티 |

## Common Issues

### 1. GitHub API Rate Limit
```
오류: 403 Forbidden - API rate limit exceeded
해결: 1시간 후 재시도하거나, GitHub 토큰 설정 (향후 기능)
```

### 2. SSL Certificate Error (macOS)
```
오류: SSL: CERTIFICATE_VERIFY_FAILED
해결: Python 설치 디렉토리의 Install Certificates.command 실행
```

### 3. Qt Plugin Not Found
```
오류: qt.qpa.plugin: Could not find the Qt platform plugin
해결: QT_QPA_PLATFORM_PLUGIN_PATH 환경변수 설정
```
