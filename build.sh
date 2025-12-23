#!/bin/bash

# LocalTranslate 빌드 스크립트
# macOS용 실행 파일 (.app) 생성

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}LocalTranslate 빌드 시작${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# 프로젝트 루트 디렉토리로 이동
cd "$(dirname "$0")"

# 1. 가상환경 활성화
echo -e "${YELLOW}[1/5] 가상환경 활성화...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${RED}오류: .venv 디렉토리를 찾을 수 없습니다.${NC}"
    exit 1
fi
source .venv/bin/activate
echo -e "${GREEN}✓ 가상환경 활성화 완료${NC}"
echo ""

# 2. PyInstaller 설치 확인
echo -e "${YELLOW}[2/5] PyInstaller 확인...${NC}"
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo -e "${YELLOW}PyInstaller를 설치합니다...${NC}"
    pip install pyinstaller
fi
echo -e "${GREEN}✓ PyInstaller 준비 완료${NC}"
echo ""

# 3. 기존 빌드 정리
echo -e "${YELLOW}[3/5] 기존 빌드 파일 정리...${NC}"
if [ -d "build" ]; then
    rm -rf build
    echo "  - build 디렉토리 삭제"
fi
if [ -d "dist" ]; then
    rm -rf dist
    echo "  - dist 디렉토리 삭제"
fi
echo -e "${GREEN}✓ 정리 완료${NC}"
echo ""

# 4. PyInstaller로 빌드
echo -e "${YELLOW}[4/5] 애플리케이션 빌드 중...${NC}"
echo -e "${YELLOW}이 작업은 몇 분 정도 걸릴 수 있습니다.${NC}"
echo ""

pyinstaller --clean --noconfirm LocalTranslate.spec

if [ $? -ne 0 ]; then
    echo -e "${RED}빌드 실패!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 빌드 완료${NC}"
echo ""

# 5. 결과 확인
echo -e "${YELLOW}[5/5] 빌드 결과 확인...${NC}"
if [ -d "dist/LocalTranslate.app" ]; then
    echo -e "${GREEN}✓ 애플리케이션이 성공적으로 생성되었습니다!${NC}"
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}빌드 완료!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "생성된 앱 위치: ${GREEN}$(pwd)/dist/LocalTranslate.app${NC}"
    echo ""
    echo "실행 방법:"
    echo "  1. Finder에서 dist 폴더를 열고 LocalTranslate.app을 더블클릭"
    echo "  2. 또는 터미널에서: open dist/LocalTranslate.app"
    echo ""

    # 앱 크기 표시
    APP_SIZE=$(du -sh "dist/LocalTranslate.app" | cut -f1)
    echo -e "앱 크기: ${YELLOW}${APP_SIZE}${NC}"
    echo ""

    # macOS 보안 경고 안내
    echo -e "${YELLOW}참고:${NC}"
    echo "처음 실행 시 macOS에서 보안 경고가 표시될 수 있습니다."
    echo "그럴 경우: 시스템 설정 > 개인정보 보호 및 보안에서 '확인 없이 열기'를 클릭하세요."
else
    echo -e "${RED}오류: 앱 생성에 실패했습니다.${NC}"
    exit 1
fi
