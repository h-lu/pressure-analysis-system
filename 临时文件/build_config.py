#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力分析系统打包配置文件
"""

import os
import sys
from pathlib import Path

# 项目基本信息
PROJECT_NAME = "压力分析系统"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "压力采集数据分析系统"

# 路径配置
BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"
BUILD_DIR = BASE_DIR / "build"
DIST_DIR = BASE_DIR / "dist"

# 打包配置
EXECUTABLE_NAME = "pressure_analysis_system"
ICON_PATH = None  # 可以设置应用图标路径

# 需要包含的数据文件
DATA_FILES = [
    (str(BACKEND_DIR / "r_analysis"), "r_analysis"),
    (str(BACKEND_DIR / "static"), "static"),
    (str(FRONTEND_DIR / "dist"), "frontend_dist"),
]

# 需要包含的二进制文件
BINARIES = []

# 隐藏导入（PyInstaller可能无法自动检测的模块）
HIDDEN_IMPORTS = [
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'fastapi',
    'fastapi.staticfiles',
    'starlette',
    'starlette.middleware',
    'starlette.middleware.cors',
    'pydantic',
    'pandas',
    'numpy',
    'rpy2',
    'rpy2.robjects',
    'rpy2.robjects.packages',
    'PIL',
    'jinja2',
    'aiofiles',
    'multipart',
]

# 排除的模块
EXCLUDES = [
    'pytest',
    'pytest-asyncio',
    'httpx',
    'test',
    'tests',
    'unittest',
]

# PyInstaller 选项
PYINSTALLER_OPTIONS = {
    'name': EXECUTABLE_NAME,
    'onefile': True,
    'windowed': False,  # 设置为True可以隐藏控制台窗口
    'icon': ICON_PATH,
    'add_data': DATA_FILES,
    'add_binary': BINARIES,
    'hidden_import': HIDDEN_IMPORTS,
    'exclude_module': EXCLUDES,
    'clean': True,
    'noconfirm': True,
} 