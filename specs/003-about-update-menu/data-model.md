# Data Model: About 및 Update Check 메뉴

**Feature Branch**: `003-about-update-menu`
**Date**: 2025-12-27

## Entities

### 1. AppInfo (Dataclass)

앱 메타데이터를 담는 불변 데이터 클래스.

**Location**: `src/core/config.py` (기존 AppConfig 확장)

**Attributes**:

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `name` | `str` | 앱 이름 | 기존 `config.app_name` |
| `version` | `str` | 현재 버전 (예: "0.1.2") | 기존 `config.version` |
| `copyright_year` | `str` | 저작권 연도 (예: "2024-2025") | 새로 추가 |
| `license` | `str` | 라이선스 유형 (예: "MIT") | 새로 추가 |
| `github_url` | `str` | GitHub 리포지토리 URL | 새로 추가 |
| `organization` | `str` | 개발 조직명 | 기존 `config.organization` |

**Validation Rules**:
- `version`: Semantic versioning 형식 (MAJOR.MINOR.PATCH)
- `github_url`: 유효한 URL 형식

---

### 2. ReleaseInfo (Dataclass)

GitHub Release 응답에서 추출한 릴리스 정보.

**Location**: `src/core/update_checker.py`

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `version` | `str` | 릴리스 버전 (태그에서 v 접두사 제거) |
| `tag_name` | `str` | 원본 태그 (예: "v1.0.0") |
| `html_url` | `str` | 릴리스 페이지 URL |
| `is_prerelease` | `bool` | 프리릴리스 여부 |
| `published_at` | `str` | 릴리스 일시 (ISO 8601) |

**Factory Method**:
```python
@classmethod
def from_github_response(cls, data: dict) -> "ReleaseInfo":
    """GitHub API 응답에서 ReleaseInfo 생성."""
```

---

### 3. UpdateStatus (Enum)

업데이트 확인 상태를 나타내는 열거형.

**Location**: `src/core/update_checker.py`

**Values**:

| Value | Description |
|-------|-------------|
| `CHECKING` | 확인 중 |
| `UP_TO_DATE` | 최신 버전 |
| `UPDATE_AVAILABLE` | 업데이트 가능 |
| `ERROR` | 오류 발생 |
| `RATE_LIMITED` | API 제한 초과 |

---

### 4. UpdateCheckResult (Dataclass)

업데이트 확인 결과를 담는 데이터 클래스.

**Location**: `src/core/update_checker.py`

**Attributes**:

| Field | Type | Description |
|-------|------|-------------|
| `status` | `UpdateStatus` | 확인 결과 상태 |
| `current_version` | `str` | 현재 앱 버전 |
| `latest_release` | `ReleaseInfo | None` | 최신 릴리스 정보 (있는 경우) |
| `error_message` | `str | None` | 오류 메시지 (있는 경우) |

**Derived Properties**:
```python
@property
def is_update_available(self) -> bool:
    """업데이트 가능 여부."""
    return self.status == UpdateStatus.UPDATE_AVAILABLE

@property
def download_url(self) -> str | None:
    """다운로드 페이지 URL."""
    return self.latest_release.html_url if self.latest_release else None
```

---

## Relationships

```
AppConfig (기존)
    └── 확장: copyright_year, license, github_url 추가

UpdateChecker
    ├── uses → AppConfig (현재 버전 조회)
    ├── produces → ReleaseInfo (API 응답 파싱)
    └── produces → UpdateCheckResult (최종 결과)

AboutDialog
    └── reads → AppConfig (앱 정보 표시)

UpdateDialog
    └── reads → UpdateCheckResult (결과 표시)
```

---

## State Transitions

### UpdateStatus 상태 전이

```
[시작] → CHECKING
           ↓
    ┌──────┴──────┬───────────┬──────────────┐
    ↓             ↓           ↓              ↓
UP_TO_DATE   UPDATE_AVAILABLE   ERROR    RATE_LIMITED
```

**전이 조건**:
- `CHECKING → UP_TO_DATE`: 최신 버전 == 현재 버전
- `CHECKING → UPDATE_AVAILABLE`: 최신 버전 > 현재 버전
- `CHECKING → ERROR`: 네트워크 오류, 파싱 오류 등
- `CHECKING → RATE_LIMITED`: GitHub API 속도 제한 초과

---

## Config Changes

### AppConfig 확장 (src/core/config.py)

```python
@dataclass(frozen=True)
class AppConfig:
    # 기존 필드
    app_name: str = "LocalTranslate"
    organization: str = "LocalTranslate"
    version: str = "0.1.2"
    # ...

    # 새로 추가할 필드
    copyright_year: str = "2024-2025"
    license: str = "MIT"
    github_url: str = "https://github.com/jeongsk/local-translate"
    github_api_url: str = "https://api.github.com/repos/jeongsk/local-translate"
```
