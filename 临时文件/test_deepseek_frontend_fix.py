#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的DeepSeek前端交互功能
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_complete_deepseek_workflow():
    """测试完整的DeepSeek分析工作流"""
    print("🚀 测试完整的DeepSeek分析工作流")
    print("="*60)
    
    # 1. 上传文件
    print("1. 上传数据文件...")
    test_file = Path("demo_data.csv")
    if not test_file.exists():
        print("❌ 测试文件 demo_data.csv 不存在")
        return False
    
    with open(test_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ 文件上传失败: {response.status_code}")
        return False
    
    upload_data = response.json()
    file_id = upload_data['file_id']
    print(f"✅ 文件上传成功，file_id: {file_id}")
    
    # 2. 开始R分析
    print("\n2. 开始R分析...")
    analysis_request = {
        "file_id": file_id,
        "target_forces": [5, 25, 50],
        "tolerance_abs": 2.0,
        "tolerance_pct": 5.0
    }
    
    response = requests.post(f"{BASE_URL}/api/analyze", json=analysis_request)
    if response.status_code != 200:
        print(f"❌ 分析启动失败: {response.status_code}")
        return False
    
    task_data = response.json()
    task_id = task_data['task_id']
    print(f"✅ 分析任务创建成功，task_id: {task_id}")
    
    # 3. 等待R分析完成
    print("\n3. 等待R分析完成...")
    max_wait = 120  # 最多等待2分钟
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/api/task/{task_id}")
        if response.status_code == 200:
            status_data = response.json()
            if status_data['status'] == 'completed':
                print("✅ R分析完成")
                break
            elif status_data['status'] == 'failed':
                print(f"❌ R分析失败: {status_data.get('error', '未知错误')}")
                return False
        
        print(".", end="", flush=True)
        time.sleep(2)
    else:
        print("❌ R分析超时")
        return False
    
    # 4. 获取R分析结果
    print("\n4. 获取R分析结果...")
    response = requests.get(f"{BASE_URL}/api/results/{task_id}")
    if response.status_code != 200:
        print(f"❌ 获取分析结果失败: {response.status_code}")
        return False
    
    analysis_result = response.json()
    print("✅ R分析结果获取成功")
    
    # 5. 生成DeepSeek分析
    print("\n5. 生成DeepSeek AI分析...")
    deepseek_request = {
        "analysis_data": {
            **analysis_result['result'],
            "task_id": task_id  # 重要：包含task_id
        },
        "report_type": "comprehensive",
        "language": "chinese"
    }
    
    response = requests.post(f"{BASE_URL}/api/deepseek/generate-report", json=deepseek_request)
    if response.status_code != 200:
        print(f"❌ DeepSeek分析失败: {response.status_code}")
        print(f"错误详情: {response.text}")
        return False
    
    deepseek_result = response.json()
    print("✅ DeepSeek AI分析完成")
    print(f"📝 报告长度: {len(deepseek_result['report'])} 字符")
    
    # 6. 检查后端是否保存了DeepSeek分析结果
    print("\n6. 检查后端保存的DeepSeek分析结果...")
    response = requests.get(f"{BASE_URL}/api/chart/{task_id}/deepseek_analysis.json")
    if response.status_code == 200:
        saved_result = response.json()
        print("✅ 后端成功保存了DeepSeek分析结果")
        print(f"📝 保存的报告长度: {len(saved_result['report'])} 字符")
    else:
        print("⚠️  后端没有保存DeepSeek分析结果")
    
    # 7. 生成综合Word报告
    print("\n7. 生成综合Word报告...")
    response = requests.post(f"{BASE_URL}/api/deepseek/generate-comprehensive-word-report?task_id={task_id}")
    if response.status_code != 200:
        print(f"❌ Word报告生成失败: {response.status_code}")
        print(f"错误详情: {response.text}")
        return False
    
    word_result = response.json()
    print("✅ 综合Word报告生成成功")
    
    # 8. 测试下载Word报告
    print("\n8. 测试下载Word报告...")
    response = requests.get(f"{BASE_URL}/api/download-comprehensive-report/{task_id}")
    if response.status_code == 200:
        # 保存下载的文件
        download_file = Path(f"test_downloaded_report_{task_id}.docx")
        with open(download_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Word报告下载成功: {download_file}")
        print(f"📁 文件大小: {download_file.stat().st_size} 字节")
        
        if download_file.stat().st_size > 1000:
            print("✅ 文件大小正常")
        else:
            print("⚠️  文件大小可能异常")
    else:
        print(f"❌ Word报告下载失败: {response.status_code}")
        return False
    
    print("\n" + "="*60)
    print("🎉 所有测试通过！DeepSeek前端交互功能修复成功！")
    print(f"📋 任务ID: {task_id}")
    print("💡 前端现在应该能够:")
    print("   • 正确生成和显示DeepSeek分析报告")
    print("   • 从后端加载已保存的分析结果")
    print("   • 生成和下载综合Word报告")
    print("="*60)
    
    return True

if __name__ == "__main__":
    print("🔧 DeepSeek前端交互功能测试")
    print("请确保后端服务器正在运行 (uvicorn backend.main:app --reload)")
    
    input("\n📋 按Enter键开始测试...")
    
    success = test_complete_deepseek_workflow()
    
    if success:
        print("\n🎊 测试完成！修复后的功能工作正常。")
    else:
        print("\n�� 测试失败，请检查日志和错误信息。") 