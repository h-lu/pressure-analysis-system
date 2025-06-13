# 压力采集数据分析系统

## 🚀 项目介绍

压力采集数据分析系统是一个基于 FastAPI + Vue 3 + R 统计分析的智能数据分析平台，集成了 DeepSeek AI 智能分析功能，专门用于压力测试数据的自动化分析和可视化。

### ✨ 核心特性

- **🔧 现代化技术栈**: FastAPI + Vue 3 + R + Docker
- **📊 智能数据分析**: 集成 R 统计分析引擎，35+ 专业图表
- **🤖 AI 智能报告**: DeepSeek AI 生成综合分析报告和建议
- **🌍 中文全支持**: 完整的中文界面和中文图表生成
- **🐳 容器化部署**: Docker 一键部署，2分钟快速启动
- **📈 实时监控**: 任务状态实时监控和进度追踪
- **📋 报告导出**: 支持 Word、PDF、图表包多格式导出

### 🎯 主要功能

#### 数据分析功能
- ✅ CSV 文件上传和预览
- ✅ 自定义分析参数（目标力值、容差设置）
- ✅ 35+ 专业统计图表
  - 基础分析图表 (8个): 时间序列、分布图、箱线图等
  - 控制图 (7个): Shewhart、移动平均、CUSUM等
  - 质量分析图 (12个): 过程能力、帕累托图、残差分析等
  - 多维分析图 (8个): 热图、异常检测、空间聚类等
- ✅ 过程能力分析 (Cp, Cpk 指标)
- ✅ 质量等级评估
- ✅ 异常检测和模式识别

#### AI 智能分析
- 🤖 DeepSeek AI 驱动的智能分析
- 📊 自动生成综合分析报告
- 💡 智能建议和改进方案
- 📄 Word 格式报告导出

#### 系统管理
- 📋 任务管理和历史记录
- 🔄 实时任务状态监控
- ⚙️ 系统设置和配置管理
- 📁 文件管理和存储

## 🛠️ 技术架构

### 后端技术栈
- **Python 3.10**: 核心开发语言
- **FastAPI**: 高性能 Web 框架
- **R 4.2.2**: 统计分析引擎
- **rpy2**: Python-R 接口
- **DeepSeek AI**: 智能分析服务

### 前端技术栈
- **Vue 3**: 现代化前端框架
- **Element Plus**: UI 组件库
- **Pinia**: 状态管理
- **ECharts**: 图表可视化
- **Axios**: HTTP 客户端

### 部署技术
- **Docker**: 容器化部署
- **Nginx**: 前端服务器
- **Docker Compose**: 服务编排

## 🚀 快速开始

### 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 2GB+ 可用内存
- 5GB+ 可用存储空间

### 一键部署

```bash
# 克隆项目
git clone <repository-url>
cd 压力系统

# 运行部署脚本
./docker-deploy.sh

# 清理重新部署（可选）
./docker-deploy.sh --clean
```

### 手动部署

