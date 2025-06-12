#!/usr/bin/env python3
"""
测试新增分析功能的脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.r_analysis import RAnalysisEngine
from backend.models.schemas import AnalysisParams

def test_new_analysis_features():
    """测试新增的分析功能"""
    print("🧪 开始测试新增分析功能...")
    
    try:
        # 初始化引擎
        engine = RAnalysisEngine()
        print("✅ R分析引擎初始化成功")
        
        # 设置分析参数  
        params = AnalysisParams(
            file_id="test_file_001",
            target_forces=[5, 25, 50],
            tolerance_abs=2.0,
            tolerance_pct=5.0
        )
        print("✅ 分析参数设置成功")
        
        # 检查测试数据文件是否存在
        if not os.path.exists('test_data.csv'):
            print("❌ 测试数据文件不存在，请先生成测试数据")
            return False
            
        # 执行分析
        task_id = 'test_new_analysis_features'
        print(f"🔍 开始执行分析 (任务ID: {task_id})...")
        
        result = engine.analyze_data('test_data.csv', params, task_id)
        
        print("✅ 分析执行完成")
        print(f"📊 分析状态: {result.get('status')}")
        print(f"📈 图表数量: {len(result.get('charts', []))}")
        
        # 检查新增的分析功能
        print("\n🔍 检查新增分析功能:")
        
        # 1. 空间分析
        spatial_analysis = result.get('spatial_analysis')
        if spatial_analysis:
            print("✅ 空间分析 - 已添加")
            spatial_correlation = spatial_analysis.get('spatial_correlation')
            if spatial_correlation:
                print(f"  - 空间相关性: {len(spatial_correlation)} 组数据")
        else:
            print("❌ 空间分析 - 未找到")
        
        # 2. 误差分布分析  
        error_analysis = result.get('error_distribution_analysis')
        if error_analysis:
            print("✅ 误差分布分析 - 已添加")
            normality_tests = error_analysis.get('normality_tests')
            if normality_tests:
                print(f"  - 正态性检验: {len(normality_tests)} 组数据")
        else:
            print("❌ 误差分布分析 - 未找到")
        
        # 3. 多源变异分析
        multi_source_analysis = result.get('multi_source_variation_analysis')
        if multi_source_analysis:
            print("✅ 多源变异分析 - 已添加")
            performance_by_machine = multi_source_analysis.get('performance_by_machine')
            performance_by_shift = multi_source_analysis.get('performance_by_shift')
            if performance_by_machine:
                print(f"  - 机台性能分析: {len(performance_by_machine)} 组数据")
            if performance_by_shift:
                print(f"  - 班次性能分析: {len(performance_by_shift)} 组数据")
        else:
            print("❌ 多源变异分析 - 未找到")
        
        # 检查新增图表
        print("\n📊 检查新增图表:")
        charts = result.get('charts', [])
        new_chart_keywords = [
            'spatial_correlation', 'error_spatial_distribution', 
            'error_distribution_analysis', 'error_qq_plot',
            'machine_performance', 'shift_performance'
        ]
        
        found_new_charts = []
        for chart in charts:
            chart_id = chart.get('chart_id', '')
            for keyword in new_chart_keywords:
                if keyword in chart_id:
                    found_new_charts.append(chart['title'])
                    break
        
        if found_new_charts:
            print(f"✅ 发现新增图表 ({len(found_new_charts)} 个):")
            for chart_title in found_new_charts:
                print(f"  - {chart_title}")
        else:
            print("⚠️ 未找到新增图表")
        
        # 输出目录检查
        output_dir = Path(f"backend/outputs/{task_id}")
        if output_dir.exists():
            print(f"\n📁 输出文件:")
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    print(f"  - {file_path.name}")
        
        print(f"\n🎉 测试完成！新功能{'已成功集成' if all([spatial_analysis, error_analysis, multi_source_analysis]) else '部分集成'}")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_analysis_features()
    sys.exit(0 if success else 1) 