"""
压力采集数据分析系统 - 后端API服务
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os
from pathlib import Path

# 改为绝对导入
from backend.core.config import settings, ensure_directories
from backend.api import files, analysis, deepseek_analysis

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="基于FastAPI和R的压力数据分析系统",
    debug=settings.DEBUG
)

# 应用启动时确保目录存在
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    try:
        # 确保所有目录存在
        ensure_directories()
        logger.info("所有必要目录已创建")
        
        # 检查目录权限
        for directory in [settings.UPLOAD_DIR, settings.CHARTS_DIR, settings.REPORTS_DIR]:
            if not os.access(directory, os.W_OK):
                logger.warning(f"目录 {directory} 可能没有写入权限")
        
        logger.info(f"{settings.PROJECT_NAME} 启动完成")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# 挂载静态文件目录
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 注册API路由
app.include_router(files.router, prefix="/api", tags=["文件管理"])
app.include_router(analysis.router, prefix="/api", tags=["数据分析"])
app.include_router(deepseek_analysis.router, prefix="/api/deepseek", tags=["AI分析报告"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系系统管理员"
        }
    )

# 挂载前端静态文件
# 注意：这应该在所有API路由和特定静态目录挂载之后
# 这会将所有不匹配上面任何路由的请求都指向前端应用，由Vue Router处理
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if not frontend_path.exists():
    logger.warning("Frontend build directory 'frontend/dist' not found. SPA routing will not work.")
else:
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# 如果直接运行此文件（已弃用，请使用根目录的run_server.py）
if __name__ == "__main__":
    import sys
    print("警告: 请使用项目根目录的 run_server.py 来启动服务")
    print("python run_server.py")
    sys.exit(1) 