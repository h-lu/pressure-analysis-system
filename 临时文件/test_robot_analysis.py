#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的R脚本 - 生成适配机器人压力测试的JSON
"""
import subprocess
import json
import os
import time

def test_robot_analysis():
    """测试修改后的R分析脚本"""
    print("🤖 测试可移动式压力采集装置分析...")
    print("=" * 60)
    
    # 1. 运行修改后的R脚本
    print("1. 运行修改后的R分析脚本...")
    try:
        # 切换到R脚本目录
        os.chdir('backend/r_analysis')
        
        # 运行R脚本
        result = subprocess.run([
            'Rscript', 'pressure_analysis.R', 
            '--input', 'demo_data.csv',
            '--output', 'robot_test_output'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ R脚本执行成功")
            print("📊 R脚本输出:")
            print(result.stdout[-1000:])  # 显示最后1000字符
        else:
            print("❌ R脚本执行失败")
            print("错误信息:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ R脚本执行超时")
        return False
    except Exception as e:
        print(f"❌ R脚本执行异常: {e}")
        return False
    
    # 2. 检查生成的JSON文件
    print("\n2. 检查生成的分析结果JSON...")
    json_path = 'output/analysis_results.json'
    
    if not os.path.exists(json_path):
        print(f"❌ JSON文件不存在: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        print("✅ JSON文件读取成功")
    except Exception as e:
        print(f"❌ JSON文件读取失败: {e}")
        return False
    
    # 3. 验证JSON结构是否符合机器人压力测试要求
    print("\n3. 验证JSON结构...")
    
    # 检查基础结构
    required_keys = [
        'data_summary', 'overall_stats', 'target_analysis',
        'trend_stats', 'outlier_summary', 'stability_analysis',
        'change_point_analysis', 'autocorr_analysis', 'process_capability',
        'spatial_analysis', 'error_distribution_analysis',
        'multi_source_variation_analysis', 'summary'
    ]
    
    missing_keys = [key for key in required_keys if key not in analysis_data]
    if missing_keys:
        print(f"❌ 缺少必需字段: {missing_keys}")
        return False
    print("✅ 基础结构完整")
    
    # 检查多源变异分析是否正确修改
    multi_source = analysis_data.get('multi_source_variation_analysis', {})
    
    # 验证已移除班次分析
    if 'performance_by_shift' in multi_source:
        print("❌ 仍包含班次分析数据")
        return False
    print("✅ 已成功移除班次分析")
    
    # 验证已移除机台分析 
    if 'performance_by_machine' in multi_source:
        print("❌ 仍包含机台分析数据")
        return False
    print("✅ 已成功移除机台分析")
    
    # 验证已添加位置区域分析
    if 'performance_by_position' not in multi_source:
        print("❌ 缺少位置区域分析")
        return False
    print("✅ 已添加位置区域分析")
    
    # 验证已添加机器人一致性分析
    if 'robot_consistency_analysis' not in multi_source:
        print("❌ 缺少机器人一致性分析")
        return False
    print("✅ 已添加机器人一致性分析")
    
    # 4. 显示关键分析结果
    print("\n4. 关键分析结果预览:")
    print(f"📊 总数据点: {analysis_data['summary']['total_records']}")
    print(f"📊 整体成功率: {analysis_data['summary']['success_rate']}%")
    
    # 显示位置区域分析
    position_analysis = multi_source.get('performance_by_position')
    if position_analysis:
        print("\n📍 位置区域分析:")
        for item in position_analysis[:6]:  # 显示前6个
            print(f"  {item['position_group']} - 目标{item['target_force']}N: "
                  f"成功率{item['成功率']}%, 数据点{item['数据点数']}个")
    
    # 显示机器人一致性分析
    robot_analysis = multi_source.get('robot_consistency_analysis')
    if robot_analysis:
        print("\n🤖 机器人一致性分析:")
        if 'force_repeatability' in robot_analysis:
            print("  力控重复性:")
            force_rep = robot_analysis['force_repeatability']
            if isinstance(force_rep, dict):
                for force, cv in force_rep.items():
                    print(f"    {force}: {cv}%")
            else:
                print(f"    {force_rep}")
        if 'position_accuracy' in robot_analysis:
            pos_acc = robot_analysis['position_accuracy']
            print(f"  位置精度: X±{pos_acc['x_std']}mm, Y±{pos_acc['y_std']}mm, Z±{pos_acc['z_std']}mm")
    
    # 5. 保存为标准化JSON文件
    print("\n5. 保存标准化JSON文件...")
    try:
        output_path = '../../robot_pressure_analysis_results.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存至: {output_path}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    
    # 6. 检查生成的图表文件
    print("\n6. 检查生成的图表文件...")
    expected_images = [
        'position_performance_comparison.png',
        'robot_consistency_analysis.png'
    ]
    
    output_dir = 'output'
    for img in expected_images:
        img_path = os.path.join(output_dir, img)
        if os.path.exists(img_path):
            print(f"✅ {img}")
        else:
            print(f"⚠️  {img} - 未生成")
    
    print("\n" + "=" * 60)
    print("🎉 可移动式压力采集装置分析测试完成!")
    print("\n📋 修改总结:")
    print("  ✅ 移除了班次(Shift-A/B)分析概念")
    print("  ✅ 移除了机台(Machine-01~04)分析概念")
    print("  ✅ 增加了位置区域(A/B/C/D)分析")
    print("  ✅ 增加了机器人施压一致性分析")
    print("  ✅ 适配了电动滑轨移动测量场景")
    print("  ✅ 生成了机器人压力测试专用JSON格式")
    
    return True

if __name__ == "__main__":
    test_robot_analysis() 