"""
压力数据分析系统 - Flask Web应用
使用rpy2调用现有的R分析代码
"""

from flask import Flask, request, jsonify, render_template, send_file
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
import pandas as pd
import json
import os
import tempfile
import zipfile
from werkzeug.utils import secure_filename
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CHARTS_FOLDER'] = 'static/charts'

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHARTS_FOLDER'], exist_ok=True)

class PressureAnalyzer:
    """压力数据分析引擎"""
    
    def __init__(self):
        """初始化R环境和分析引擎"""
        try:
            # 激活pandas和R的数据交换
            pandas2ri.activate()
            
            # 初始化R环境
            self.r = robjects.r
            
            # 预加载必要的R包
            self.r('library(tidyverse)')
            self.r('library(ggplot2)')
            self.r('library(plotly)')
            self.r('library(ggthemr)')
            
            # 设置中文字体支持
            self.r('library(showtext)')
            self.r('font_add("simhei", "simhei.ttf")')
            self.r('showtext_auto()')
            
            logger.info("R环境初始化成功")
            
        except Exception as e:
            logger.error(f"R环境初始化失败: {e}")
            raise
    
    def set_parameters(self, data_file, target_forces, tolerance_abs, tolerance_pct):
        """设置分析参数"""
        try:
            # 设置R全局变量
            self.r.assign('data_file', data_file)
            self.r.assign('target_forces', robjects.FloatVector(target_forces))
            self.r.assign('tolerance_abs', tolerance_abs)
            self.r.assign('tolerance_pct', tolerance_pct)
            
            # 设置输出目录
            self.r.assign('charts_dir', app.config['CHARTS_FOLDER'])
            
            logger.info(f"参数设置成功: {target_forces}, {tolerance_abs}, {tolerance_pct}")
            
        except Exception as e:
            logger.error(f"参数设置失败: {e}")
            raise
    
    def analyze_data(self, csv_file, target_forces, tolerance_abs, tolerance_pct):
        """执行完整的数据分析"""
        try:
            # 1. 设置参数
            self.set_parameters(csv_file, target_forces, tolerance_abs, tolerance_pct)
            
            # 2. 执行R分析脚本
            logger.info("开始执行R分析脚本...")
            self.r('source("pressure_analysis_simple.R")')
            
            # 3. 提取分析结果
            results = self.extract_results()
            
            logger.info("分析完成")
            return results
            
        except Exception as e:
            logger.error(f"分析执行失败: {e}")
            raise
    
    def extract_results(self):
        """从R环境中提取分析结果"""
        try:
            results = {
                'summary': self.get_text_summary(),
                'charts': self.get_charts_info(),
                'statistics': self.get_statistics(),
                'files': self.get_output_files()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"结果提取失败: {e}")
            raise
    
    def get_text_summary(self):
        """获取文本分析摘要"""
        try:
            # 从R环境获取数据摘要
            total_points = int(self.r('nrow(data)')[0])
            force_range = f"{float(self.r('min(data$force_numeric)')[0]):.1f} - {float(self.r('max(data$force_numeric)')[0]):.1f}"
            cv = float(self.r('sd(data$force_numeric) / mean(data$force_numeric) * 100')[0])
            
            summary_html = f"""
            <div class="row">
                <div class="col-md-4">
                    <h6>数据概览</h6>
                    <p><strong>总数据点:</strong> {total_points}</p>
                    <p><strong>力值范围:</strong> {force_range} N</p>
                    <p><strong>变异系数:</strong> {cv:.2f}%</p>
                </div>
                <div class="col-md-4">
                    <h6>质量评估</h6>
                    <p><strong>整体稳定性:</strong> {'良好' if cv < 10 else '需关注' if cv < 20 else '不稳定'}</p>
                    <p><strong>异常值检测:</strong> 已完成</p>
                    <p><strong>趋势分析:</strong> 已完成</p>
                </div>
                <div class="col-md-4">
                    <h6>输出文件</h6>
                    <p><strong>清理数据:</strong> cleaned_pressure_data.csv</p>
                    <p><strong>分析结果:</strong> analysis_results.RData</p>
                    <p><strong>图表数量:</strong> 29个</p>
                </div>
            </div>
            """
            
            return summary_html
            
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return f"<p>摘要生成失败: {e}</p>"
    
    def get_charts_info(self):
        """获取图表信息"""
        try:
            charts = []
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
            
            # 检查生成的图表文件
            charts_dir = app.config['CHARTS_FOLDER']
            for i, title in enumerate(chart_titles, 1):
                chart_file = f"chart_{i:02d}.png"
                chart_path = os.path.join(charts_dir, chart_file)
                
                if os.path.exists(chart_path):
                    charts.append({
                        'title': title,
                        'url': f"/static/charts/{chart_file}",
                        'file': chart_file
                    })
            
            return charts
            
        except Exception as e:
            logger.error(f"图表信息获取失败: {e}")
            return []
    
    def get_statistics(self):
        """获取统计数据"""
        try:
            # 从R环境提取关键统计信息
            stats = {}
            
            # 基础统计
            stats['mean'] = float(self.r('mean(data$force_numeric)')[0])
            stats['std'] = float(self.r('sd(data$force_numeric)')[0])
            stats['min'] = float(self.r('min(data$force_numeric)')[0])
            stats['max'] = float(self.r('max(data$force_numeric)')[0])
            
            return stats
            
        except Exception as e:
            logger.error(f"统计数据获取失败: {e}")
            return {}
    
    def get_output_files(self):
        """获取输出文件信息"""
        output_files = []
        
        # 检查输出文件
        files_to_check = [
            ('cleaned_pressure_data.csv', '清理后的数据'),
            ('analysis_results.RData', 'R分析结果')
        ]
        
        for filename, description in files_to_check:
            if os.path.exists(filename):
                output_files.append({
                    'filename': filename,
                    'description': description,
                    'size': os.path.getsize(filename)
                })
        
        return output_files

