#!/usr/bin/env python3
"""
真实的综合分析调用脚本
对demo_data.csv进行完整的分析流程：
1. 上传文件
2. 执行R分析并生成所有图表
3. 调用DeepSeek进行AI分析
4. 生成综合Word报告
5. 下载结果
"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def log_step(step, message):
    """记录步骤"""
    print(f"\n{'='*10} {step} {'='*10}")
    print(f"📋 {message}")
    print()

def check_server():
    """检查服务器状态"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器正常运行: {data.get('service', 'Unknown')}")
            return True
        else:
            print(f"❌ 服务器状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接服务器: {str(e)}")
        return False

def upload_file(file_path):
    """上传文件"""
    log_step("步骤1", f"上传文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 文件上传成功")
            print(f"   文件ID: {data.get('file_id')}")
            print(f"   文件大小: {data.get('file_size')} bytes")
            print(f"   数据行数: {data.get('preview_info', {}).get('total_rows', 'N/A')}")
            return data.get('file_id')
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 上传过程出错: {str(e)}")
        return None

def wait_for_task_completion(task_id, max_wait_seconds=300):
    """等待任务完成"""
    start_time = time.time()
    last_progress = -1
    
    while True:
        try:
            # 检查任务状态
            response = requests.get(f"{BASE_URL}/api/task/{task_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                task = data.get('task', {})
                status = task.get('status')
                progress = task.get('progress', 0)
                message = task.get('message', '')
                
                # 显示进度（仅在进度变化时）
                if progress != last_progress:
                    print(f"   进度: {progress}% - {message}")
                    last_progress = progress
                
                if status == 'completed':
                    print(f"✅ 分析任务完成")
                    
                    # 获取分析结果
                    results_response = requests.get(f"{BASE_URL}/api/results/{task_id}", timeout=30)
                    if results_response.status_code == 200:
                        results_data = results_response.json()
                        results = results_data.get('result', {})
                        
                        # 显示关键统计信息
                        if 'data_summary' in results:
                            summary = results['data_summary']
                            if isinstance(summary, list) and len(summary) > 0:
                                summary = summary[0]
                            print(f"   数据概览:")
                            print(f"     - 总行数: {summary.get('总行数', 'N/A')}")
                            print(f"     - 力值范围: {summary.get('力值最小值', 'N/A')} - {summary.get('力值最大值', 'N/A')} N")
                            print(f"     - 平均力值: {summary.get('力值均值', 'N/A')} N")
                        
                        if 'charts_info' in results:
                            charts_info = results['charts_info']
                            print(f"   生成图表数量: {len(charts_info.get('charts', []))}")
                    
                    return task_id
                    
                elif status == 'failed':
                    error = task.get('error', '未知错误')
                    print(f"❌ 分析任务失败: {error}")
                    return None
                    
                elif status in ['pending', 'running']:
                    # 检查超时
                    if time.time() - start_time > max_wait_seconds:
                        print(f"❌ 任务超时 ({max_wait_seconds}秒)")
                        return None
                    
                    # 等待一段时间后再检查
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 未知任务状态: {status}")
                    return None
            else:
                print(f"❌ 无法获取任务状态: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 检查任务状态时出错: {str(e)}")
            return None

def run_analysis(file_id):
    """执行分析"""
    log_step("步骤2", "执行R统计分析并生成所有图表")
    
    # 分析参数
    analysis_params = {
        "file_id": file_id,
        "target_forces": [5, 25, 50],
        "tolerance_abs": 2.0,
        "tolerance_pct": 5.0,
        "window_size": 10,
        "confidence_level": 0.95,
        "equipment_info": {
            "name": "压力测试机器人",
            "model": "PT-2024",
            "serial": "PT2024001",
            "calibration_date": "2024-01-15"
        },
        "operator_info": {
            "name": "测试操作员",
            "shift": "白班",
            "date": "2024-01-20"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=analysis_params,
            timeout=300  # 5分钟超时
        )
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ 分析任务已启动")
            print(f"   任务ID: {task_id}")
            print(f"   预估时长: {data.get('estimated_duration', 'N/A')} 秒")
            
            # 等待任务完成
            print("⏳ 正在等待分析完成...")
            return wait_for_task_completion(task_id)
        else:
            print(f"❌ 分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("❌ 分析超时，请稍后再试")
        return None
    except Exception as e:
        print(f"❌ 分析过程出错: {str(e)}")
        return None

def generate_comprehensive_report(task_id):
    """生成综合Word报告"""
    log_step("步骤3", "调用DeepSeek AI并生成综合Word报告")
    
    # 报告参数
    report_params = {
        "report_title": "机器人压力测试系统 - 综合质量分析报告",
        "equipment_info": {
            "name": "压力测试机器人",
            "model": "PT-2024",
            "serial": "PT2024001",
            "calibration_date": "2024-01-15"
        },
        "test_conditions": {
            "environment": "标准实验室环境",
            "temperature": "23±2°C",
            "humidity": "45-65%RH",
            "operator": "测试操作员"
        },
        "analysis_focus": [
            "过程稳定性评估",
            "精度与重复性分析", 
            "异常模式识别",
            "质量改进建议"
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/deepseek/generate-comprehensive-word-report",
            json={
                "task_id": task_id,
                **report_params
            },
            timeout=600  # 10分钟超时，因为包含AI调用
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 综合报告生成成功")
            print(f"   报告任务ID: {data.get('report_task_id')}")
            print(f"   Word文件: {data.get('word_file')}")
            print(f"   文件大小: {data.get('file_size_mb', 'N/A')} MB")
            
            # 显示报告统计
            stats = data.get('report_stats', {})
            print(f"   报告统计:")
            print(f"     - 段落数: {stats.get('paragraphs', 'N/A')}")
            print(f"     - 表格数: {stats.get('tables', 'N/A')}")
            print(f"     - 图像数: {stats.get('images', 'N/A')}")
            
            return data.get('report_task_id')
        else:
            print(f"❌ 报告生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("❌ 报告生成超时，请稍后再试")
        return None
    except Exception as e:
        print(f"❌ 报告生成出错: {str(e)}")
        return None

def download_report(report_task_id, output_dir="downloads"):
    """下载报告"""
    log_step("步骤4", f"下载综合分析报告到 {output_dir} 目录")
    
    # 确保下载目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/analysis/download-comprehensive-report/{report_task_id}",
            timeout=60
        )
        
        if response.status_code == 200:
            # 从响应头获取文件名
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"comprehensive_report_{report_task_id}.docx"
            
            # 保存文件
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / (1024 * 1024)  # MB
            print(f"✅ 报告下载成功")
            print(f"   文件路径: {output_path}")
            print(f"   文件大小: {file_size:.2f} MB")
            
            return output_path
        else:
            print(f"❌ 报告下载失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 下载过程出错: {str(e)}")
        return None

def main():
    """主函数"""
    print("🚀 开始真实的综合分析流程")
    print("=" * 60)
    
    # 检查服务器
    if not check_server():
        return
    
    # 文件路径
    data_file = "demo_data.csv"
    
    # 步骤1: 上传文件
    file_id = upload_file(data_file)
    if not file_id:
        print("❌ 上传失败，终止流程")
        return
    
    # 步骤2: 执行分析
    task_id = run_analysis(file_id)
    if not task_id:
        print("❌ 分析失败，终止流程")
        return
    
    # 步骤3: 生成综合报告
    report_task_id = generate_comprehensive_report(task_id)
    if not report_task_id:
        print("❌ 报告生成失败，终止流程")
        return
    
    # 步骤4: 下载报告
    report_path = download_report(report_task_id)
    if not report_path:
        print("❌ 报告下载失败")
        return
    
    # 流程完成
    log_step("完成", "综合分析流程成功完成")
    print("🎉 恭喜！所有步骤都已成功完成")
    print(f"📄 最终报告位置: {report_path}")
    print(f"📊 分析任务ID: {task_id}")
    print(f"📝 报告任务ID: {report_task_id}")
    
    # 验证文件
    if os.path.exists(report_path):
        size_mb = os.path.getsize(report_path) / (1024 * 1024)
        print(f"✅ 文件验证通过，大小: {size_mb:.2f} MB")
    else:
        print("❌ 文件验证失败，文件不存在")

if __name__ == "__main__":
    main() 