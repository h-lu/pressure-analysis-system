# 压力采集数据分析系统 v1.0

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-red.svg)
![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)

## 项目简介

压力采集数据分析系统是一个基于 FastAPI + Vue 3 的智能压力数据分析平台，集成了 R 统计分析引擎和 DeepSeek AI 智能分析，为工业压力测试数据提供全面的统计分析和质量控制解决方案。

## 🌟 核心功能

### 📊 数据分析功能
- **多维度统计分析**: 提供35种专业统计图表和分析方法
- **过程能力分析**: Cp/Cpk指数计算，过程能力评估
- **统计过程控制**: Shewhart、CUSUM、EWMA等多种控制图
- **质量管理工具**: 帕雷托图、雷达图、相关性分析
- **空间分析**: 误差空间分布、位置相关性分析

### 🤖 AI智能分析
- **DeepSeek AI集成**: 智能分析报告生成
- **综合报告**: 自动生成Word格式的专业分析报告
- **智能建议**: 基于数据特征的改进建议
- **多语言支持**: 中文专业术语分析

### 📈 图表和可视化
- **35种专业图表**: 涵盖基础分析、控制图、专业质量分析等
- **交互式图表**: 支持缩放、筛选、导出
- **批量图表生成**: 一键生成所有相关图表
- **高清图表导出**: PNG格式，适合报告使用

### 📋 任务管理
- **实时任务监控**: 分析进度实时更新
- **历史记录管理**: 完整的分析历史追踪
- **批量操作**: 支持批量删除、导出等操作
- **任务重命名**: 自定义任务名称管理

### 🗂️ 文件管理
- **智能文件上传**: 支持CSV格式数据导入
- **数据预览**: 上传前数据预览和验证
- **文件格式检查**: 自动验证数据格式正确性
- **存储统计**: 实时存储空间监控

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI 0.104.1
- **数据分析**: R 4.x + rpy2 3.5.13
- **AI服务**: OpenAI API (DeepSeek)
- **数据处理**: Pandas 2.1.3, NumPy 1.24.3
- **文档生成**: python-docx 1.1.0
- **数据库**: JSON文件存储 + 文件系统

### 前端技术栈
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

### 部署环境
- **Python**: 3.8+
- **R**: 4.0+
- **系统支持**: Windows, macOS, Linux

## 🚀 快速开始

### 环境要求

```bash
Python >= 3.8
R >= 4.0
Node.js >= 16.0
```

### 1. 克隆项目

```bash
git clone https://github.com/your-username/pressure-analysis-system.git
cd pressure-analysis-system
```

### 2. 后端安装

```bash
cd backend
pip install -r requirements.txt
```

### 3. R包依赖安装

```bash
# 在R控制台中运行
install.packages(c("ggplot2", "dplyr", "tidyr", "corrplot", "VIM", 
                   "forecast", "changepoint", "nortest", "car"))
```

### 4. 前端安装

```bash
cd frontend
npm install
```

### 5. 配置文件

创建 `backend/.env` 文件（可选，系统支持前端配置）：

