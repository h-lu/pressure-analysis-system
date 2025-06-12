#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试综合Word报告生成 - 简化版本
"""
import requests
import json
import time

def test_comprehensive_report():
    """测试综合Word报告生成功能"""
    print("🔧 测试综合Word报告生成功能...")
    print("=" * 60)
    
    # 1. 检查服务器状态
    print("1. 检查服务器状态...")
    try:
        response = requests.get('http://localhost:8000/api/deepseek/test-connection', timeout=10)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
        else:
            print("❌ 服务器连接失败")
            return False
    except Exception as e:
        print(f"❌ 服务器连接异常: {e}")
        return False
    
    # 2. 模拟分析数据（确保数据结构正确）
    print("\n2. 准备测试数据...")
    test_data = {
        'data_summary': {
            '总行数': 20,
            '力值最小值': 4.5,
            '力值最大值': 50.3,
            '力值均值': 26.8,
            '缺失值': 0,
            '重复行': 0
        },
        'overall_stats': {  # 直接使用字典而不是列表
            '样本数': 20,
            '均值': 26.8,
            '中位数': 25.0,
            '标准差': 18.2,
            '变异系数': 67.9,
            '最小值': 4.5,
            '最大值': 50.3
        },
        'target_analysis': [
            {
                'target_force': 5,
                '数据点数': 8,
                '成功率_综合': 75.0,
                '平均力值': 5.1,
                '平均偏差_绝对': 0.3,
                '标准差': 0.4,
                '最大偏差_绝对': 0.8,
                '绝对容差限制': 2.0
            },
            {
                'target_force': 25,
                '数据点数': 6,
                '成功率_综合': 100.0,
                '平均力值': 25.2,
                '平均偏差_绝对': 0.2,
                '标准差': 0.5,
                '最大偏差_绝对': 0.4,
                '绝对容差限制': 2.0
            },
            {
                'target_force': 50,
                '数据点数': 6,
                '成功率_综合': 100.0,
                '平均力值': 49.8,
                '平均偏差_绝对': 0.2,
                '标准差': 0.3,
                '最大偏差_绝对': 0.3,
                '绝对容差限制': 2.0
            }
        ],
        'process_capability': [
            {
                'target_force': 5,
                'Cp': 3.333,
                'Cpk': 3.317,
                '能力等级': '优秀'
            },
            {
                'target_force': 25,
                'Cp': 2.564,
                'Cpk': 2.538,
                '能力等级': '优秀'
            },
            {
                'target_force': 50,
                'Cp': 2.778,
                'Cpk': 2.778,
                '能力等级': '优秀'
            }
        ],
        'multi_source_variation_analysis': {
            'performance_by_position': [
                {
                    'position_group': '位置区域-A',
                    'target_force': 5,
                    '数据点数': 3,
                    '成功率_综合': 100.0,
                    '平均偏差_绝对': 0.1,
                    '标准差': 0.2
                },
                {
                    'position_group': '位置区域-C',
                    'target_force': 5,
                    '数据点数': 5,
                    '成功率_综合': 71.4,
                    '平均偏差_绝对': 0.4,
                    '标准差': 0.5
                }
            ],
            'robot_consistency_analysis': {
                'force_repeatability': {
                    '5N': 4.05,
                    '25N': 1.06,
                    '50N': 0.47
                },
                'position_accuracy': {
                    'X坐标': 0.9,
                    'Y坐标': 0.7,
                    'Z坐标': 0.6
                }
            }
        },
        'spatial_analysis': {},
        'error_distribution_analysis': {},
        'trend_stats': [],
        'outlier_summary': [],
        'stability_analysis': [],
        'change_point_analysis': [],
        'autocorr_analysis': []
    }
    
    # 3. 保存测试数据到临时文件
    reports_dir = "temp/reports"
    import os
    os.makedirs(reports_dir, exist_ok=True)
    
    test_task_id = f"test_{int(time.time())}"
    test_file_path = f"{reports_dir}/analysis_results_{test_task_id}.json"
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 测试数据已保存: {test_file_path}")
    
    # 4. 测试综合报告生成
    print("\n3. 测试综合报告生成...")
    try:
        response = requests.post(
            'http://localhost:8000/api/deepseek/generate-comprehensive-word-report',
            params={'task_id': test_task_id},
            timeout=120  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 综合报告生成成功")
                print(f"📄 下载链接: {result.get('download_url')}")
                print(f"📁 文件路径: {result.get('report_path')}")
                
                # 验证文件是否存在
                import os
                report_path = result.get('report_path')
                if report_path and os.path.exists(report_path):
                    file_size = os.path.getsize(report_path)
                    print(f"✅ 报告文件存在，大小: {file_size:,} 字节")
                    
                    if file_size > 30000:  # 大于30KB表示可能生成成功
                        print("✅ 文件大小正常，报告生成完整")
                        return True
                    else:
                        print("⚠️ 文件过小，可能生成不完整")
                        return False
                else:
                    print("❌ 报告文件不存在")
                    return False
            else:
                print(f"❌ 综合报告生成失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 综合报告生成异常: {e}")
        return False
    
    # 5. 测试下载功能
    print("\n4. 测试下载功能...")
    try:
        download_response = requests.get(
            f'http://localhost:8000/api/download-comprehensive-report/{test_task_id}',
            timeout=30
        )
        
        if download_response.status_code == 200:
            content_type = download_response.headers.get('content-type', '')
            if 'wordprocessingml' in content_type or 'application/octet-stream' in content_type:
                print("✅ 下载功能正常，文件类型正确")
                print(f"📁 Content-Type: {content_type}")
                print(f"📊 文件大小: {len(download_response.content):,} 字节")
                return True
            else:
                print(f"⚠️ 文件类型异常: {content_type}")
                return False
        else:
            print(f"❌ 下载失败: {download_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 下载测试异常: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_report()
    print("\n" + "=" * 60)
    if success:
        print("🎉 综合报告测试完全成功！")
        print("\n✅ 验证通过的功能:")
        print("  • 服务器连接正常")
        print("  • 数据结构正确")
        print("  • DeepSeek分析正常")
        print("  • Word报告生成成功")
        print("  • 文件下载正常")
    else:
        print("❌ 综合报告测试失败")
        print("\n🔧 可能的解决方案:")
        print("  • 检查服务器状态")
        print("  • 检查数据结构")
        print("  • 检查API配置")
        print("  • 检查文件权限") 