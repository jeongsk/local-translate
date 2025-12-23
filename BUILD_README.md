# LocalTranslate 빌드 가이드

이 문서는 LocalTranslate 애플리케이션을 실행 파일로 빌드하는 방법을 설명합니다.

## 📦 빌드 완료!

실행 파일이 성공적으로 생성되었습니다!

### 생성된 파일 위치
```
dist/LocalTranslate.app
```

### 앱 크기
약 596MB (PyTorch 및 번역 모델 포함)

## 🚀 실행 방법

### 방법 1: Finder에서 실행
1. Finder를 열고 프로젝트의 `dist` 폴더로 이동
2. `LocalTranslate.app`을 더블클릭

### 방법 2: 터미널에서 실행
```bash
open dist/LocalTranslate.app
```

## ⚠️ macOS 보안 경고

처음 실행 시 macOS에서 다음과 같은 보안 경고가 표시될 수 있습니다:

> "LocalTranslate.app은(는) 확인되지 않은 개발자가 배포했기 때문에 열 수 없습니다."

### 해결 방법

1. **시스템 설정** 열기
2. **개인정보 보호 및 보안** 선택
3. "보안" 섹션에서 **"확인 없이 열기"** 버튼 클릭
4. 다시 앱 실행

또는 터미널에서 다음 명령어로 실행:
```bash
xattr -cr dist/LocalTranslate.app
open dist/LocalTranslate.app
```

## 🔨 재빌드 방법

코드를 수정한 후 다시 빌드하려면:

```bash
./build.sh
```

이 스크립트는 자동으로:
- 기존 빌드 파일 정리
- PyInstaller로 새 앱 빌드
- 빌드 결과 확인

## 📝 빌드 구성

### 빌드 설정 파일
- `LocalTranslate.spec`: PyInstaller 빌드 설정 파일
- `build.sh`: 자동 빌드 스크립트

### 포함된 구성요소
- ✅ PySide6 (Qt GUI 프레임워크)
- ✅ PyTorch (딥러닝 프레임워크)
- ✅ Transformers (Hugging Face 모델)
- ✅ Lingua (언어 감지)
- ✅ 모든 의존성 라이브러리

### 제외된 구성요소 (빌드 크기 최적화)
- ❌ pytest (테스트 프레임워크)
- ❌ jupyter (노트북)
- ❌ matplotlib (플로팅 라이브러리)
- ❌ IPython (대화형 쉘)

## 🎯 배포하기

### 1. 앱 공유
빌드된 `LocalTranslate.app`을 다른 macOS 사용자에게 공유할 수 있습니다.

### 2. DMG 파일 생성 (선택사항)
더 전문적인 배포를 위해 DMG 파일을 생성할 수 있습니다:

```bash
# hdiutil을 사용한 DMG 생성
hdiutil create -volname "LocalTranslate" -srcfolder dist/LocalTranslate.app -ov -format UDZO LocalTranslate.dmg
```

### 3. 코드 서명 (선택사항)
App Store 배포나 Gatekeeper 경고를 피하려면 Apple Developer ID로 서명:

```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: YOUR_NAME" dist/LocalTranslate.app
```

## 💡 문제 해결

### 빌드 실패 시
1. 가상환경이 활성화되어 있는지 확인
2. 의존성이 모두 설치되어 있는지 확인:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### 앱 실행 시 오류 발생
1. 콘솔 앱을 열고 오류 로그 확인
2. 터미널에서 직접 실행하여 오류 메시지 확인:
   ```bash
   ./dist/LocalTranslate.app/Contents/MacOS/LocalTranslate
   ```

### 메모리 부족 오류
- 최소 8GB RAM 필요
- 최소 10GB 여유 저장공간 필요

## 📚 추가 정보

### 빌드 로그
빌드 과정에서 생성된 파일:
- `build/`: 중간 빌드 파일
- `dist/`: 최종 실행 파일
- `build/LocalTranslate/warn-LocalTranslate.txt`: 빌드 경고 로그

### 개발 모드
개발 중에는 빌드하지 않고 직접 실행하는 것이 빠릅니다:
```bash
source .venv/bin/activate
python -m src.main
```

## 🔄 업데이트

새 버전을 배포할 때:
1. `src/core/config.py`에서 버전 번호 업데이트
2. `LocalTranslate.spec`의 `CFBundleVersion` 업데이트
3. 재빌드: `./build.sh`

---

**빌드 날짜**: 2024년 12월 23일
**PyInstaller 버전**: 6.17.0
**Python 버전**: 3.12.11
**플랫폼**: macOS (Apple Silicon)
