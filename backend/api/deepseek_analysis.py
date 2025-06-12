"""
DeepSeek AI分析API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import json
import logging
from typing import Any, Dict
from openai import OpenAI
from backend.core.config import settings
from backend.services.config_manager import config_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalysisReportRequest(BaseModel):
    """分析报告请求模型"""
    analysis_data: Dict[str, Any]
    report_type: str = "comprehensive"  # comprehensive, summary, technical
    language: str = "chinese"  # chinese, english

class AnalysisReportResponse(BaseModel):
    """分析报告响应模型"""
    success: bool
    report: str
    analysis_summary: Dict[str, Any]
    message: str

def create_deepseek_prompt(analysis_data: Dict[str, Any], report_type: str = "comprehensive") -> str:
    """
    创建DeepSeek分析提示词
    """
    
    # 动态构建参数摘要
    params_summary = ""
    if "analysis_parameters" in analysis_data:
        params = analysis_data["analysis_parameters"]
        target_forces = params.get("target_forces", [])
        tolerance_abs = params.get("tolerance_abs", [])
        tolerance_pct = params.get("tolerance_pct", [])

        if target_forces and tolerance_abs and tolerance_pct and len(target_forces) == len(tolerance_abs) and len(target_forces) == len(tolerance_pct):
            params_summary += "\\n\\n## 本次分析使用的关键参数：\\n"
            params_summary += "请在报告中紧密结合以下用户设定的目标值和容差进行分析，这是评估系统性能的核心依据：\\n"
            for i, force in enumerate(target_forces):
                params_summary += (
                    f"- **目标力 {force}N**: "
                    f"绝对容差(±) = {tolerance_abs[i]}N, "
                    f"百分比容差(±) = {tolerance_pct[i]}%\\n"
                )
    
    base_prompt = f"""
你是一位专业的工业数据分析专家，专门从事可移动式压力采集装置的质量控制和统计过程控制(SPC)分析。请基于提供的压力采集数据分析结果，生成一份详细、专业的分析报告。

## 设备背景说明：
本系统是可移动式压力采集装置，主要功能包括：
- 力传感器放置于1m×1m电动滑轨上，可二维平面移动
- 通过上位机控制传感器位置和数据采集
- 测试机器人末端在指定位置施加不同压力(5N、25N、50N)
- 数据格式：序号、X、Y、Z、力值
{params_summary}
## 你的专业背景：
- 精通机器人力控制和压力测量系统分析
- 熟悉移动式测量设备的精度评估
- 具备丰富的空间位置相关的测量系统分析经验
- 精通过程能力分析、控制图理论和异常检测

## 报告要求：
1. **专业性**: 使用准确的统计术语和工业标准
2. **完整性**: 涵盖所有重要的分析维度
3. **实用性**: 提供具体可执行的改进建议
4. **逻辑性**: 结构清晰，层次分明

## 分析数据结构说明：
- `data_summary`: 基础数据概览
- `overall_stats`: 整体统计指标
- `target_analysis`: 按目标力值(5N、25N、50N)分组的详细分析
- `trend_stats`: 测试序列趋势分析结果
- `outlier_summary`: 异常值检测结果
- `stability_analysis`: 稳定性分析(游程检验)
- `change_point_analysis`: 变化点检测
- `autocorr_analysis`: 自相关分析
- `process_capability`: 过程能力分析(Cp, Cpk)
- `spatial_analysis`: 空间位置(X、Y、Z)相关的分布分析
- `error_distribution_analysis`: 压力测量误差分布分析
- `multi_source_variation_analysis`: 多源变异分析(不同测试位置、机器人施压一致性)

## 报告结构：

### 1. 执行摘要 (Executive Summary)
- 系统整体表现评级(优秀/良好/一般/需改进/不合格)
- 关键发现(3-5个要点)
- 主要问题和风险
- 优先改进建议

### 2. 数据质量评估 (Data Quality Assessment)
- 数据完整性和可靠性
- 测量系统稳定性
- 异常值和缺失值影响

### 3. 过程能力分析 (Process Capability Analysis)
- 各目标力值的Cp和Cpk指数解读
- 过程能力等级评定
- 规格限制符合性分析
- 短期vs长期能力对比

### 4. 统计过程控制分析 (Statistical Process Control)
- 过程稳定性评估
- 趋势和偏移检测
- 控制图失控模式识别
- 特殊原因vs普通原因变异

