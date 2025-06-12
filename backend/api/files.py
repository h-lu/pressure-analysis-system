"""
文件上传API路由
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
import aiofiles
import os
import uuid
from pathlib import Path
import pandas as pd
import json
from typing import List

from ..core.config import settings
from ..models.schemas import FileUploadResponse, DataPreview, DataValidationResult, AnalysisParams, TaskInfo, TaskStatus
from .analysis import run_analysis_task, tasks, get_r_engine

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传CSV文件
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持CSV文件格式")
        
        # 检查文件大小
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        new_filename = f"{file_id}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / new_filename
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return FileUploadResponse(
            success=True,
            message="文件上传成功",
            filename=new_filename,
            file_size=file_size,
            file_id=file_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/preview/{filename}")
async def preview_data(filename: str):
    """
    预览CSV数据
    """
    try:
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 数据预处理
        df_processed = df.copy()
        
        # 如果有力值列，进行数据清理
        force_col = None
        for col in df.columns:
            if '力值' in col or 'force' in col.lower() or '力' in col:
                force_col = col
                break
        
        if force_col:
            # 清理力值列中的字母N等非数值字符
            df_processed[force_col] = df_processed[force_col].astype(str)
            df_processed[force_col] = df_processed[force_col].str.replace('[^\d.-]', '', regex=True)
            df_processed[force_col] = pd.to_numeric(df_processed[force_col], errors='coerce')
        
        # 生成基础统计信息
        basic_stats = {}
        if force_col and not df_processed[force_col].empty:
            force_data = df_processed[force_col].dropna()
            if len(force_data) > 0:
                basic_stats = {
                    'count': len(force_data),
                    'mean': float(force_data.mean()),
                    'std': float(force_data.std()),
                    'min': float(force_data.min()),
                    'max': float(force_data.max()),
                    'range': float(force_data.max() - force_data.min())
                }
        
        # 生成预览数据
        preview = DataPreview(
            filename=filename,
            total_rows=len(df),
            columns=df.columns.tolist(),
            sample_data=df.head(10).to_dict('records'),
            data_types={col: str(dtype) for col, dtype in df.dtypes.items()},
            missing_values={col: df[col].isnull().sum() for col in df.columns},
            basic_stats=basic_stats
        )
        
        return {
            "success": True,
            "message": "获取数据预览成功",
            "preview": preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据预览失败: {str(e)}")

@router.get("/validate/{filename}")
async def validate_data(filename: str):
    """
    验证CSV数据格式
    """
    try:
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 增加与preview和R脚本一致的清理逻辑
        force_col_name = None
        for col in df.columns:
            if '力值' in col or 'force' in col.lower() or '力' in col:
                force_col_name = col
                break

        if force_col_name:
            # 清理力值列中的字母N等非数值字符，再进行验证
            df[force_col_name] = pd.to_numeric(
                df[force_col_name].astype(str).str.replace('[^\\d.-]', '', regex=True),
                errors='coerce'
            )
        
        # 期望的列名
        expected_columns = ['序号', 'X', 'Y', 'Z', '力值']
        actual_columns = df.columns.tolist()
        
        # 检查列名
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        extra_columns = [col for col in actual_columns if col not in expected_columns]
        
        errors = []
        warnings = []
        
        # 验证必要列
        if missing_columns:
            errors.append(f"缺少必要列: {', '.join(missing_columns)}")
        
        # 检查额外列
        if extra_columns:
            warnings.append(f"包含额外列: {', '.join(extra_columns)}")
        
        # 检查数据类型
        if '力值' in df.columns:
            # 验证 '力值' 列是否为数字，且没有因转换失败而产生的空值
            if not pd.api.types.is_numeric_dtype(df['力值']) or df['力值'].isnull().any():
                errors.append("力值列包含无法解析的非数值数据")
        
        # 检查空值 (在数据清理之后)
        if df.isnull().any().any():
            null_cols = df.columns[df.isnull().any()].tolist()
            warnings.append(f"以下列包含空值: {', '.join(null_cols)}")
        
        # 检查数据量
        if len(df) < 10:
            warnings.append("数据量过少，可能影响分析结果")
        
        validation_result = DataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            row_count=len(df),
            column_count=len(df.columns),
            expected_columns=expected_columns,
            actual_columns=actual_columns,
            missing_columns=missing_columns,
            extra_columns=extra_columns
        )
        
        return {
            "success": True,
            "message": "数据验证完成",
            "validation": validation_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")

@router.get("/chart/{chart_name}")
async def get_chart(chart_name: str):
    """
    获取分析结果图表（兼容旧版本）
    """
    try:
        # 检查图表文件名是否安全
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.svg']
        if not any(chart_name.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="不支持的图片格式")
        
        # 构建图表文件路径
        chart_path = Path(settings.CHARTS_DIR) / chart_name
        
        if not chart_path.exists():
            # 如果charts目录中没有，尝试在output目录中查找
            output_path = Path("output") / chart_name
            if output_path.exists():
                chart_path = output_path
            else:
                raise HTTPException(status_code=404, detail="图表文件不存在")
        
        # 返回图片文件
        return FileResponse(
            path=chart_path,
            media_type="image/png",
            filename=chart_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表失败: {str(e)}")

@router.get("/chart/{task_id}/{chart_name}")
async def get_chart_by_task(task_id: str, chart_name: str):
    """
    根据任务ID获取特定的图表文件
    """
    try:
        # 检查图表文件名是否安全
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.svg']
        if not any(chart_name.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="不支持的图片格式")
        
        # 按优先级查找图表文件
        search_paths = [
            Path(settings.CHARTS_DIR) / task_id / chart_name,  # 专用任务目录
            Path("static") / "charts" / task_id / chart_name,   # static/charts目录
            Path("backend") / "static" / "charts" / task_id / chart_name,  # backend/static/charts目录
            Path("output") / chart_name,  # output目录（兼容）
            Path(settings.CHARTS_DIR) / chart_name  # charts根目录（兼容）
        ]
        
        chart_path = None
        for path in search_paths:
            if path.exists():
                chart_path = path
                break
        
        if chart_path is None:
            raise HTTPException(status_code=404, detail=f"任务 {task_id} 的图表文件 {chart_name} 不存在")
        
        # 返回图片文件
        return FileResponse(
            path=chart_path,
            media_type="image/png",
            filename=chart_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表失败: {str(e)}")

@router.get("/download/{file_type}/{task_id}")
async def download_file(file_type: str, task_id: str):
    """
    下载结果文件
    """
    try:
        if file_type == "pdf":
            # PDF报告下载
            file_path = Path(settings.REPORTS_DIR) / task_id / "report.pdf"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="PDF报告不存在")
            return FileResponse(file_path, filename=f"analysis_report_{task_id}.pdf")
            
        elif file_type == "csv":
            # 清洗后的CSV数据下载
            file_path = Path(settings.REPORTS_DIR) / task_id / "cleaned_data.csv"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="清洗后的数据不存在")
            return FileResponse(file_path, filename=f"cleaned_data_{task_id}.csv")
            
        elif file_type == "charts":
            # 图表ZIP包下载
            file_path = Path(settings.REPORTS_DIR) / task_id / "charts.zip"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="图表包不存在")
            return FileResponse(file_path, filename=f"charts_{task_id}.zip")
            
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")

@router.get("/list")
async def list_uploaded_files():
    """
    列出已上传的文件
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        
        if not upload_dir.exists():
            return {
                "success": True,
                "message": "获取文件列表成功",
                "files": []
            }
        
        files = []
        for file_path in upload_dir.glob("*.csv"):
            file_stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": file_stat.st_size,
                "created_at": file_stat.st_ctime,
                "modified_at": file_stat.st_mtime
            })
        
        return {
            "success": True,
            "message": "获取文件列表成功",
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    """
    删除上传的文件
    """
    try:
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_path.unlink()
        
        return {
            "success": True,
            "message": "文件删除成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

@router.post("/upload-and-analyze")
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_forces: str = Form("5,25,50"),
    tolerance_abs: str = Form("2"),
    tolerance_pct: str = Form("5")
):
    """
    一键上传文件并启动分析
    """
    try:
        # 1. 上传文件
        upload_response = await upload_file(file)
        file_id = upload_response.file_id
        
        # 2. 解析参数
        try:
            target_forces_list = [float(x.strip()) for x in target_forces.split(',')]
            
            # 处理单个或多个容差值
            def parse_tolerance(val_str: str, num_targets: int) -> List[float]:
                vals = [float(x.strip()) for x in val_str.split(',')]
                if len(vals) == 1:
                    return vals * num_targets
                if len(vals) != num_targets:
                    raise ValueError("容差值的数量必须为1或与目标力值的数量相同")
                return vals

            tolerance_abs_list = parse_tolerance(tolerance_abs, len(target_forces_list))
            tolerance_pct_list = parse_tolerance(tolerance_pct, len(target_forces_list))

        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=f"分析参数格式错误: {e}")

        # 3. 创建并启动分析任务 (复用 analysis.py 的逻辑)
        params = AnalysisParams(
            file_id=file_id,
            target_forces=target_forces_list,
            tolerance_abs=tolerance_abs_list,
            tolerance_pct=tolerance_pct_list
        )

        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务信息
        task_info = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，等待执行..."
        )
        tasks[task_id] = task_info
        
        # 构建文件路径
        uploads_dir = Path(settings.UPLOAD_DIR)
        csv_path = str(uploads_dir / f"{file_id}.csv")
        
        # 添加后台任务
        background_tasks.add_task(run_analysis_task, task_id, csv_path, params)
        
        return {
            "success": True,
            "message": "文件上传成功，分析任务已启动",
            "file_id": file_id,
            "task_id": task_id
        }

    except HTTPException as e:
        # 重新抛出已知的HTTP异常
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"一键上传分析失败: {str(e)}") 