# 全局分析器实例
analyzer = None

def get_analyzer():
    """获取分析器实例（单例模式）"""
    global analyzer
    if analyzer is None:
        analyzer = PressureAnalyzer()
    return analyzer

# 路由定义

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析数据的API端点"""
    try:
        # 验证文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': '只支持CSV文件'})
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 获取分析参数
        target_forces_str = request.form.get('target_forces', '5,25,50')
        tolerance_abs = float(request.form.get('tolerance_abs', 2))
        tolerance_pct = float(request.form.get('tolerance_pct', 5))
        
        # 解析目标力值
        target_forces = [float(x.strip()) for x in target_forces_str.split(',')]
        
        # 执行分析
        logger.info(f"开始分析文件: {filepath}")
        analyzer = get_analyzer()
        results = analyzer.analyze_data(filepath, target_forces, tolerance_abs, tolerance_pct)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': '分析完成'
        })
        
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download/<file_type>')
def download_file(file_type):
    """下载结果文件"""
    try:
        if file_type == 'csv':
            filename = 'cleaned_pressure_data.csv'
            if os.path.exists(filename):
                return send_file(filename, as_attachment=True)
            else:
                return jsonify({'error': '文件不存在'}), 404
                
        elif file_type == 'charts':
            # 打包所有图表为ZIP文件
            zip_filename = 'pressure_analysis_charts.zip'
            charts_dir = app.config['CHARTS_FOLDER']
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for filename in os.listdir(charts_dir):
                    if filename.endswith('.png'):
                        file_path = os.path.join(charts_dir, filename)
                        zipf.write(file_path, filename)
            
            return send_file(zip_filename, as_attachment=True)
        
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
            
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """健康检查"""
    try:
        # 检查R环境
        analyzer = get_analyzer()
        r_version = str(analyzer.r('R.version.string')[0])
        
        return jsonify({
            'status': 'healthy',
            'r_version': r_version,
            'python_packages': ['flask', 'rpy2', 'pandas']
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 开发模式
    app.run(host='0.0.0.0', port=5000, debug=True) 