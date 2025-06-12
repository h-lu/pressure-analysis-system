#!/usr/bin/env python3
"""
生成综合Word报告的脚本
"""

import requests
import json

def generate_word_report():
    """生成Word报告"""
    
    # 报告参数
    report_data = {
        "task_id": "4514bcbf-1459-409c-8e17-710e6b73ab31",
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
    
    print("🚀 开始生成综合Word报告...")
    print(f"📊 分析任务ID: {report_data['task_id']}")
    
    try:
        response = requests.post(
            f"http://localhost:8000/api/deepseek/generate-comprehensive-word-report?task_id={report_data['task_id']}",
            timeout=600  # 10分钟超时
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 综合报告生成成功")
            print(f"   下载URL: {data.get('download_url')}")
            print(f"   Word文件路径: {data.get('report_path')}")
            
            # 显示分析摘要
            summary = data.get('analysis_summary', {})
            print(f"   分析摘要:")
            print(f"     - 总样本数: {summary.get('total_samples', 'N/A')}")
            print(f"     - 平均力值: {summary.get('mean_force', 'N/A')} N")
            print(f"     - 变异系数: {summary.get('cv_percent', 'N/A')}%")
            print(f"     - 整体成功率: {summary.get('overall_success_rate', 'N/A')}%")
            print(f"     - 平均Cp: {summary.get('average_cp', 'N/A')}")
            print(f"     - 平均Cpk: {summary.get('average_cpk', 'N/A')}")
            
            # 返回任务ID用于下载
            return report_data['task_id']
        else:
            print(f"❌ 报告生成失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 生成报告时出错: {str(e)}")
        return None

def download_report(report_task_id):
    """下载报告"""
    import os
    
    print(f"\n📥 开始下载报告...")
    print(f"   报告任务ID: {report_task_id}")
    
    # 确保下载目录存在
    os.makedirs("downloads", exist_ok=True)
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/download-comprehensive-report/{report_task_id}",
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
            output_path = os.path.join("downloads", filename)
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

if __name__ == "__main__":
    # 生成报告
    report_task_id = generate_word_report()
    
    if report_task_id:
        # 下载报告
        report_path = download_report(report_task_id)
        
        if report_path:
            print(f"\n🎉 流程完成！")
            print(f"📄 最终报告位置: {report_path}")
        else:
            print(f"\n❌ 下载失败")
    else:
        print(f"\n❌ 生成失败") 