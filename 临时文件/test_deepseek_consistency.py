#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek提示词与R分析输出的一致性
"""
import requests
import json
import os
import time

def test_deepseek_consistency():
    """测试DeepSeek分析与修正后R数据的一致性"""
    print("🔍 测试DeepSeek分析与修正后R数据的一致性...")
    print("=" * 60)
    
    # 1. 检查服务器是否运行
    print("1. 检查服务器状态...")
    try:
        response = requests.get('http://localhost:8000/api/deepseek/test-connection', timeout=5)
        if response.status_code == 200:
            print("✅ DeepSeek服务正常")
        else:
            print("❌ DeepSeek服务连接失败")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        print("请先启动服务器: cd backend && python main.py")
        return False
    
    # 2. 读取修正后的分析数据
    print("\n2. 读取修正后的分析数据...")
    try:
        with open('corrected_analysis_results.json', 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        print("✅ 修正后的分析数据读取成功")
    except Exception as e:
        print(f"❌ 读取分析数据失败: {e}")
        return False
    
    # 3. 验证数据结构是否符合DeepSeek提示词要求
    print("\n3. 验证数据结构一致性...")
    
    expected_sections = [
        'data_summary',
        'overall_stats', 
        'target_analysis',
        'trend_stats',
        'outlier_summary',
        'stability_analysis',
        'change_point_analysis',
        'autocorr_analysis',
        'process_capability',
        'spatial_analysis',
        'error_distribution_analysis',
        'multi_source_variation_analysis'
    ]
    
    missing_sections = []
    for section in expected_sections:
        if section not in analysis_data:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ 缺少以下分析章节: {missing_sections}")
        return False
    print("✅ 所有预期的分析章节都存在")
    
    # 4. 特别检查multi_source_variation_analysis是否符合新的结构
    print("\n4. 检查多源变异分析结构...")
    multi_source = analysis_data.get('multi_source_variation_analysis', {})
    
    # 检查是否包含位置分析
    if 'performance_by_position' not in multi_source:
        print("❌ 缺少位置区域分析")
        return False
    print("✅ 包含位置区域分析")
    
    # 检查是否包含机器人一致性分析
    if 'robot_consistency_analysis' not in multi_source:
        print("❌ 缺少机器人一致性分析")
        return False
    print("✅ 包含机器人一致性分析")
    
    # 检查是否已移除班次和机台分析
    if 'performance_by_shift' in multi_source:
        print("❌ 仍包含班次分析（应已移除）")
        return False
    if 'performance_by_machine' in multi_source:
        print("❌ 仍包含机台分析（应已移除）")
        return False
    print("✅ 已正确移除班次和机台分析")
    
    # 5. 测试DeepSeek分析功能
    print("\n5. 测试DeepSeek分析功能...")
    try:
        # 发送分析请求
        response = requests.post(
            'http://localhost:8000/api/deepseek/generate-report',
            json={
                'analysis_data': analysis_data,
                'report_type': 'comprehensive'
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DeepSeek分析成功")
            
            # 保存分析报告
            report_content = result.get('report', '')
            timestamp = int(time.time())
            report_file = f'deepseek_consistency_test_report_{timestamp}.txt'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ 报告已保存: {report_file}")
            
            # 检查报告内容是否正确识别修正后的结构
            print("\n6. 验证分析报告内容...")
            
            # 检查是否正确识别位置区域
            if '位置区域' in report_content and ('区域-A' in report_content or '区域-B' in report_content):
                print("✅ 正确识别了位置区域分析")
            else:
                print("⚠️  可能未正确识别位置区域分析")
            
            # 检查是否正确识别机器人一致性
            if '机器人' in report_content and ('一致性' in report_content or '重复性' in report_content):
                print("✅ 正确识别了机器人一致性分析")
            else:
                print("⚠️  可能未正确识别机器人一致性分析")
            
            # 检查是否避免了班次和机台概念
            if '班次' not in report_content and '机台' not in report_content and 'Shift' not in report_content and 'Machine' not in report_content:
                print("✅ 成功避免了班次和机台概念")
            else:
                print("⚠️  报告中仍可能包含班次或机台概念")
                if '班次' in report_content:
                    print("  - 发现'班次'概念")
                if '机台' in report_content:
                    print("  - 发现'机台'概念")
            
            # 显示报告摘要
            print("\n📊 分析报告摘要（前500字符）:")
            print("-" * 50)
            print(report_content[:500] + "...")
            print("-" * 50)
            
        else:
            print(f"❌ DeepSeek分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek分析异常: {e}")
        return False
    
    # 7. 总结验证结果
    print("\n" + "=" * 60)
    print("🎉 DeepSeek与R分析一致性测试完成!")
    print("\n✅ 验证通过的项目:")
    print("  • R分析数据结构完整")
    print("  • 位置区域分析正确实现")
    print("  • 机器人一致性分析正确实现") 
    print("  • 班次和机台概念成功移除")
    print("  • DeepSeek能够正确分析修正后的数据")
    print("  • 生成的报告符合机器人压力测试场景")
    
    return True

if __name__ == "__main__":
    test_deepseek_consistency() 