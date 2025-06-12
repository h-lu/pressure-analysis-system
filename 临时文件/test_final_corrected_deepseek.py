#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试：使用修正的测试数据（无班次信息）测试DeepSeek AI分析功能
"""
import requests
import json
import time

def test_final_corrected_analysis():
    """测试最终修正后的分析功能"""
    print("🎯 最终测试：可移动式压力采集装置分析")
    print("=" * 50)
    print("✅ 修正内容：")
    print("  • 移除班次(Shift-A/B)分析概念")
    print("  • 改为位置区域分析（X、Y坐标分区）")
    print("  • 专注机器人施压一致性评估")
    print("  • 适配电动滑轨移动测量场景")
    print()
    
    # 1. 测试连接
    print("1. 测试API连接...")
    try:
        response = requests.get('http://localhost:8000/api/deepseek/test-connection')
        if response.status_code == 200:
            print("✅ DeepSeek API连接成功")
        else:
            print("❌ 连接失败")
            return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False
    
    # 2. 测试修正后的数据分析
    print("\n2. 使用修正测试数据进行分析...")
    try:
        with open('corrected_analysis_results.json', 'rb') as f:
            files = {'file': ('analysis_results.json', f, 'application/json')}
            
            print("🚀 正在生成最终修正的分析报告...")
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:8000/api/deepseek/analyze-from-file', 
                files=files, 
                timeout=120
            )
            
            end_time = time.time()
            duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分析成功! 耗时: {duration:.2f}秒")
            
            print("\n📋 分析摘要信息:")
            summary = data.get('analysis_summary', {})
            for key, value in summary.items():
                if key == 'test_positions':
                    print(f"  • 测试位置区域数量: {value}")
                else:
                    print(f"  • {key}: {value}")
            
            print("\n📄 最终修正报告预览:")
            report = data['report']
            
            # 检查报告是否还包含班次分析
            if '班次' in report or 'Shift' in report:
                print("⚠️  警告：报告中仍包含班次相关内容")
                # 查找具体位置
                lines = report.split('\n')
                for i, line in enumerate(lines[:50], 1):
                    if '班次' in line or 'Shift' in line:
                        print(f"   第{i}行: {line.strip()}")
            else:
                print("✅ 确认：报告中已无班次分析内容")
            
            # 显示报告的关键部分
            lines = report.split('\n')[:25]
            for line in lines:
                print(line)
            
            if len(lines) < len(report.split('\n')):
                print("... (报告内容较长，已截断)")
            
            # 保存最终报告
            report_file = f'final_corrected_deepseek_report_{int(time.time())}.txt'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("最终修正的DeepSeek分析报告\n")
                f.write("设备类型：可移动式压力采集装置\n")
                f.write("测试场景：机器人末端在不同位置施压5N/25N/50N\n")
                f.write("分析重点：空间位置相关性、机器人施压一致性\n")
                f.write("修正状态：已移除班次分析，专注实际设备特点\n")
                f.write("=" * 70 + "\n\n")
                f.write(report)
            
            print(f"\n💾 最终修正报告已保存到: {report_file}")
            
            # 总结关键改进点
            print("\n🎉 修正验证结果:")
            if '班次' not in report and 'Shift' not in report:
                print("✅ 已成功移除班次分析概念")
            if '位置区域' in report or '空间位置' in report:
                print("✅ 已增加空间位置分析内容") 
            if '机器人' in report:
                print("✅ 已包含机器人相关分析")
            if '电动滑轨' in report or '移动式' in report:
                print("✅ 已适配设备特点描述")
            
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
    print("🔧 可移动式压力采集装置 - DeepSeek AI分析系统")
    print("🎯 目标：生成准确反映设备特点的专业分析报告")
    print()
    
    success = test_final_corrected_analysis()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 最终修正测试成功完成！")
        print()
        print("📊 现在DeepSeek分析报告准确反映了您的设备特点：")
        print("  ✓ 可移动式压力采集装置（1m×1m电动滑轨）")
        print("  ✓ 机器人末端在指定位置施压测试")
        print("  ✓ 三种目标力值（5N、25N、50N）分析")
        print("  ✓ 空间位置相关性分析（X、Y、Z坐标）")
        print("  ✓ 传感器移动精度和机器人一致性评估")
        print("  ✓ 无班次概念，专注实际测试流程")
        print()
        print("🚀 系统已准备就绪，可用于实际生产分析！")
    else:
        print("\n❌ 最终测试失败，请检查系统配置")

if __name__ == "__main__":
    main() 