### 5. 多维度变异分析 (Multi-dimensional Variation Analysis)
- 不同测试位置(X、Y、Z)的压力精度差异
- 机器人末端施压一致性评估
- 传感器移动精度对测量结果的影响
- 空间位置相关的测量异常模式

### 6. 根本原因分析 (Root Cause Analysis)
- 基于帕雷托原理的问题排序
- 异常模式的系统性分析
- 潜在影响因素识别

### 7. 改进建议 (Improvement Recommendations)
- 短期纠正措施(1个月内)
- 中期改进计划(3-6个月)
- 长期优化策略(6个月以上)
- 预防措施建议

### 8. 监控建议 (Monitoring Recommendations)
- 关键测试位置和压力值的监控点识别
- 传感器校准频率建议
- 机器人施压精度预警阈值设定
- 系统精度验证计划

## 数据解读指南：

### 过程能力指数解读：
- Cp, Cpk ≥ 1.33: 过程能力优秀
- 1.0 ≤ Cp, Cpk < 1.33: 过程能力合格
- 0.67 ≤ Cp, Cpk < 1.0: 过程能力勉强
- Cp, Cpk < 0.67: 过程能力不合格

### 成功率评级：
- ≥95%: 优秀
- 90-95%: 良好
- 80-90%: 一般
- 70-80%: 需改进
- <70%: 不合格

### 变异系数(CV)评级：
- CV ≤ 5%: 优秀稳定性
- 5% < CV ≤ 10%: 良好稳定性
- 10% < CV ≤ 15%: 一般稳定性
- CV > 15%: 稳定性差

