"""
文件管理API
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/files")
async def list_files():
    """获取文件列表"""
    return {"message": "文件管理API", "files": []}

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "module": "files"}