```bash
# 创建数据目录
mkdir -p data/uploads data/output data/logs

# 构建并启动服务
docker-compose build --parallel
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 访问地址

部署成功后，可通过以下地址访问：

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📖 使用指南

### 1. 系统配置

首次使用前，请在系统设置页面配置：

1. **DeepSeek AI 设置**
   - 访问 `系统设置` -> `DeepSeek AI 设置`
   - 输入 DeepSeek API Key
   - 测试连接确保配置正确

2. **分析参数默认设置**
   - 设置默认目标力值 (如: 5, 25, 50)
   - 配置容差参数

### 2. 数据分析流程

#### 步骤1: 上传数据文件
- 支持 CSV 格式文件
- 拖拽上传或点击选择
- 自动数据验证和预览

#### 步骤2: 配置分析参数
- 设置目标力值 (N)
- 配置绝对容差和百分比容差
- 选择分析选项

#### 步骤3: 执行分析
- 点击"开始分析"按钮
- 实时监控分析进度
- 查看任务状态和日志

#### 步骤4: 查看结果
- 浏览 35+ 分析图表
- 查看关键指标和统计数据
- 生成 AI 智能分析报告

#### 步骤5: 导出报告
- 下载 Word 综合报告
- 导出单个图表
- 保存分析数据

### 3. 图表说明

#### 基础分析图表 (8个)
- `force_time_series`: 力值时间序列图
- `force_distribution`: 力值分布直方图
- `force_boxplot`: 力值箱线图
- `absolute_deviation_boxplot`: 绝对偏差箱线图
- `percentage_deviation_boxplot`: 百分比偏差箱线图
- `interactive_3d_scatter`: 交互式3D散点图
- `scatter_matrix`: 散点矩阵图
- `correlation_matrix`: 相关系数矩阵

#### 控制图 (7个)
- `shewhart_control`: Shewhart控制图
- `moving_average`: 移动平均控制图
- `xbar_r_control`: X-bar和R控制图
- `cusum_control`: CUSUM控制图
- `ewma_control`: EWMA控制图
- `imr_control`: I-MR控制图
- `run_chart`: 运行图

#### 专业质量分析 (12个)
- `process_capability`: 过程能力分析
- `pareto_chart`: 帕累托图
- `residual_analysis`: 残差分析
- `qq_normality`: Q-Q正态性检验图
- `radar_chart`: 雷达图
- `heatmap`: 热图分析
- `success_rate_trend`: 成功率趋势图
- `capability_index`: 能力指数图
- `quality_dashboard`: 质量仪表板
- `waterfall_chart`: 瀑布图
- `spatial_clustering`: 空间聚类分析
- `parallel_coordinates`: 平行坐标图

#### 多维分析 (8个)
- `xy_heatmap`: XY位置热图
- `projection_2d`: 2D投影图
- `position_anomaly_heatmap`: 位置异常热图
- `spatial_density`: 空间密度图
- `multivariate_relations`: 多变量关系图
- `anomaly_patterns`: 异常模式图
- `quality_distribution_map`: 质量分布图
- `comprehensive_assessment`: 综合评估图

## 🔧 系统管理

### 服务管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [backend|frontend]

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

### 数据管理

```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 清理临时文件
docker-compose exec backend rm -rf /app/backend/uploads/*
docker-compose exec backend rm -rf /app/backend/output/*

# 查看存储使用情况
du -sh data/
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看系统健康状态
curl http://localhost:8000/health

# 查看API响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

## 🛠️ 开发指南

### 本地开发环境

#### 后端开发

```bash
# 安装Python依赖
cd backend
pip install -r requirements.txt

# 安装R依赖
R -e "install.packages(c('tidyverse', 'ggplot2', 'dplyr', ...))"

# 启动开发服务器
python run_server.py
```

#### 前端开发

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 自定义配置

#### 修改分析参数

编辑 `backend/r_analysis/pressure_analysis.R` 文件自定义分析逻辑。

#### 添加新图表

1. 在 R 脚本中添加新的图表生成函数
2. 更新前端图表列表
3. 添加相应的API端点

#### 自定义AI分析

修改 `backend/deepseek/` 目录下的提示词模板。

## 📊 系统要求

### 最低配置
- CPU: 2核
- 内存: 2GB
- 存储: 5GB
- 网络: 稳定的互联网连接（用于AI服务）

### 推荐配置
- CPU: 4核
- 内存: 4GB
- 存储: 10GB
- 网络: 高速互联网连接

## 🔐 安全说明

- DeepSeek API Key 仅存储在浏览器本地
- 分析数据仅在本地处理
- 不会上传敏感数据到外部服务
- 建议在内网环境中部署使用

## 🐛 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细错误日志
docker-compose logs backend
docker-compose logs frontend

# 重新构建镜像
docker-compose build --no-cache
```

#### 2. R分析执行失败
```bash
# 检查R包安装
docker-compose exec backend R -e "installed.packages()"

# 手动测试R脚本
docker-compose exec backend Rscript backend/r_analysis/test.R
```

#### 3. 前端无法访问后端
```bash
# 检查网络连接
docker network ls
docker network inspect pressure-analysis-system_pressure-network

# 重启nginx
docker-compose restart frontend
```

#### 4. AI分析失败
- 检查 DeepSeek API Key 配置
- 确认网络连接正常
- 查看 API 调用日志

## 📝 更新日志

### v2.0.0 (2024-06-13)
- ✨ 新增中文字体支持
- 🔧 优化Docker构建性能（构建时间从2.4小时减少到2分钟）
- 🤖 改进DeepSeek AI配置方式
- 📊 增加35+专业分析图表
- 🐳 简化部署流程
- 🔒 增强安全性配置

### v1.0.0 (2024-06-01)
- 🎉 首个正式版本发布
- 📊 基础数据分析功能
- 🤖 AI智能分析集成
- 🐳 Docker容器化部署

## 📄 开源协议

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues]
- 📖 文档: [项目文档]

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！** 