"""
分析API路由
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any
import asyncio
import uuid
import os
import json
import logging
from datetime import datetime
import pytz
from pathlib import Path

# 设置时区为上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')
from ..core.config import settings
import shutil

from ..models.schemas import (
    AnalysisParams, TaskCreateResponse, TaskStatusResponse, 
    AnalysisResultResponse, TaskInfo, TaskStatus
)
from ..services.r_analysis import RAnalysisEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# 任务存储 (生产环境应使用Redis或数据库)
tasks: Dict[str, TaskInfo] = {}
results: Dict[str, Dict[str, Any]] = {}

# R分析引擎实例 - 修改为函数式调用，不再使用全局单例
# r_engine = None 

def get_r_engine():
    """获取R分析引擎实例（每次都创建新的实例以保证无状态）"""
    # global r_engine
    # if r_engine is None:
    #     r_engine = RAnalysisEngine()
    # return r_engine
    return RAnalysisEngine()

async def run_analysis_task(task_id: str, csv_path: str, params: AnalysisParams):
    """后台分析任务"""
    try:
        # 更新任务状态
        tasks[task_id].status = TaskStatus.RUNNING
        tasks[task_id].started_at = datetime.now(SHANGHAI_TZ)
        tasks[task_id].progress = 10
        tasks[task_id].message = "正在初始化分析..."
        
        # 获取R引擎
        engine = get_r_engine()
        
        # 更新进度
        tasks[task_id].progress = 30
        tasks[task_id].message = "正在执行数据分析..."
        
        # 执行分析
        result = engine.analyze_data(csv_path, params, task_id)
        
        # 更新进度
        tasks[task_id].progress = 90
        tasks[task_id].message = "正在生成报告..."
        
        # 保存结果
        results[task_id] = result
        
        # 完成任务
        tasks[task_id].status = TaskStatus.COMPLETED
        tasks[task_id].completed_at = datetime.now(SHANGHAI_TZ)
        tasks[task_id].progress = 100
        tasks[task_id].message = "分析完成"
        
    except Exception as e:
        # 任务失败
        tasks[task_id].status = TaskStatus.FAILED
        tasks[task_id].error = str(e)
        tasks[task_id].message = f"分析失败: {str(e)}"

@router.post("/analyze", response_model=TaskCreateResponse)
async def start_analysis(
    params: AnalysisParams,
    background_tasks: BackgroundTasks
):
    """
    启动数据分析任务
    """
    try:
        # 检查file_id参数
        if not params.file_id:
            raise HTTPException(status_code=400, detail="缺少file_id参数")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务信息
        task_info = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，等待执行..."
        )
        
        # 保存任务
        tasks[task_id] = task_info
        
        # 构建文件路径 - 使用绝对路径，避免重复.csv后缀
        # 确保file_id不重复包含.csv后缀
        file_id = params.file_id
        if file_id.endswith('.csv'):
            file_id = file_id[:-4]  # 移除.csv后缀
        
        # 构建绝对路径
        uploads_dir = Path(settings.UPLOAD_DIR)
        csv_path = str(uploads_dir / f"{file_id}.csv")
        
        # 添加后台任务
        background_tasks.add_task(run_analysis_task, task_id, csv_path, params)
        
        return TaskCreateResponse(
            success=True,
            message="分析任务已启动",
            task_id=task_id,
            estimated_duration=120  # 预估2分钟
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动分析任务失败: {str(e)}")

@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态 - 支持从活动任务和历史记录中获取
    """
    # 首先检查活动任务
    if task_id in tasks:
        task_info = tasks[task_id]
        
        # 如果是已完成的任务，尝试从历史记录中补充信息
        if task_info.status == TaskStatus.COMPLETED:
            try:
                history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
                if history_file.exists():
                    with open(history_file, 'r', encoding='utf-8') as f:
                        record = json.load(f)
                    
                    # 补充任务信息
                    task_dict = task_info.dict()
                    task_dict.update({
                        "filename": record.get('original_filename', 'demo_data.csv'),
                        "name": record.get('name', f"分析报告_{task_id[:8]}"),
                        "success_rate": record.get('successRate', 0)
                    })
                    
                    # 返回补充了额外信息的任务数据
                    return {
                        "success": True,
                        "message": "获取任务状态成功",
                        "task": task_dict
                    }
            except Exception as e:
                logger.error(f"补充任务信息失败: {e}")
        
        return TaskStatusResponse(
            success=True,
            message="获取任务状态成功",
            task=task_info
        )
    
    logger.info(f"活动任务中未找到 {task_id}，尝试从历史记录获取...")
    
    # 如果活动任务中没有，尝试从历史记录中获取
    try:
        history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
        logger.info(f"检查历史记录文件: {history_file}")
        if history_file.exists():
            logger.info(f"历史记录文件存在，读取数据...")
            with open(history_file, 'r', encoding='utf-8') as f:
                record = json.load(f)
            logger.info(f"历史记录内容: {record}")
            
            # 构建任务信息（兼容TaskInfo格式）
            from datetime import datetime
            
            # 安全地解析时间字符串
            def safe_parse_datetime(date_str):
                if not date_str:
                    return datetime.now(SHANGHAI_TZ)
                try:
                    # 尝试解析包含时区的时间
                    if '+' in date_str or 'T' in date_str:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        return datetime.fromisoformat(date_str)
                except:
                    return datetime.now(SHANGHAI_TZ)
            
            created_time = safe_parse_datetime(record.get('created_at', record.get('date', '')))
            completed_time = safe_parse_datetime(record.get('date', ''))
            
            task_info = TaskInfo(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                created_at=created_time,
                started_at=created_time,
                completed_at=completed_time,
                progress=100,
                message="分析完成",
                error=None
            )
            
            # 为兼容性，手动构建响应（不使用TaskStatusResponse）
            response_data = {
                "task_id": task_id,
                "status": "completed",
                "created_at": created_time.isoformat(),
                "started_at": created_time.isoformat(),
                "completed_at": completed_time.isoformat(),
                "progress": 100,
                "message": "分析完成",
                "error": None,
                "filename": record.get('original_filename', 'demo_data.csv'),
                "name": record.get('name', f"分析报告_{task_id[:8]}"),
                "success_rate": record.get('successRate', 0)
            }
            
            return {
                "success": True,
                "message": "获取任务状态成功",
                "task": response_data
            }
    except Exception as e:
        logger.error(f"从历史记录获取任务状态失败: {e}")
    
    # 任务不存在
    raise HTTPException(status_code=404, detail="任务不存在")

