"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    PROJECT_NAME: str = "压力采集数据分析系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Vue.js开发服务器
        "http://localhost:3001",  # Vue.js开发服务器备用端口
        "http://localhost:3002",  # Vue.js开发服务器端口3002
        "http://localhost:5173",  # Vite开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
        "http://localhost:8000",  # Docker生产环境
        "http://127.0.0.1:8000",  # Docker生产环境
        "*"  # 生产环境允许所有源(Docker容器中)
    ]
    
    # 基础路径
    BASE_DIR: str = str(Path(__file__).parent.parent.parent)
    
    # R环境配置 - 请根据您的R安装路径修改
    # 通常在macOS上是 /usr/local/bin/R, 在Windows上可能是 C:\\Program Files\\R\\R-4.x.x\\bin\\x64
    R_HOME: str = "/usr/local/bin"
    
    # 文件上传和处理目录 - 统一存放在 backend/output 目录下
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "backend", "uploads")
    CHARTS_DIR: str = os.path.join(BASE_DIR, "backend", "output", "charts")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "backend", "output", "reports")
    HISTORY_DIR: str = os.path.join(BASE_DIR, "backend", "output", "history")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".csv"]
    
    # 静态文件配置
    STATIC_DIR: str = "backend/static"
    
    # R分析配置
    R_SCRIPT_PATH: str = "backend/r_analysis/pressure_analysis.R"
    R_WORKING_DIR: str = "backend/r_analysis"
    
    # 分析参数默认值
    DEFAULT_TARGET_FORCES: List[float] = [5.0, 25.0, 50.0]
    DEFAULT_TOLERANCE_ABS: List[float] = [0.5, 1.0, 2.0]
    DEFAULT_TOLERANCE_PCT: List[float] = [5.0, 4.0, 3.0]
    
    # 任务管理
    TASK_TIMEOUT: int = 300  # 5分钟
    CLEANUP_INTERVAL: int = 3600  # 1小时清理一次临时文件
    
    API_V1_STR: str = "/api/v1"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 数据库配置 (如果使用)
    # DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        # 移除 env_file 的设置, 让 pydantic 直接从环境变量中读取
        # env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()

# 确保必要的目录存在
def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        settings.UPLOAD_DIR,
        settings.STATIC_DIR,
        settings.CHARTS_DIR,
        settings.REPORTS_DIR,
        settings.HISTORY_DIR,
        settings.R_WORKING_DIR
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# 应用启动时创建目录
ensure_directories() 