```env
# DeepSeek AI配置（可选）
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 6. 启动服务

**启动后端**:
```bash
cd backend
python run_server.py
```

**启动前端** (开发模式):
```bash
cd frontend
npm run dev
```

**生产环境部署**:
```bash
cd frontend
npm run build
# 构建完成后，后端会自动服务前端静态文件
```

### 7. 访问系统

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📖 使用指南

### 数据分析流程

1. **上传数据文件**
   - 支持CSV格式
   - 自动数据预览和验证
   - 最大文件大小：100MB

2. **配置分析参数**
   - 目标力值设置 (如: 5, 25, 50N)
   - 绝对容差 (默认: 0.5)
   - 百分比容差 (默认: 5%)

3. **执行分析**
   - 实时进度监控
   - 自动生成35种统计图表
   - 详细分析结果展示

4. **查看结果**
   - 关键指标摘要
   - 交互式图表浏览
   - AI智能分析报告

5. **导出报告**
   - 综合Word报告
   - 单独图表导出
   - CSV数据导出

### DeepSeek AI配置

1. 进入 **设置** 页面
2. 在 **DeepSeek AI配置** 中填入API密钥
3. 点击 **测试连接** 验证配置
4. 保存配置后即可使用AI分析功能

## 📊 分析功能详解

### 基础分析图表 (8个)
- 力值时间序列图
- 力值分布直方图  
- 力值箱线图
- 绝对偏差箱线图
- 百分比偏差箱线图
- 三维散点图
- 散点图矩阵
- 相关性矩阵

### 控制图 (7个)
- Shewhart控制图
- 移动平均控制图
- X-bar & R控制图
- CUSUM控制图
- EWMA控制图
- I-MR控制图
- 运行图

### 专业质量分析 (12个)
- 过程能力分析
- 帕雷托图
- 残差分析
- Q-Q正态性检验图
- 雷达图
- 热力图
- 成功率趋势图
- 能力指数图
- 质量仪表盘
- 瀑布图
- 空间聚类分析
- 平行坐标图

### 多维分析 (8个)
- XY平面热力图
- 2D投影图
- 位置异常热力图
- 空间密度图
- 多变量关系图
- 异常模式图
- 质量分布图
- 综合评估图

## 🔧 API 文档

### 主要API端点

**文件管理**:
- `POST /api/upload` - 文件上传
- `GET /api/preview/{filename}` - 数据预览
- `GET /api/list` - 文件列表

**分析任务**:
- `POST /api/analyze` - 启动分析
- `GET /api/task/{task_id}` - 任务状态
- `GET /api/results/{task_id}` - 分析结果

**AI分析**:
- `POST /api/deepseek/generate-comprehensive-word-report` - 生成Word报告
- `GET /api/deepseek/get/{task_id}` - 获取AI分析

**系统管理**:
- `GET /api/tasks` - 任务列表
- `GET /api/history/` - 历史记录
- `GET /api/system-info` - 系统信息

完整API文档请访问: http://localhost:8000/docs

## 🗂️ 项目结构

```
pressure-analysis-system/
├── backend/                 # 后端服务
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── services/           # 业务服务
│   ├── static/             # 静态文件
│   ├── output/             # 分析输出
│   ├── temp/               # 临时文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API服务
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── stores/        # 状态管理
│   │   └── router/        # 路由配置
│   ├── public/            # 公共资源
│   └── package.json       # Node依赖
├── R/                      # R分析脚本
├── docs/                   # 项目文档
└── README.md              # 项目说明
```

## 🐛 常见问题

### Q: R包安装失败？
A: 确保R版本>=4.0，使用管理员权限安装包，或尝试指定CRAN镜像。

### Q: DeepSeek AI连接失败？
A: 检查API密钥是否正确，网络连接是否正常，确认API配额充足。

### Q: 文件上传失败？
A: 检查文件格式是否为CSV，文件大小是否超过100MB，数据格式是否正确。

### Q: 图表显示异常？
A: 清除浏览器缓存，检查数据是否包含异常值，确认R脚本正常执行。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2025-06-12)
- ✨ 初始版本发布
- 🎉 完整的压力数据分析功能
- 🤖 DeepSeek AI智能分析集成
- 📊 35种专业统计图表
- 📋 任务管理和历史记录
- 🔧 用户配置管理系统
- 📱 响应式Web界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 开发团队

- **项目维护者**: [Your Name]
- **技术支持**: [Support Email]

## 🔗 相关链接

- [项目主页](https://github.com/your-username/pressure-analysis-system)
- [在线文档](https://your-docs-site.com)
- [问题报告](https://github.com/your-username/pressure-analysis-system/issues)
- [功能请求](https://github.com/your-username/pressure-analysis-system/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 