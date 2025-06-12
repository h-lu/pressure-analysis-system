#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek AI分析报告功能
"""
import requests
import json
import time
import os
from pathlib import Path

def test_deepseek_connection():
    """测试DeepSeek API连接"""
    print("=" * 60)
    print("🔍 测试DeepSeek API连接...")
    
    try:
        response = requests.get("http://localhost:8000/api/deepseek/test-connection")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 连接测试成功!")
            print(f"📝 响应: {result['response']}")
            return True
        else:
            print(f"❌ 连接测试失败! 状态码: {response.status_code}")
            print(f"📝 错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试异常: {str(e)}")
        return False

def test_generate_report_from_data():
    """测试从数据生成报告"""
    print("=" * 60)
    print("📊 测试从数据生成分析报告...")
    
    # 读取测试数据
    analysis_file = Path("backend/static/charts/test_new_analysis_features/analysis_results.json")
    
    if not analysis_file.exists():
        print(f"❌ 测试数据文件不存在: {analysis_file}")
        return False
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # 准备请求数据
        request_data = {
            "analysis_data": analysis_data,
            "report_type": "comprehensive",
            "language": "chinese"
        }
        
        print("🚀 正在生成分析报告...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/api/deepseek/generate-report",
            json=request_data,
            timeout=60  # 60秒超时
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 报告生成成功! 耗时: {duration:.2f}秒")
            print("=" * 60)
            print("📋 分析摘要:")
            summary = result.get('analysis_summary', {})
            for key, value in summary.items():
                print(f"  • {key}: {value}")
            
            print("\n" + "=" * 60)
            print("📄 完整报告:")
            print(result['report'])
            
            # 保存报告到文件
            report_file = f"deepseek_analysis_report_{int(time.time())}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(result['report'])
            print(f"\n💾 报告已保存到: {report_file}")
            
            return True
        else:
            print(f"❌ 报告生成失败! 状态码: {response.status_code}")
            print(f"📝 错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 生成报告异常: {str(e)}")
        return False

def test_upload_file_analysis():
    """测试文件上传分析"""
    print("=" * 60)
    print("📂 测试文件上传分析...")
    
    analysis_file = Path("backend/static/charts/test_new_analysis_features/analysis_results.json")
    
    if not analysis_file.exists():
        print(f"❌ 测试文件不存在: {analysis_file}")
        return False
    
    try:
        with open(analysis_file, 'rb') as f:
            files = {'file': ('analysis_results.json', f, 'application/json')}
            
            print("🚀 正在上传文件并生成报告...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/api/deepseek/analyze-from-file",
                files=files,
                timeout=60
            )
            
            end_time = time.time()
            duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文件分析成功! 耗时: {duration:.2f}秒")
            print("=" * 60)
            print("📋 分析摘要:")
            summary = result.get('analysis_summary', {})
            for key, value in summary.items():
                print(f"  • {key}: {value}")
            
            # 保存简略版报告
            report_file = f"deepseek_file_analysis_report_{int(time.time())}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(result['report'])
            print(f"\n💾 报告已保存到: {report_file}")
            
            return True
        else:
            print(f"❌ 文件分析失败! 状态码: {response.status_code}")
            print(f"📝 错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 文件分析异常: {str(e)}")
        return False

def test_different_report_types():
    """测试不同类型的报告"""
    print("=" * 60)
    print("📊 测试不同类型的分析报告...")
    
    analysis_file = Path("backend/static/charts/test_new_analysis_features/analysis_results.json")
    
    if not analysis_file.exists():
        print(f"❌ 测试数据文件不存在: {analysis_file}")
        return False
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        report_types = ["summary", "technical", "comprehensive"]
        
        for report_type in report_types:
            print(f"\n🔄 生成 {report_type} 类型报告...")
            
            request_data = {
                "analysis_data": analysis_data,
                "report_type": report_type,
                "language": "chinese"
            }
            
            response = requests.post(
                "http://localhost:8000/api/deepseek/generate-report",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {report_type} 报告生成成功!")
                
                # 保存报告
                report_file = f"deepseek_report_{report_type}_{int(time.time())}.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(f"报告类型: {report_type}\n")
                    f.write("=" * 50 + "\n")
                    f.write(result['report'])
                print(f"💾 {report_type} 报告已保存到: {report_file}")
            else:
                print(f"❌ {report_type} 报告生成失败! 状态码: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成不同类型报告异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始DeepSeek AI分析报告功能测试")
    print("请确保后端服务器正在运行 (python run_server.py)")
    
    # 等待用户确认服务器运行
    input("\n📋 按Enter键开始测试...")
    
    test_results = []
    
    # 1. 测试连接
    result1 = test_deepseek_connection()
    test_results.append(("连接测试", result1))
    
    if not result1:
        print("❌ 连接测试失败，停止后续测试")
        return
    
    # 2. 测试数据生成报告
    result2 = test_generate_report_from_data()
    test_results.append(("数据报告生成", result2))
    
    # 3. 测试文件上传分析
    result3 = test_upload_file_analysis()
    test_results.append(("文件上传分析", result3))
    
    # 4. 测试不同类型报告
    result4 = test_different_report_types()
    test_results.append(("不同类型报告", result4))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in test_results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  • {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 总体成功率: {success_count}/{len(test_results)} ({success_count/len(test_results)*100:.1f}%)")
    
    if success_count == len(test_results):
        print("🎉 所有测试通过! DeepSeek AI分析报告功能正常工作!")
    else:
        print("⚠️  部分测试失败，请检查日志和错误信息")

if __name__ == "__main__":
    main() 