请基于以下分析数据生成专业报告：
"""
    
    if report_type == "summary":
        base_prompt += "\n**注意**: 请生成简明摘要版本，重点突出关键发现和建议。\n"
    elif report_type == "technical":
        base_prompt += "\n**注意**: 请生成技术详细版本，包含深入的统计分析和技术细节。\n"
    
    return base_prompt

@router.post("/generate-report", response_model=AnalysisReportResponse)
async def generate_analysis_report(request: AnalysisReportRequest):
    """
    使用DeepSeek AI生成分析报告
    """
    try:
        # 使用用户配置创建OpenAI客户端
        user_config = config_manager.get_deepseek_config()
        
        if not user_config.get("api_key"):
            return AnalysisReportResponse(
                success=False,
                report="",
                analysis_summary={},
                message="未配置DeepSeek API Key，请先在设置中配置"
            )
        
        client = OpenAI(
            api_key=user_config["api_key"],
            base_url=user_config["base_url"]
        )
        
        # 生成提示词
        prompt = create_deepseek_prompt(request.analysis_data, request.report_type)
        
        # 准备消息
        messages = [
            {
                "role": "system", 
                "content": "你是一位专业的工业数据分析专家，精通统计过程控制和质量管理。请用中文回答。"
            },
            {
                "role": "user", 
                "content": f"{prompt}\n\n分析数据：\n{json.dumps(request.analysis_data, ensure_ascii=False, indent=2)}"
            }
        ]
        
        # 调用DeepSeek API
        logger.info("开始调用DeepSeek API生成分析报告...")
        response = client.chat.completions.create(
            model=user_config["model"],
            messages=messages,
            stream=False,
            temperature=0.1,  # 降低随机性，提高一致性
            max_tokens=8192  # 修正max_tokens的值
        )
        
        report_content = response.choices[0].message.content
        
        # 提取关键摘要信息
        analysis_summary = extract_summary_from_data(request.analysis_data)
        
        # 保存DeepSeek分析结果到文件
        # 尝试从analysis_data中提取task_id，如果没有则生成一个
        task_id = request.analysis_data.get('task_id')
        if task_id:
            try:
                from pathlib import Path
                import time
                
                charts_dir = Path(settings.CHARTS_DIR) / task_id
                if charts_dir.exists():
                    # 保存DeepSeek分析结果
                    deepseek_result = {
                        "success": True,
                        "report": report_content,
                        "analysis_summary": analysis_summary,
                        "message": "分析报告生成成功",
                        "generated_at": time.time(),
                        "report_type": request.report_type
                    }
                    
                    deepseek_file = charts_dir / "deepseek_analysis.json"
                    with open(deepseek_file, 'w', encoding='utf-8') as f:
                        json.dump(deepseek_result, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"DeepSeek分析结果已保存到: {deepseek_file}")
                
            except Exception as save_error:
                logger.warning(f"保存DeepSeek分析结果失败: {save_error}")
        
        logger.info("DeepSeek分析报告生成成功")
        
        return AnalysisReportResponse(
            success=True,
            report=report_content,
            analysis_summary=analysis_summary,
            message="分析报告生成成功"
        )
        
    except Exception as e:
        logger.error(f"生成分析报告失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析报告生成失败: {str(e)}"
        )

@router.post("/analyze-from-file")
async def analyze_from_file(file: UploadFile = File(...)):
    """
    从上传的analysis_results.json文件生成分析报告
    """
    try:
        # 验证文件类型
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="请上传JSON格式的分析结果文件"
            )
        
        # 读取文件内容
        content = await file.read()
        analysis_data = json.loads(content.decode('utf-8'))
        
        # 创建分析请求
        request = AnalysisReportRequest(
            analysis_data=analysis_data,
            report_type="comprehensive"
        )
        
        # 生成报告
        return await generate_analysis_report(request)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="JSON文件格式错误"
        )
    except Exception as e:
        logger.error(f"文件分析失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"文件分析失败: {str(e)}"
        )

def extract_summary_from_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从分析数据中提取关键摘要信息
    """
    summary = {}
    
    try:
        # 基础统计
        if 'overall_stats' in analysis_data and analysis_data['overall_stats']:
            stats = analysis_data['overall_stats'][0]
            summary['total_samples'] = stats.get('样本数', 0)
            summary['mean_force'] = round(stats.get('均值', 0), 2)
            summary['cv_percent'] = round(stats.get('变异系数', 0), 2)
        
        # 整体成功率
        if 'target_analysis' in analysis_data:
            target_data = analysis_data['target_analysis']
            if target_data:
                total_points = sum(item.get('数据点数', 0) for item in target_data)
                weighted_success = sum(
                    item.get('数据点数', 0) * item.get('成功率_综合', 0) 
                    for item in target_data
                )
                overall_success_rate = weighted_success / total_points if total_points > 0 else 0
                summary['overall_success_rate'] = round(overall_success_rate, 1)
        
        # 过程能力
        if 'process_capability' in analysis_data:
            capability_data = analysis_data['process_capability']
            if capability_data:
                avg_cp = sum(item.get('Cp', 0) for item in capability_data) / len(capability_data)
                avg_cpk = sum(item.get('Cpk', 0) for item in capability_data) / len(capability_data)
                summary['average_cp'] = round(avg_cp, 3)
                summary['average_cpk'] = round(avg_cpk, 3)
        
        # 异常检测
        if 'outlier_summary' in analysis_data:
            outlier_data = analysis_data['outlier_summary']
            if outlier_data:
                total_outliers = sum(item.get('IQR异常值', 0) for item in outlier_data)
                summary['total_outliers'] = total_outliers
        
        # 多源变异分析
        if 'multi_source_variation_analysis' in analysis_data:
            multi_source = analysis_data['multi_source_variation_analysis']
            if 'performance_by_machine' in multi_source:
                machine_data = multi_source['performance_by_machine']
                if machine_data:
                    machines = list(set(item.get('machine_id', '') for item in machine_data))
                    summary['test_positions'] = len(machines)  # 改为测试位置数量
            
            # 移除班次分析，因为该设备没有班次概念
        
    except Exception as e:
        logger.warning(f"提取摘要信息时发生错误: {str(e)}")
    
    return summary

@router.get("/get-config")
async def get_deepseek_config():
    """
    获取DeepSeek API配置
    """
    try:
        user_config = config_manager.get_deepseek_config()
        masked_key = config_manager.get_masked_api_key()
        
        return {
            "success": True,
            "data": {
                "api_key": masked_key,
                "base_url": user_config.get("base_url", "https://api.deepseek.com"),
                "model": user_config.get("model", "deepseek-chat")
            }
        }
    except Exception as e:
        logger.error(f"获取DeepSeek配置失败: {str(e)}")
        return {
            "success": False,
            "message": f"获取配置失败: {str(e)}"
        }

