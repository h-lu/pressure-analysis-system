"""
数据模型和API请求/响应模式
"""
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# 分析参数模型
class AnalysisParams(BaseModel):
    """分析参数"""
    file_id: str = Field(..., description="文件ID", example="12345-abcde")
    target_forces: List[float] = Field(..., description="目标力值列表", example=[5.0, 25.0, 50.0])
    tolerance_abs: Union[float, List[float]] = Field(..., description="绝对容差(N)或列表", example=2.0)
    tolerance_pct: Union[float, List[float]] = Field(..., description="百分比容差(%)或列表", example=5.0)
    
    @field_validator('target_forces')
    @classmethod
    def validate_target_forces(cls, v: List[float]) -> List[float]:
        if not v:
            raise ValueError('目标力值列表不能为空')
        if any(force <= 0 for force in v):
            raise ValueError('目标力值必须大于0')
        return sorted(list(set(v)))  # 去重并排序

    @field_validator('tolerance_abs', 'tolerance_pct')
    @classmethod
    def validate_and_transform_tolerances(cls, v: Any, info: ValidationInfo) -> List[float]:
        if 'target_forces' not in info.data:
            # This validation depends on 'target_forces', which is validated first.
            # If 'target_forces' is invalid or missing, Pydantic will have already raised an error.
            # We return 'v' to avoid a crash here, letting the original error be displayed.
            return v

        target_forces = info.data['target_forces']
        n_targets = len(target_forces)
        field_name = info.field_name

        if isinstance(v, (float, int)):
            if v <= 0:
                raise ValueError(f'{field_name} 的值必须大于0')
            return [float(v)] * n_targets
        elif isinstance(v, list):
            if len(v) != n_targets:
                raise ValueError(f'{field_name} 列表的长度 ({len(v)}) 必须与 target_forces 的长度 ({n_targets}) 相同')
            if any(val <= 0 for val in v):
                 raise ValueError(f'{field_name} 列表中的值必须大于0')
            return v
        else:
            raise TypeError(f'{field_name} 必须是数字或数字列表')

# 分析请求模型
class AnalysisRequest(BaseModel):
    """分析请求"""
    params: AnalysisParams
    filename: str = Field(..., description="上传的文件名")

# 任务状态枚举
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 任务信息模型
class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = Field(default=0, ge=0, le=100)
    message: str = ""
    error: Optional[str] = None

# 统计结果模型
class StatisticsResult(BaseModel):
    """统计分析结果"""
    total_records: int
    valid_records: int
    invalid_records: int
    mean_force: float
    std_force: float
    min_force: float
    max_force: float
    target_analysis: Dict[str, Any]  # 按目标力值分组的统计
    success_rate: float
    overall_bias: float

# 图表信息模型
class ChartInfo(BaseModel):
    """图表信息"""
    chart_id: str
    title: str
    description: str
    file_path: str
    file_url: str
    chart_type: str
    created_at: datetime = Field(default_factory=datetime.now)

# 分析结果模型
class AnalysisResult(BaseModel):
    """完整分析结果"""
    task_id: str
    statistics: StatisticsResult
    charts: List[ChartInfo]
    summary_report: str
    data_quality_report: str
    recommendations: List[str]
    files: Dict[str, str]  # 文件类型到URL的映射

# API响应基类
class BaseResponse(BaseModel):
    """API响应基类"""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

# 任务创建响应
class TaskCreateResponse(BaseResponse):
    """任务创建响应"""
    task_id: str
    estimated_duration: int  # 预估完成时间(秒)

# 任务状态响应
class TaskStatusResponse(BaseResponse):
    """任务状态响应"""
    task: TaskInfo

# 分析结果响应
class AnalysisResultResponse(BaseResponse):
    """分析结果响应"""
    result: AnalysisResult

# 文件上传响应
class FileUploadResponse(BaseResponse):
    """文件上传响应"""
    filename: str
    file_size: int
    file_id: str

# 错误响应
class ErrorResponse(BaseResponse):
    """错误响应"""
    error_code: str
    error_details: Optional[Dict[str, Any]] = None

# 数据预览模型
class DataPreview(BaseModel):
    """数据预览"""
    filename: str
    total_rows: int
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    basic_stats: Dict[str, Any]

# 数据验证结果
class DataValidationResult(BaseModel):
    """数据验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    row_count: int
    column_count: int
    expected_columns: List[str]
    actual_columns: List[str]
    missing_columns: List[str]
    extra_columns: List[str] 