@router.get("/results/{task_id}")
async def get_analysis_results(task_id: str):
    """
    获取分析结果 - 从文件系统读取实际结果
    """
    try:
        # 首先检查历史记录中是否存在这个任务
        history_file = Path(settings.HISTORY_DIR) / f"{task_id}.json"
        logger.info(f"检查历史记录文件: {history_file}")
        logger.info(f"文件是否存在: {history_file.exists()}")
        if not history_file.exists():
            raise HTTPException(status_code=404, detail=f"任务不存在: {history_file}")
        
        # 检查分析结果文件是否存在
        results_file = Path(settings.CHARTS_DIR) / task_id / "analysis_results.json"
        if not results_file.exists():
            raise HTTPException(status_code=404, detail="分析结果文件不存在")
        
        # 读取分析结果
        with open(results_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 读取历史记录获取任务基本信息
        with open(history_file, 'r', encoding='utf-8') as f:
            task_record = json.load(f)
        
        # 构建完整的分析结果响应
        result = {
            "task_id": task_id,
            "status": "completed",
            "progress": 100,
            "filename": task_record.get('original_filename', 'demo_data.csv'),
            "data_summary": analysis_data.get('data_summary', []),
            "analysis_results": analysis_data,
            "chart_names": [
                # 基础分析图表 (8个)
                'force_time_series', 'force_histogram', 'force_boxplot',
                'deviation_analysis', 'percentage_deviation', 'correlation_matrix',
                
                # 控制图 (7个)  
                'shewhart_control', 'moving_average', 'xbar_r_chart',
                'cusum_chart', 'ewma_chart', 'imr_chart', 'run_chart',
                
                # 专业质量分析 (12个)
                'process_capability', 'pareto_analysis', 'residual_analysis',
                'qq_plot', 'radar_chart', 'position_heatmap',
                'success_rate_trend', 'capability_histogram', 'quality_dashboard',
                'waterfall_chart', 'spatial_clustering', 'parallel_coordinates',
                
                # 多维分析 (8个)
                'xy_heatmap', 'projection_combined', 'position_performance_comparison',
                'spatial_correlation_matrix', 'error_distribution_analysis', 'robot_consistency_analysis',
                'error_spatial_distribution', 'error_qq_plot'
            ]
        }
        
        return {
            "success": True,
            "message": "获取分析结果成功",
            "result": result
        }
        
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e}")
        raise HTTPException(status_code=404, detail="分析结果文件不存在")
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise HTTPException(status_code=500, detail="分析结果文件格式错误")
    except Exception as e:
        logger.error(f"获取分析结果失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取分析结果失败: {str(e)}")

