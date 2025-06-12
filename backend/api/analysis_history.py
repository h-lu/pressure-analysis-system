"""
历史记录API路由
"""
from fastapi import APIRouter, HTTPException
import logging
from pathlib import Path

from ..core.config import settings
from ..services.r_analysis import RAnalysisEngine

logger = logging.getLogger(__name__)
router = APIRouter()

def get_r_engine():
    """获取R分析引擎实例（每次都创建新的实例以保证无状态）"""
    return RAnalysisEngine()

@router.get("/", summary="获取历史分析记录")
async def get_history():
    """获取所有分析历史记录的摘要列表"""
    try:
        engine = get_r_engine()
        history = engine.get_analysis_history()
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取历史记录失败")

@router.get("/stats", summary="获取历史记录统计信息")
async def get_history_stats():
    """获取历史记录统计信息"""
    try:
        engine = get_r_engine()
        history = engine.get_analysis_history()
        
        # 计算统计信息
        total_tasks = len(history)
        completed_tasks = len([h for h in history if h.get('status') == 'completed'])
        failed_tasks = len([h for h in history if h.get('status') == 'failed'])
        running_tasks = len([h for h in history if h.get('status') == 'running'])
        
        return {
            "success": True,
            "stats": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "running_tasks": running_tasks,
                "success_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            }
        }
    except Exception as e:
        logger.error(f"获取历史记录统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取历史记录统计失败")

# 清空所有历史记录的API已被移除
# 为了安全性考虑，不再支持一键清空所有历史记录功能

@router.delete("/batch", summary="批量删除分析记录")
async def batch_delete_analysis_records(task_ids: dict):
    """
    批量删除多个分析记录
    请求体格式: {"task_ids": ["task_id1", "task_id2", ...]}
    """
    try:
        task_id_list = task_ids.get('task_ids', [])
        if not task_id_list or not isinstance(task_id_list, list):
            raise HTTPException(status_code=400, detail="请求格式错误：需要task_ids数组")
        
        success_count = 0
        failed_items = []
        
        for task_id in task_id_list:
            try:
                # 删除历史记录文件
                history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
                if history_file.exists():
                    history_file.unlink()
                    
                    # 删除关联的分析目录
                    task_analysis_dir = Path(settings.CHARTS_DIR) / task_id
                    if task_analysis_dir.exists() and task_analysis_dir.is_dir():
                        import shutil
                        shutil.rmtree(task_analysis_dir)
                    
                    success_count += 1
                else:
                    failed_items.append({
                        "task_id": task_id,
                        "reason": "记录不存在"
                    })
                    
            except Exception as e:
                logger.error(f"删除分析记录 {task_id} 失败: {e}")
                failed_items.append({
                    "task_id": task_id,
                    "reason": str(e)
                })
        
        return {
            "success": True,
            "message": f"批量删除完成：成功 {success_count} 个，失败 {len(failed_items)} 个",
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"批量删除分析记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量删除分析记录失败: {e}")

@router.delete("/{task_id}", summary="删除分析记录")
async def delete_analysis_record(task_id: str):
    """
    删除指定的分析记录文件以及关联的分析结果目录
    """
    try:
        # 删除历史记录文件
        history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
        if not history_file.exists():
            raise HTTPException(status_code=404, detail="指定的分析记录不存在")
        
        history_file.unlink()
        
        # 删除关联的分析目录
        task_analysis_dir = Path(settings.CHARTS_DIR) / task_id
        if task_analysis_dir.exists() and task_analysis_dir.is_dir():
            import shutil
            shutil.rmtree(task_analysis_dir)
            
        return {
            "success": True,
            "message": "分析记录已成功删除"
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"删除分析记录 {task_id} 失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除分析记录失败: {e}")

@router.put("/{task_id}/name", summary="更新分析记录名称")
async def update_analysis_record_name(task_id: str, name_data: dict):
    """
    更新指定分析记录的显示名称
    """
    try:
        new_name = name_data.get('name')
        if not new_name:
            raise HTTPException(status_code=400, detail="缺少新名称 (name)")
            
        history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
        if not history_file.exists():
            raise HTTPException(status_code=404, detail="指定的分析记录不存在")
        
        import json
        record = json.loads(history_file.read_text(encoding='utf-8'))
        record['name'] = new_name
        # 更新修改时间
        from datetime import datetime
        import pytz
        record['modified_at'] = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        
        history_file.write_text(json.dumps(record, ensure_ascii=False, indent=4), encoding='utf-8')
        
        return {
            "success": True,
            "message": "分析记录名称更新成功",
            "updated_record": record
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"更新分析记录名称 {task_id} 失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新分析记录名称失败: {e}") 