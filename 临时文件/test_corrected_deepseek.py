#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修正后的DeepSeek AI分析功能
"""
import requests
import json
import time

def test_corrected_analysis():
    """测试修正后的分析功能"""
    print("🔍 测试修正后的DeepSeek分析功能...")
    
    # 1. 测试连接
    print("1. 测试连接...")
    try:
        response = requests.get('http://localhost:8000/api/deepseek/test-connection')
        if response.status_code == 200:
            print("✅ 连接成功")
        else:
            print("❌ 连接失败")
            return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False
    
    # 2. 测试文件分析（使用修正后的提示词）
    print("\n2. 测试修正后的分析报告...")
    try:
        with open('backend/static/charts/test_new_analysis_features/analysis_results.json', 'rb') as f:
            files = {'file': ('analysis_results.json', f, 'application/json')}
            
            print("🚀 正在生成修正后的分析报告...")
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:8000/api/deepseek/analyze-from-file', 
                files=files, 
                timeout=120  # 增加到2分钟
            )
            
            end_time = time.time()
            duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分析成功! 耗时: {duration:.2f}秒")
            
            print("\n📋 分析摘要:")
            summary = data.get('analysis_summary', {})
            for key, value in summary.items():
                print(f"  • {key}: {value}")
            
            print("\n📄 修正后的报告预览:")
            report = data['report']
            # 显示报告的前几行
            lines = report.split('\n')[:20]
            for line in lines:
                print(line)
            
            if len(lines) < len(report.split('\n')):
                print("... (报告内容较长，已截断)")
            
            # 保存完整报告
            report_file = f'corrected_deepseek_report_{int(time.time())}.txt'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("修正后的DeepSeek分析报告\n")
                f.write("设备：可移动式压力采集装置\n") 
                f.write("修正内容：移除班次分析，专注于位置和机器人施压分析\n")
                f.write("=" * 60 + "\n\n")
                f.write(report)
            
            print(f"\n💾 完整的修正报告已保存到: {report_file}")
            
            return True
        else:
            print("❌ 分析失败")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 分析异常: {e}")
        return False

def main():
    """主函数"""
    print("🎯 测试修正后的DeepSeek分析功能")
    print("修正内容：")
    print("  ✓ 移除了A班B班的概念")
    print("  ✓ 更新为可移动式压力采集装置场景")
    print("  ✓ 专注于空间位置和机器人施压分析")
    print("  ✓ 适配实际的测试流程")
    print()
    
    success = test_corrected_analysis()
    
    if success:
        print("\n🎉 修正测试完成！")
        print("现在的分析报告更加准确地反映了您的设备特点：")
        print("  • 可移动式压力采集装置")
        print("  • 机器人末端施压测试")
        print("  • 空间位置相关分析")
        print("  • 无班次概念")
    else:
        print("\n❌ 修正测试失败，请检查服务器状态")

if __name__ == "__main__":
    main() 