@router.get("/tasks")
async def list_tasks():
    """
    列出所有任务 - 从历史记录中获取
    """
    logger.info("开始获取任务列表...")
    
    try:
        # 直接从历史记录目录读取
        history_dir = Path(settings.HISTORY_DIR)
        logger.info(f"历史记录目录: {history_dir}")
        logger.info(f"目录是否存在: {history_dir.exists()}")
        
        if not history_dir.exists():
            logger.warning(f"历史记录目录不存在: {history_dir}")
            return {"success": True, "message": "暂无任务记录", "tasks": []}
        
        # 列出所有json文件
        json_files = list(history_dir.glob("*.json"))
        logger.info(f"找到 {len(json_files)} 个历史记录文件: {[f.name for f in json_files]}")
        
        if not json_files:
            return {"success": True, "message": "暂无任务记录", "tasks": []}
        
        tasks_list = []
        
        for json_file in json_files:
            try:
                logger.info(f"处理文件: {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                
                logger.info(f"文件内容: {record}")
                
                task_id = record.get('id')
                if not task_id:
                    logger.warning(f"记录缺少ID: {record}")
                    continue
                
                # 构建任务信息
                task_info = {
                    "task_id": task_id,
                    "status": "completed",
                    "progress": 100,
                    "message": "分析完成",
                    "filename": record.get('original_filename', 'demo_data.csv'),
                    "data_points": 0,
                    "start_time": record.get('date', ''),
                    "created_at": record.get('created_at', record.get('date', '')),
                    "completed_at": record.get('date', ''),
                                         "success_rate": record.get('successRate', 0),
                    "error": None,
                    "name": record.get('name', f"分析报告_{task_id[:8]}")
                }
                
                logger.info(f"构建的任务信息: {task_info}")
                tasks_list.append(task_info)
                
            except Exception as e:
                logger.error(f"处理文件 {json_file} 失败: {e}", exc_info=True)
                continue
        
        logger.info(f"最终任务列表长度: {len(tasks_list)}")
        
        # 按创建时间排序
        tasks_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {
            "success": True,
            "message": f"成功获取 {len(tasks_list)} 个任务",
            "tasks": tasks_list
        }
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}", exc_info=True)
        return {"success": False, "message": f"获取任务列表失败: {str(e)}", "tasks": []}

@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 删除任务和结果
    del tasks[task_id]
    if task_id in results:
        del results[task_id]
    
    return {
        "success": True,
        "message": "任务删除成功"
    }