@router.post("/save-config")
async def save_deepseek_config(config: dict):
    """
    保存DeepSeek API配置
    """
    try:
        api_key = config.get("api_key", "")
        base_url = config.get("base_url", "https://api.deepseek.com")
        model = config.get("model", "deepseek-chat")
        
        if not api_key:
            return {
                "success": False,
                "message": "API Key不能为空"
            }
        
        # 使用配置管理器保存配置
        success = config_manager.save_deepseek_config(api_key, base_url, model)
        
        if success:
            return {
                "success": True,
                "message": "配置保存成功"
            }
        else:
            return {
                "success": False,
                "message": "配置保存失败"
            }
    except Exception as e:
        logger.error(f"保存DeepSeek配置失败: {str(e)}")
        return {
            "success": False,
            "message": f"保存配置失败: {str(e)}"
        }

@router.get("/test-connection")
async def test_deepseek_connection():
    """
    测试DeepSeek API连接（使用用户配置）
    """
    try:
        user_config = config_manager.get_deepseek_config()
        
        if not user_config.get("api_key"):
            return {
                "success": False,
                "message": "未配置API Key，请先在设置中配置DeepSeek API"
            }
        
        client = OpenAI(
            api_key=user_config["api_key"],
            base_url=user_config["base_url"]
        )
        
        response = client.chat.completions.create(
            model=user_config["model"],
            messages=[
                {"role": "system", "content": "你是一个有用的助手"},
                {"role": "user", "content": "请简单回复：连接测试成功"}
            ],
            stream=False,
            max_tokens=50
        )
        
        return {
            "success": True,
            "message": "DeepSeek API连接成功",
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        logger.error(f"DeepSeek API连接测试失败: {str(e)}")
        return {
            "success": False,
            "message": f"连接失败: {str(e)}"
        }

@router.post("/test-connection")
async def test_deepseek_connection_with_config(request: dict):
    """
    使用自定义配置测试DeepSeek API连接
    """
    try:
        api_key = request.get("api_key")
        base_url = request.get("base_url", "https://api.deepseek.com")
        
        if not api_key:
            return {"success": False, "message": "API Key不能为空"}
        
        # 使用自定义配置创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个有用的助手"},
                {"role": "user", "content": "请简单回复：连接测试成功"}
            ],
            stream=False,
            max_tokens=50
        )
        
        return {
            "success": True,
            "message": "DeepSeek API连接成功",
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        logger.error(f"DeepSeek API连接测试失败: {str(e)}")
        return {
            "success": False,
            "message": f"连接失败: {str(e)}"
        }



@router.post("/generate-comprehensive-word-report")
async def generate_comprehensive_word_report(task_id: str):
    """
    生成包含DeepSeek分析和R分析结果的综合Word报告
    """
    try:
        from ..services.r_analysis import RAnalysisEngine
        from pathlib import Path
        import json
        
        # 1. 检查任务是否存在
        engine = RAnalysisEngine()
        
        # 尝试多个可能的分析结果文件位置
        possible_paths = [
            Path(__file__).parent.parent.parent / "temp" / "reports" / f"analysis_results_{task_id}.json",
            Path(settings.CHARTS_DIR) / task_id / "analysis_results.json",
            Path(__file__).parent.parent.parent / "backend" / "static" / "charts" / task_id / "analysis_results.json"
        ]
        
        analysis_file = None
        for path in possible_paths:
            if path.exists():
                analysis_file = path
                logger.info(f"找到分析结果文件: {analysis_file}")
                break
        
        if not analysis_file:
            logger.error(f"未找到任务 {task_id} 的分析结果，尝试了以下路径: {[str(p) for p in possible_paths]}")
            raise HTTPException(
                status_code=404,
                detail=f"未找到任务 {task_id} 的分析结果"
            )
        
        # 2. 读取R分析结果
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 3. 生成DeepSeek分析报告
        logger.info("开始生成DeepSeek分析报告...")
        
        # 使用用户配置的API参数
        user_config = config_manager.get_deepseek_config()
        
        if not user_config.get("api_key"):
            raise HTTPException(
                status_code=400,
                detail="未配置DeepSeek API Key，请先在设置中配置"
            )
        
        client = OpenAI(
            api_key=user_config["api_key"],
            base_url=user_config["base_url"]
        )
        
        prompt = create_deepseek_prompt(analysis_data, "comprehensive")
        
        messages = [
            {
                "role": "system", 
                "content": "你是一位专业的工业数据分析专家，精通统计过程控制和质量管理。请用中文回答。"
            },
            {
                "role": "user", 
                "content": f"{prompt}\n\n分析数据：\n{json.dumps(analysis_data, ensure_ascii=False, indent=2)}"
            }
        ]
        
        response = client.chat.completions.create(
            model=user_config["model"],
            messages=messages,
            stream=False,
            temperature=0.1,
            max_tokens=4000
        )
        
        deepseek_report = response.choices[0].message.content
        logger.info("DeepSeek分析报告生成成功")
        
        # 3.5. 保存DeepSeek分析结果到json文件
        try:
            charts_dir = Path(settings.CHARTS_DIR) / task_id
            if charts_dir.exists():
                import time
                deepseek_result = {
                    "success": True,
                    "report": deepseek_report,
                    "analysis_summary": extract_summary_from_data(analysis_data),
                    "message": "分析报告生成成功",
                    "generated_at": time.time(),
                    "report_type": "comprehensive"
                }
                
                deepseek_file = charts_dir / "deepseek_analysis.json"
                with open(deepseek_file, 'w', encoding='utf-8') as f:
                    json.dump(deepseek_result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"DeepSeek分析结果已保存到: {deepseek_file}")
            else:
                logger.warning(f"任务目录不存在: {charts_dir}")
        except Exception as save_error:
            logger.warning(f"保存DeepSeek分析结果失败: {save_error}")
        
        # 4. 生成综合Word报告
        logger.info("开始生成综合Word报告...")
        try:
            comprehensive_report_path = engine.generate_comprehensive_word_report(
                task_id=task_id,
                analysis_data=analysis_data,
                deepseek_report=deepseek_report
            )
            
            if not comprehensive_report_path or not Path(comprehensive_report_path).exists():
                raise HTTPException(status_code=500, detail="综合Word报告生成失败：文件未创建")
                
        except Exception as word_error:
            logger.error(f"Word报告生成详细错误: {word_error}")
            raise HTTPException(status_code=500, detail=f"综合Word报告生成失败：{str(word_error)}")
        
        # 5. 返回下载链接
        return {
            "success": True,
            "message": "综合Word报告生成成功",
            "download_url": f"/api/download-comprehensive-report/{task_id}",
            "report_path": str(comprehensive_report_path),
            "analysis_summary": extract_summary_from_data(analysis_data)
        }
        
    except Exception as e:
        logger.error(f"生成综合Word报告失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"综合Word报告生成失败: {str(e)}"
        )

@router.get("/check/{task_id}")
async def check_deepseek_analysis(task_id: str):
    """
    检查指定任务的DeepSeek分析是否存在
    """
    try:
        from pathlib import Path
        
        # 检查任务目录是否存在
        charts_dir = Path(settings.CHARTS_DIR) / task_id
        if not charts_dir.exists():
            return {
                "exists": False,
                "message": "任务不存在"
            }
        
        # 检查deepseek分析文件是否存在
        deepseek_file = charts_dir / "deepseek_analysis.json"
        
        if deepseek_file.exists():
            # 读取文件内容验证
            try:
                with open(deepseek_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    "exists": True,
                    "message": "DeepSeek分析报告存在",
                    "generated_at": data.get("generated_at"),
                    "report_type": data.get("report_type", "comprehensive")
                }
            except Exception as e:
                logger.warning(f"读取DeepSeek分析文件失败: {e}")
                return {
                    "exists": False,
                    "message": "DeepSeek分析文件损坏"
                }
        else:
            return {
                "exists": False,
                "message": "尚未生成DeepSeek分析报告"
            }
            
    except Exception as e:
        logger.error(f"检查DeepSeek分析时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"检查DeepSeek分析失败: {str(e)}"
        )

@router.get("/get/{task_id}")
async def get_deepseek_analysis(task_id: str):
    """
    获取指定任务的DeepSeek分析结果
    """
    try:
        from pathlib import Path
        
        # 检查任务目录是否存在
        charts_dir = Path(settings.CHARTS_DIR) / task_id
        if not charts_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        # 检查deepseek分析文件是否存在
        deepseek_file = charts_dir / "deepseek_analysis.json"
        
        if not deepseek_file.exists():
            raise HTTPException(
                status_code=404,
                detail="DeepSeek分析报告不存在"
            )
        
        # 读取并返回分析结果
        try:
            with open(deepseek_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "success": True,
                "data": data,
                "message": "获取DeepSeek分析报告成功"
            }
        except Exception as e:
            logger.error(f"读取DeepSeek分析文件失败: {e}")
            raise HTTPException(
                status_code=500,
                detail="DeepSeek分析文件读取失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取DeepSeek分析时出错: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取DeepSeek分析失败: {str(e)}"
        ) 