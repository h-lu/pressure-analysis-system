"""
压力数据分析系统 - Streamlit版本
更简单的Web界面实现，快速原型开发
"""

import streamlit as st
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
import os
import tempfile
import zipfile
from io import BytesIO
import logging

# 页面配置
st.set_page_config(
    page_title="压力数据分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None

@st.cache_resource
def initialize_r_environment():
    """初始化R环境（缓存）"""
    try:
        pandas2ri.activate()
        r = robjects.r
        
        # 加载必要的R包
        r('library(tidyverse)')
        r('library(ggplot2)')
        r('library(plotly)')
        
        st.success("✅ R环境初始化成功")
        return r
    except Exception as e:
        st.error(f"❌ R环境初始化失败: {e}")
        return None

def analyze_with_r(csv_file, target_forces, tolerance_abs, tolerance_pct):
    """使用R进行数据分析"""
    try:
        r = initialize_r_environment()
        if r is None:
            return None
        
        # 保存上传的文件到临时位置
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(csv_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # 设置R变量
        r.assign('data_file', tmp_file_path)
        r.assign('target_forces', robjects.FloatVector(target_forces))
        r.assign('tolerance_abs', tolerance_abs)
        r.assign('tolerance_pct', tolerance_pct)
        
        # 创建临时输出目录
        output_dir = tempfile.mkdtemp()
        r.assign('output_dir', output_dir)
        
        # 执行R分析脚本
        with st.spinner('正在执行分析...'):
            r('source("pressure_analysis_simple.R")')
        
        # 提取结果
        results = extract_r_results(r, output_dir)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return results
        
    except Exception as e:
        st.error(f"分析失败: {e}")
        return None

def extract_r_results(r, output_dir):
    """从R环境中提取分析结果"""
    try:
        # 获取基础统计信息
        total_points = int(r('nrow(data)')[0])
        force_mean = float(r('mean(data$force_numeric)')[0])
        force_std = float(r('sd(data$force_numeric)')[0])
        force_min = float(r('min(data$force_numeric)')[0])
        force_max = float(r('max(data$force_numeric)')[0])
        cv = (force_std / force_mean) * 100
        
        # 查找生成的图表文件
        chart_files = []
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                if filename.endswith('.png'):
                    chart_files.append(os.path.join(output_dir, filename))
        
        results = {
            'statistics': {
                'total_points': total_points,
                'force_mean': force_mean,
                'force_std': force_std,
                'force_min': force_min,
                'force_max': force_max,
                'cv': cv
            },
            'chart_files': chart_files,
            'output_dir': output_dir
        }
        
        return results
        
    except Exception as e:
        st.error(f"结果提取失败: {e}")
        return None

def main():
    """主应用程序"""
    
    # 主标题
    st.markdown('<h1 class="main-header">🔧 压力采集数据分析系统</h1>', unsafe_allow_html=True)
    
    # 侧边栏 - 参数配置
    st.sidebar.header("📊 分析参数配置")
    
    # 文件上传
    uploaded_file = st.sidebar.file_uploader(
        "上传CSV数据文件",
        type=['csv'],
        help="支持格式：序号,X,Y,Z,力值"
    )
    
    # 分析参数
    st.sidebar.subheader("参数设置")
    
    target_forces_str = st.sidebar.text_input(
        "目标力值 (N)",
        value="5,25,50",
        help="用逗号分隔多个目标值"
    )
    
    tolerance_abs = st.sidebar.number_input(
        "绝对容差 (N)",
        value=2.0,
        min_value=0.1,
        step=0.1,
        help="允许的绝对偏差范围"
    )
    
    tolerance_pct = st.sidebar.number_input(
        "百分比容差 (%)",
        value=5.0,
        min_value=0.1,
        step=0.1,
        help="允许的百分比偏差范围"
    )
    
    # 解析目标力值
    try:
        target_forces = [float(x.strip()) for x in target_forces_str.split(',')]
    except:
        st.sidebar.error("目标力值格式错误，请用逗号分隔数字")
        target_forces = [5, 25, 50]
    
    # 主内容区域
    if uploaded_file is not None:
        # 显示文件信息
        st.subheader("📁 数据文件信息")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("文件名", uploaded_file.name)
        with col2:
            st.metric("文件大小", f"{len(uploaded_file.getvalue())/1024:.1f} KB")
        with col3:
            st.metric("文件类型", uploaded_file.type)
        
        # 预览数据
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("📋 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总行数", len(df))
            with col2:
                st.metric("列数", len(df.columns))
            with col3:
                st.metric("预期列", "序号,X,Y,Z,力值")
            
        except Exception as e:
            st.error(f"数据预览失败: {e}")
            return
        
        # 分析按钮
        st.subheader("🚀 开始分析")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 执行完整分析", type="primary", use_container_width=True):
                # 重置文件指针
                uploaded_file.seek(0)
                
                # 执行分析
                results = analyze_with_r(uploaded_file, target_forces, tolerance_abs, tolerance_pct)
                
                if results:
                    st.session_state.results = results
                    st.session_state.analysis_complete = True
                    st.success("✅ 分析完成！")
                    st.rerun()
        
        # 显示分析结果
        if st.session_state.analysis_complete and st.session_state.results:
            display_results(st.session_state.results)
    
    else:
        # 欢迎页面
        st.subheader("👋 欢迎使用压力数据分析系统")
        
        st.markdown("""
        ### 🎯 系统功能
        - **数据分析**: 29个专业统计图表
        - **质量控制**: SPC控制图和过程能力分析  
        - **异常检测**: 自动识别异常值和趋势
        - **报告生成**: 专业的分析报告和图表
        
        ### 📝 使用步骤
        1. 在左侧上传CSV数据文件
        2. 配置分析参数（目标力值、容差等）
        3. 点击"执行完整分析"按钮
        4. 查看分析结果和下载报告
        
        ### 📊 数据格式要求
        CSV文件必须包含以下列：
        - **序号**: 数据点编号
        - **X**: X坐标位置
        - **Y**: Y坐标位置  
        - **Z**: Z坐标位置
        - **力值**: 测量的力值（支持单位如"3.6N"）
        """)
        
        # 示例数据格式
        st.subheader("📋 数据格式示例")
        example_data = pd.DataFrame({
            '序号': [1, 2, 3, 4, 5],
            'X': [97.2, 98.8, 107.8, 99.1, 102.3],
            'Y': [96.4, 101.3, 98.8, 95.7, 100.2],
            'Z': [111, 106.6, 98.7, 103.2, 108.9],
            '力值': ['3.6N', '23.5N', '48.1N', '25.8N', '49.7N']
        })
        st.dataframe(example_data, use_container_width=True)

def display_results(results):
    """显示分析结果"""
    st.subheader("📊 分析结果")
    
    # 统计摘要
    stats = results['statistics']
    
    st.markdown("### 📈 统计摘要")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("数据点数", f"{stats['total_points']:,}")
    with col2:
        st.metric("平均力值", f"{stats['force_mean']:.2f} N")
    with col3:
        st.metric("标准差", f"{stats['force_std']:.2f} N")
    with col4:
        st.metric("力值范围", f"{stats['force_min']:.1f} - {stats['force_max']:.1f} N")
    with col5:
        st.metric("变异系数", f"{stats['cv']:.2f}%")
    
    # 质量评估
    st.markdown("### 🎯 质量评估")
    
    cv = stats['cv']
    if cv < 10:
        st.markdown('<div class="success-box">✅ 系统稳定性：优秀 (变异系数 < 10%)</div>', unsafe_allow_html=True)
    elif cv < 20:
        st.markdown('<div class="warning-box">⚠️ 系统稳定性：良好 (变异系数 10-20%)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">❌ 系统稳定性：需要关注 (变异系数 > 20%)</div>', unsafe_allow_html=True)
    
    # 图表展示
    chart_files = results.get('chart_files', [])
    if chart_files:
        st.markdown("### 📊 分析图表")
        
        chart_titles = [
            "力值时间序列图", "力值分布直方图", "力值箱线图",
            "绝对偏差箱线图", "百分比偏差箱线图", "误差散点图",
            "X值控制图", "Y值控制图", "Z值控制图", "力值控制图",
            "移动极差控制图", "EWMA控制图", "力值vs位置散点图",
            "3D散点图", "相关性热图", "多变量箱线图",
            "力值密度图", "累积分布图", "QQ正态性图",
            "力值趋势图", "滑动平均图", "变化点检测图",
            "游程检验图", "自相关图", "时间序列分解图",
            "Cp和Cpk图", "公差带图", "过程能力直方图", "综合控制图"
        ]
        
        # 分页显示图表
        charts_per_page = 6
        total_charts = len(chart_files)
        total_pages = (total_charts + charts_per_page - 1) // charts_per_page
        
        if total_pages > 1:
            page = st.selectbox("选择图表页面", range(1, total_pages + 1), key="chart_page")
            start_idx = (page - 1) * charts_per_page
            end_idx = min(start_idx + charts_per_page, total_charts)
            display_charts = chart_files[start_idx:end_idx]
            display_titles = chart_titles[start_idx:end_idx]
        else:
            display_charts = chart_files
            display_titles = chart_titles[:len(chart_files)]
        
        # 显示图表
        cols = st.columns(2)
        for i, (chart_file, title) in enumerate(zip(display_charts, display_titles)):
            with cols[i % 2]:
                if os.path.exists(chart_file):
                    st.subheader(f"📊 {title}")
                    st.image(chart_file, use_column_width=True)
                else:
                    st.warning(f"图表文件不存在: {chart_file}")
    
    # 下载选项
    st.markdown("### 💾 下载结果")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 下载分析报告", use_container_width=True):
            # 生成报告
            report = generate_report(results)
            st.download_button(
                label="下载PDF报告",
                data=report,
                file_name="pressure_analysis_report.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("📊 下载所有图表", use_container_width=True):
            # 打包图表
            if chart_files:
                zip_buffer = create_charts_zip(chart_files)
                st.download_button(
                    label="下载图表ZIP",
                    data=zip_buffer,
                    file_name="pressure_analysis_charts.zip",
                    mime="application/zip"
                )
    
    with col3:
        if st.button("📋 下载数据", use_container_width=True):
            # 下载清理后的数据
            if os.path.exists('cleaned_pressure_data.csv'):
                with open('cleaned_pressure_data.csv', 'rb') as f:
                    st.download_button(
                        label="下载清理数据",
                        data=f.read(),
                        file_name="cleaned_pressure_data.csv",
                        mime="text/csv"
                    )

def generate_report(results):
    """生成PDF报告（简化版）"""
    # 这里应该使用reportlab等库生成PDF
    # 目前返回文本版本
    stats = results['statistics']
    
    report_text = f"""
压力采集数据分析报告
==================

分析概要
--------
总数据点数: {stats['total_points']}
平均力值: {stats['force_mean']:.2f} N
标准差: {stats['force_std']:.2f} N
力值范围: {stats['force_min']:.1f} - {stats['force_max']:.1f} N
变异系数: {stats['cv']:.2f}%

质量评估
--------
系统稳定性: {'优秀' if stats['cv'] < 10 else '良好' if stats['cv'] < 20 else '需要关注'}

分析完成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report_text.encode('utf-8')

def create_charts_zip(chart_files):
    """创建图表ZIP压缩包"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, chart_file in enumerate(chart_files):
            if os.path.exists(chart_file):
                zip_file.write(chart_file, f"chart_{i+1:02d}.png")
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if __name__ == "__main__":
    main() 