@router.get("/download-report/{task_id}")
async def download_report(task_id: str):
    """下载Word格式分析报告，如果不存在DeepSeek分析则自动生成"""
    try:
        # 检查任务ID格式
        if not task_id or task_id == "undefined":
            raise HTTPException(status_code=400, detail="无效的任务ID")
        
        # 获取R分析引擎
        engine = get_r_engine()
        
        # 检查分析结果是否存在
        results_file = Path(settings.CHARTS_DIR) / task_id / "analysis_results.json"
        if not results_file.exists():
            raise HTTPException(status_code=404, detail="分析结果不存在，请先完成数据分析")
        
        # 检查DeepSeek分析是否存在，如果不存在则自动生成
        deepseek_file = Path(settings.CHARTS_DIR) / task_id / "deepseek_analysis.json"
        if not deepseek_file.exists():
            logger.info(f"DeepSeek分析不存在，正在为任务 {task_id} 自动生成...")
            try:
                from .deepseek_analysis import generate_analysis_report
                from ..api.deepseek_analysis import AnalysisReportRequest
                
                # 读取R分析结果
                with open(results_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                
                # 创建DeepSeek分析请求
                request = AnalysisReportRequest(
                    analysis_data=analysis_data,
                    report_type="comprehensive"
                )
                
                # 生成DeepSeek分析报告
                await generate_analysis_report(request)
                logger.info(f"自动生成DeepSeek分析完成: {task_id}")
                
            except Exception as e:
                logger.warning(f"自动生成DeepSeek分析失败: {str(e)}，将生成不包含AI分析的报告")
        
        # 强制重新生成Word报告，确保是最新的（包含DeepSeek分析如果存在）
        report_path = engine.generate_comprehensive_word_report(
            task_id=task_id, 
            analysis_data=json.loads(results_file.read_text(encoding='utf-8')),
            deepseek_report=json.loads(deepseek_file.read_text(encoding='utf-8')).get('report', '') if deepseek_file.exists() else ''
        )
        
        if not report_path or not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="Word报告生成失败")
        
        # 验证文件大小，确保报告正确生成
        file_size = os.path.getsize(report_path)
        if file_size < 10000:  # 如果文件小于10KB，可能生成有问题
            logger.warning(f"生成的Word报告文件可能过小: {file_size} 字节")
        
        # 生成下载文件名 - 使用英文避免编码问题
        current_time = datetime.now(SHANGHAI_TZ).strftime("%Y%m%d_%H%M%S")
        download_filename = f"pressure_analysis_report_{current_time}.docx"
        
        # 使用URL编码的中文文件名
        import urllib.parse
        chinese_filename = f"压力系统分析报告_{current_time}.docx"
        encoded_filename = urllib.parse.quote(chinese_filename.encode('utf-8'))
        
        return FileResponse(
            path=report_path,
            filename=download_filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}; filename*=UTF-8''{encoded_filename}",
                "Content-Length": str(file_size)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")

