#!/usr/bin/env python3
"""
压力采集数据分析系统 - 服务器启动脚本
在项目根目录运行此脚本以启动后端服务
"""
import uvicorn
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入应用
from backend.main import app
from backend.core.config import settings

if __name__ == "__main__":
    print(f"启动 {settings.PROJECT_NAME}")
    print(f"访问地址: http://{settings.HOST}:{settings.PORT}")
    print(f"API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print("按 Ctrl+C 停止服务")
    
    # 确保在项目根目录运行
    os.chdir(project_root)
    
    # 启动服务
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[str(project_root / "backend")]
    ) 