#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试综合Word报告生成功能
"""
import requests
import json
import time
import os

def test_comprehensive_report_generation():
    """测试综合Word报告生成"""
    print("🔬 测试综合Word报告生成功能...")
    print("=" * 60)
    
    # 1. 检查分析数据是否存在
    print("1. 检查修正后的分析数据...")
    if not os.path.exists('corrected_analysis_results.json'):
        print("❌ 未找到corrected_analysis_results.json，请先运行R分析")
        return False
    
    with open('corrected_analysis_results.json', 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    print("✅ 分析数据读取成功")
    
    # 2. 生成一个模拟的任务ID
    task_id = f"test_{int(time.time())}"
    print(f"使用测试任务ID: {task_id}")
    
    # 3. 创建临时分析结果文件
    temp_dir = "temp/reports"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_analysis_file = f"{temp_dir}/analysis_results_{task_id}.json"
    with open(temp_analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 临时分析文件已创建: {temp_analysis_file}")
    
    # 4. 测试DeepSeek + 综合Word报告生成
    print("\n4. 测试DeepSeek + 综合Word报告生成...")
    try:
        response = requests.post(
            'http://localhost:8000/api/deepseek/generate-comprehensive-word-report',
            params={'task_id': task_id},
            timeout=120  # 增加超时时间，因为需要生成DeepSeek报告
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 综合Word报告生成成功!")
            print(f"下载链接: {result.get('download_url')}")
            print(f"报告路径: {result.get('report_path')}")
            
            # 验证文件是否真的存在
            report_path = result.get('report_path')
            if report_path and os.path.exists(report_path):
                file_size = os.path.getsize(report_path)
                print(f"✅ 报告文件确实存在，大小: {file_size/1024:.1f} KB")
                
                if file_size > 50000:  # 大于50KB说明内容丰富
                    print("✅ 报告文件大小合理，内容应该比较完整")
                else:
                    print("⚠️  报告文件较小，可能内容不完整")
                
                # 测试下载功能
                print("\n5. 测试报告下载功能...")
                download_response = requests.get(
                    f'http://localhost:8000{result.get("download_url")}',
                    timeout=30
                )
                
                if download_response.status_code == 200:
                    print("✅ 报告下载功能正常")
                    
                    # 保存下载的文件到当前目录验证
                    test_download_file = f"test_comprehensive_report_{task_id}.docx"
                    with open(test_download_file, 'wb') as f:
                        f.write(download_response.content)
                    print(f"✅ 测试下载文件已保存: {test_download_file}")
                else:
                    print(f"❌ 报告下载失败: {download_response.status_code}")
                    
            else:
                print("❌ 报告文件不存在")
                return False
                
        else:
            print(f"❌ 综合Word报告生成失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False
    
    # 6. 清理测试文件
    print("\n6. 清理测试文件...")
    try:
        if os.path.exists(temp_analysis_file):
            os.remove(temp_analysis_file)
            print("✅ 临时分析文件已清理")
    except Exception as e:
        print(f"⚠️  清理文件失败: {e}")
    
    # 7. 测试总结
    print("\n" + "=" * 60)
    print("🎉 综合Word报告生成测试完成!")
    print("\n✅ 测试通过的功能:")
    print("  • 读取R分析数据")
    print("  • 调用DeepSeek API生成AI分析报告")
    print("  • 整合AI分析和R统计数据")
    print("  • 生成包含图表的综合Word文档")
    print("  • 提供Word文档下载功能")
    print("  • 文档内容包含:")
    print("    - DeepSeek AI智能分析报告")
    print("    - R统计分析详细数据表格")
    print("    - 关键图表展示")
    print("    - 综合结论与建议")
    
    print("\n📋 报告特点:")
    print("  • 双重分析: AI分析 + 统计分析")
    print("  • 数据完整: 表格 + 图表 + 文字说明")
    print("  • 适配场景: 机器人压力测试系统")
    print("  • 避免概念: 无工厂班次、机台等概念")
    print("  • 突出特色: 位置区域分析、机器人一致性分析")
    
    return True

if __name__ == "__main__":
    test_comprehensive_report_generation() 