@router.get("/download-comprehensive-report/{task_id}")
async def download_comprehensive_report(task_id: str):
    """
    下载包含R分析和DeepSeek分析的综合Word报告
    """
    try:
        # 检查分析结果文件是否存在
        results_file = Path(settings.CHARTS_DIR) / task_id / "analysis_results.json"
        if not results_file.exists():
            raise HTTPException(status_code=404, detail="分析结果不存在")
        
        # 读取分析结果
        with open(results_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 读取DeepSeek分析（如果存在）
        deepseek_file = Path(settings.CHARTS_DIR) / task_id / "deepseek_analysis.json"
        deepseek_report = ""
        if deepseek_file.exists():
            with open(deepseek_file, 'r', encoding='utf-8') as f:
                deepseek_data = json.load(f)
                deepseek_report = deepseek_data.get('report', '')
        
        # 生成Word报告
        engine = get_r_engine()
        report_path = engine.generate_comprehensive_word_report(task_id, analysis_data, deepseek_report)
        
        if not report_path or not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="综合报告生成失败")
        
        # 生成下载文件名
        current_time = datetime.now(SHANGHAI_TZ).strftime("%Y%m%d_%H%M%S")
        download_filename = f"comprehensive_report_{current_time}.docx"
        
        return FileResponse(
            path=report_path, 
            filename=download_filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载综合报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载综合报告失败: {str(e)}")

@router.get("/download-csv/{task_id}")
async def download_csv_data(task_id: str):
    """
    下载清理后的CSV数据文件
    """
    try:
        # 构建CSV文件路径
        csv_file = Path(settings.CHARTS_DIR) / task_id / "cleaned_data.csv"
        
        if not csv_file.exists():
            raise HTTPException(status_code=404, detail="清理后的数据文件不存在")
        
        # 生成下载文件名
        current_time = datetime.now(SHANGHAI_TZ).strftime("%Y%m%d_%H%M%S")
        download_filename = f"cleaned_data_{current_time}.csv"
        
        return FileResponse(
            path=str(csv_file),
            filename=download_filename,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={download_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载CSV文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载CSV文件失败: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """
    获取系统信息
    """
    try:
        import psutil
        import time
        from pathlib import Path
        
        # 获取系统资源信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 计算系统运行时间（从服务器启动时间算起）
        # 这里简化处理，实际应该记录服务器启动时间
        uptime = time.time() * 1000  # 转换为毫秒
        
        return {
            "success": True,
            "data": {
                "version": "1.0.0",
                "status": "running",
                "uptime": uptime,
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": f"{round(memory.used / 1024 / 1024)} MB / {round(memory.total / 1024 / 1024)} MB",
                "memory_percent": memory.percent,
                "disk_usage": f"{round(disk.used / 1024 / 1024 / 1024, 1)} GB / {round(disk.total / 1024 / 1024 / 1024, 1)} GB",
                "disk_percent": round((disk.used / disk.total) * 100, 1),
                "r_engine_status": "ready"
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return {
            "success": False,
            "message": f"获取系统信息失败: {str(e)}"
        }

@router.get("/storage-stats")
async def get_storage_stats():
    """
    获取存储使用统计
    """
    try:
        from pathlib import Path
        import os
        
        # 计算历史记录数量
        history_dir = Path(settings.HISTORY_DIR)
        history_count = len(list(history_dir.glob("*.json"))) if history_dir.exists() else 0
        
        # 计算图表文件数量和大小
        charts_dir = Path(settings.CHARTS_DIR)
        chart_files = 0
        chart_size = 0
        if charts_dir.exists():
            for task_dir in charts_dir.iterdir():
                if task_dir.is_dir():
                    png_files = list(task_dir.glob("*.png"))
                    chart_files += len(png_files)
                    chart_size += sum(f.stat().st_size for f in png_files)
        
        # 计算报告文件数量和大小（包括两个目录）
        # 1. 临时报告目录
        temp_reports_dir = Path("temp/reports")
        temp_report_files = 0
        temp_report_size = 0
        if temp_reports_dir.exists():
            temp_docx_files = list(temp_reports_dir.glob("*.docx"))
            temp_report_files = len(temp_docx_files)
            temp_report_size = sum(f.stat().st_size for f in temp_docx_files)
        
        # 2. 输出报告目录
        output_reports_dir = Path(settings.CHARTS_DIR).parent / "reports"
        output_report_files = 0
        output_report_size = 0
        if output_reports_dir.exists():
            output_docx_files = list(output_reports_dir.glob("*.docx"))
            output_report_files = len(output_docx_files)
            output_report_size = sum(f.stat().st_size for f in output_docx_files)
        
        # 合并报告统计（去重）
        report_files = max(temp_report_files, output_report_files)  # 取较大值，因为文件应该是重复的
        report_size = max(temp_report_size, output_report_size)
        
        # 计算总大小（MB）
        total_size = round((chart_size + report_size) / 1024 / 1024, 1)
        
        return {
            "success": True,
            "data": {
                "history_count": history_count,
                "chart_files": chart_files,
                "report_files": report_files,
                "total_size": total_size,
                "chart_size_mb": round(chart_size / 1024 / 1024, 1),
                "report_size_mb": round(report_size / 1024 / 1024, 1)
            }
        }
    except Exception as e:
        logger.error(f"获取存储统计失败: {e}")
        return {
            "success": False,
            "message": f"获取存储统计失败: {str(e)}"
        }

@router.post("/clear-cache")
async def clear_cache():
    """
    清理系统缓存
    """
    try:
        import shutil
        from pathlib import Path
        
        cleared_items = []
        total_freed = 0
        
        # 清理临时文件
        temp_dirs = [
            Path("temp"),
            Path("/tmp").glob("pressure_*"),  # 临时文件
        ]
        
        for temp_path in temp_dirs:
            if isinstance(temp_path, Path) and temp_path.exists():
                if temp_path.is_dir():
                    # 计算目录大小
                    size_before = sum(f.stat().st_size for f in temp_path.rglob('*') if f.is_file())
                    # 清理目录内容但保留目录
                    for item in temp_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    
                    cleared_items.append(f"清理临时目录: {temp_path}")
                    total_freed += size_before
        
        # 清理过期的报告文件（超过7天的）
        reports_dir = Path("temp/reports")
        if reports_dir.exists():
            import time
            current_time = time.time()
            for report_file in reports_dir.glob("*.docx"):
                if current_time - report_file.stat().st_mtime > 7 * 24 * 3600:  # 7天
                    size = report_file.stat().st_size
                    report_file.unlink()
                    cleared_items.append(f"删除过期报告: {report_file.name}")
                    total_freed += size
        
        return {
            "success": True,
            "message": "缓存清理完成",
            "data": {
                "cleared_items": cleared_items,
                "freed_space_mb": round(total_freed / 1024 / 1024, 2)
            }
        }
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        return {
            "success": False,
            "message": f"清理缓存失败: {str(e)}"
        }

@router.post("/backup-data")
async def backup_data():
    """
    备份重要数据
    """
    try:
        import shutil
        import zipfile
        from datetime import datetime
        from pathlib import Path
        
        # 创建备份目录
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pressure_system_backup_{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        # 要备份的目录和文件
        backup_items = [
            (Path(settings.HISTORY_DIR), "history"),
            (Path(settings.CHARTS_DIR), "charts"),
            (Path("temp/reports"), "reports"),
        ]
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_path, archive_folder in backup_items:
                if source_path.exists():
                    if source_path.is_dir():
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                # 计算相对路径
                                relative_path = file_path.relative_to(source_path)
                                archive_path = f"{archive_folder}/{relative_path}"
                                zipf.write(file_path, archive_path)
                    else:
                        zipf.write(source_path, f"{archive_folder}/{source_path.name}")
        
        backup_size = backup_path.stat().st_size
        
        return {
            "success": True,
            "message": "数据备份完成",
            "data": {
                "backup_file": backup_filename,
                "backup_path": str(backup_path),
                "backup_size_mb": round(backup_size / 1024 / 1024, 2)
            }
        }
    except Exception as e:
        logger.error(f"数据备份失败: {e}")
        return {
            "success": False,
            "message": f"数据备份失败: {str(e)}"
        }

@router.delete("/clear-all-data")
async def clear_all_data():
    """
    清理所有历史数据（危险操作）
    """
    try:
        import shutil
        from pathlib import Path
        
        cleared_items = []
        
        # 清理历史记录
        history_dir = Path(settings.HISTORY_DIR)
        if history_dir.exists():
            count = len(list(history_dir.glob("*.json")))
            for json_file in history_dir.glob("*.json"):
                json_file.unlink()
            cleared_items.append(f"删除历史记录: {count} 个文件")
        
        # 清理图表文件
        charts_dir = Path(settings.CHARTS_DIR)
        if charts_dir.exists():
            count = 0
            for task_dir in charts_dir.iterdir():
                if task_dir.is_dir():
                    shutil.rmtree(task_dir)
                    count += 1
            cleared_items.append(f"删除图表目录: {count} 个")
        
        # 清理报告文件
        reports_dir = Path("temp/reports")
        if reports_dir.exists():
            count = len(list(reports_dir.glob("*.docx")))
            for report_file in reports_dir.glob("*.docx"):
                report_file.unlink()
            cleared_items.append(f"删除报告文件: {count} 个")
        
        return {
            "success": True,
            "message": "所有数据已清理",
            "data": {
                "cleared_items": cleared_items
            }
        }
    except Exception as e:
        logger.error(f"清理所有数据失败: {e}")
        return {
            "success": False,
            "message": f"清理所有数据失败: {str(e)}"
        }

# -------------------------------------------------------------
# 历史记录相关API已被移动到 backend/api/analysis_history.py
# ------------------------------------------------------------- 