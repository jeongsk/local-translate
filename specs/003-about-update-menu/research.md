# Research: About 및 Update Check 메뉴

**Feature Branch**: `003-about-update-menu`
**Date**: 2025-12-27

## 1. GitHub Releases API for Update Check

### Decision
GitHub Releases API의 `/releases/latest` 엔드포인트를 사용하여 최신 버전을 확인한다.

### Rationale
- 공개 리포지토리의 경우 인증 없이 사용 가능
- `/releases/latest`는 단일 API 호출로 최신 릴리스 정보를 반환
- 응답에 필요한 모든 필드(`tag_name`, `html_url`)가 포함됨

### Key Details

**API Endpoint**:
```
GET https://api.github.com/repos/jeongsk/local-translate/releases/latest
```

**필요한 응답 필드**:
- `tag_name`: 버전 태그 (예: "v1.0.0")
- `html_url`: 릴리스 페이지 URL
- `prerelease`: 프리릴리스 여부 (제외 처리)
- `draft`: 드래프트 여부 (제외 처리)

**Rate Limiting**:
- 비인증 요청: 60 requests/hour/IP
- 헤더 확인: `x-ratelimit-remaining`, `x-ratelimit-reset`

**Timeout 설정**:
- Connection timeout: 5초
- Read timeout: 10초
- Total timeout: 15초 (SC-004 요구사항 충족)

### Alternatives Considered
1. **GraphQL API**: 더 유연하지만 인증 필요 - 불필요한 복잡성
2. **자체 업데이트 서버**: 관리 오버헤드 발생 - 과도한 설계
3. **모든 릴리스 조회 후 필터링**: 불필요한 데이터 전송 - 비효율적

---

## 2. PySide6 About 대화상자

### Decision
`QDialog`를 사용한 커스텀 About 대화상자를 구현한다.

### Rationale
- 클릭 가능한 GitHub 링크 필요
- 앱 아이콘 표시 필요
- 라이선스 정보 등 다양한 정보 레이아웃 필요

### Key Details

**링크 처리**:
```python
label = QLabel()
label.setText('<a href="https://github.com/jeongsk/local-translate">GitHub</a>')
label.setOpenExternalLinks(True)  # 외부 브라우저에서 링크 열기
```

**앱 아이콘 표시**:
```python
from PySide6.QtGui import QPixmap
icon_label = QLabel()
pixmap = QPixmap("path/to/icon.png").scaledToWidth(128)
icon_label.setPixmap(pixmap)
```

**macOS 메뉴 통합**:
```python
about_action = QAction("About LocalTranslate", self)
about_action.setMenuRole(QAction.MenuRole.AboutRole)  # macOS 앱 메뉴에 자동 배치
```

### Alternatives Considered
1. **QMessageBox.about()**: 클릭 가능한 링크 지원이 제한적 - 기능 부족
2. **QWebEngineView**: HTML 페이지 렌더링 - 과도한 의존성

---

## 3. 버전 비교

### Decision
`packaging.version` 라이브러리를 사용하여 버전 비교를 수행한다.

### Rationale
- pip의 의존성으로 이미 설치되어 있음
- PEP 440 표준 버전 형식 지원
- 프리릴리스, 포스트릴리스 등 다양한 버전 형식 처리

### Key Details

**버전 비교 패턴**:
```python
from packaging.version import Version

def normalize_version(version_str: str) -> Version:
    """v 접두사 제거 후 Version 객체 반환."""
    return Version(version_str.lstrip('v'))

current = normalize_version("v0.1.2")
latest = normalize_version("v1.0.0")

if latest > current:
    print("업데이트 가능")
```

**v-prefix 처리**:
- GitHub 태그는 보통 `v1.0.0` 형식
- `packaging.version`은 `v` 접두사를 직접 지원하지 않음
- `lstrip('v')`로 정규화 필요

### Alternatives Considered
1. **semver 라이브러리**: 별도 설치 필요 - 불필요한 의존성 추가
2. **수동 문자열 파싱**: 엣지 케이스 처리 어려움 - 버그 가능성
3. **단순 문자열 비교**: "1.10.0" > "1.9.0" 잘못 처리 - 부정확

---

## 4. HTTP 클라이언트

### Decision
Python 표준 라이브러리 `urllib.request`를 사용한다.

### Rationale
- requests 라이브러리는 현재 의존성에 없음
- 단순한 GET 요청 하나만 필요
- 추가 의존성 최소화

### Key Details

**구현 패턴**:
```python
import urllib.request
import json
from urllib.error import URLError, HTTPError

def fetch_latest_release(timeout: int = 15) -> dict:
    url = "https://api.github.com/repos/jeongsk/local-translate/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "LocalTranslate"})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        if e.code == 404:
            raise NoReleasesError("No releases found")
        raise
    except URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
```

### Alternatives Considered
1. **requests**: 더 편리하지만 새 의존성 추가 필요 - 과도한 설계
2. **aiohttp**: 비동기지만 Qt 이벤트 루프와 통합 복잡 - 불필요

---

## Summary

| 영역 | 결정 | 이유 |
|------|------|------|
| API | GitHub Releases `/latest` | 단순, 인증 불필요 |
| About UI | Custom QDialog | 링크, 아이콘 지원 |
| 버전 비교 | packaging.version | 이미 설치됨, 표준 |
| HTTP | urllib.request | 의존성 없음 |
