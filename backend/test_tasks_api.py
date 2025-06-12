#!/usr/bin/env python3
"""
测试任务列表API的问题
"""
import json
from pathlib import Path

def test_history_reading():
    try:
        print("=== 测试历史记录读取 ===")
        
        # 检查历史记录目录
        history_dir = Path("output/history")
        print(f"历史记录目录存在: {history_dir.exists()}")
        
        if not history_dir.exists():
            print("历史记录目录不存在，退出测试")
            return
        
        # 列出所有历史记录文件
        history_files = list(history_dir.glob("*.json"))
        print(f"找到历史记录文件数量: {len(history_files)}")
        
        for i, history_file in enumerate(history_files[:3]):  # 只处理前3个文件
            print(f"\n--- 处理文件 {i+1}: {history_file.name} ---")
            
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                task_id = history_data.get('id') or history_file.stem
                print(f"任务ID: {task_id}")
                print(f"日期: {history_data.get('date')}")
                print(f"名称: {history_data.get('name')}")
                
                # 检查对应的分析结果文件
                analysis_results_file = Path(f"output/charts/{task_id}/analysis_results.json")
                print(f"分析结果文件存在: {analysis_results_file.exists()}")
                
                if analysis_results_file.exists():
                    try:
                        with open(analysis_results_file, 'r', encoding='utf-8') as f:
                            analysis_data = json.load(f)
                        
                        if 'data_summary' in analysis_data:
                            # data_summary 是一个数组，取第一个元素
                            summary = analysis_data['data_summary'][0] if analysis_data['data_summary'] else {}
                            filename = summary.get('filename', 'demo_data.csv')  # 使用默认文件名
                            data_points = summary.get('总行数', summary.get('total_records', 0))
                            print(f"文件名: {filename}")
                            print(f"数据点: {data_points}")
                        else:
                            print("分析结果中没有data_summary")
                    except Exception as e:
                        print(f"读取分析结果失败: {e}")
                
            except Exception as e:
                print(f"处理历史记录文件失败: {e}")
                
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_history_reading() 