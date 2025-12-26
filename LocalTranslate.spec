# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LocalTranslate
macOS 실행 파일 빌드 설정
"""

import sys
from pathlib import Path

block_cipher = None

# 프로젝트 루트 경로
project_root = Path.cwd()

# 소스 파일 경로
src_path = project_root / 'src'

# 숨겨진 imports (PyInstaller가 자동으로 찾지 못하는 모듈들)
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'torch',
    'transformers',
    'accelerate',
    'optimum.quanto',
    'lingua',
    # PyTorch 관련 필수 모듈
    'torch.nn',
    'torch.nn.functional',
    'torch.utils',
    'torch.utils.data',
    # Transformers 관련
    'transformers.models',
    'transformers.models.auto',
    'transformers.models.auto.modeling_auto',
    'transformers.models.auto.tokenization_auto',
    # 기타 필수 모듈
    'dataclasses',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
]

# 데이터 파일 (리소스 등)
datas = []

# src 디렉토리의 Python 모듈들 포함
datas.append((str(src_path), 'src'))

# resources 디렉토리가 있으면 포함
resources_path = project_root / 'resources'
if resources_path.exists():
    datas.append((str(resources_path), 'resources'))

# binaries (필요한 경우 추가 라이브러리)
binaries = []

# 분석 단계
a = Analysis(
    [str(src_path / 'main.py')],
    pathex=[str(project_root), str(src_path)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 불필요한 모듈 제외 (빌드 크기 감소)
        'matplotlib',
        'numpy.distutils',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ (Python 라이브러리 아카이브)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE (실행 파일)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalTranslate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 앱이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT (모든 파일 수집)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LocalTranslate',
)

# macOS 앱 번들 생성
app = BUNDLE(
    coll,
    name='LocalTranslate.app',
    icon=None,  # 아이콘 파일이 있으면 경로 지정
    bundle_identifier='com.localtranslate.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleName': 'LocalTranslate',
        'CFBundleDisplayName': 'LocalTranslate',
        'CFBundleGetInfoString': 'Local translation application',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 LocalTranslate Contributors',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': 'True',
    },
)
