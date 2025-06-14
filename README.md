# 压力采集数据分析系统

一个基于Vue.js + FastAPI + R的压力数据分析系统，支持数据上传、智能分析、图表生成和AI辅助分析。

## 🚀 快速开始

### 系统要求

- Docker 20.0+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 生产环境部署

#### 1. 克隆项目

```bash
git clone https://github.com/h-lu/pressure-analysis-system
cd pressure-analysis-system
```

#### 2. 配置环境变量（可选）

复制环境变量示例文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，根据需要修改配置：

```bash
# ==================== 前端配置 ====================
# 前端访问端口 (默认: 80)
FRONTEND_PORT=80

# ==================== 后端配置 ====================
# 后端服务端口 (默认: 8000)
BACKEND_PORT=8000

# ==================== AI配置 ====================
# DeepSeek AI 配置 (可选，也可以通过前端界面配置)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

#### 3. 启动服务

**使用默认端口 (80)：**

```bash
docker-compose up -d
```

**使用自定义端口：**

```bash
# 方法1: 通过环境变量
FRONTEND_PORT=8080 docker-compose up -d

# 方法2: 修改 .env 文件
echo "FRONTEND_PORT=8080" >> .env
docker-compose up -d

# 方法3: 导出环境变量
export FRONTEND_PORT=8080
docker-compose up -d
```

#### 4. 访问应用

- **前端界面**: `http://localhost:端口号` (默认: http://localhost)
- **后端API**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`

#### 5. 验证部署

检查服务状态：

```bash
# 查看容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 检查健康状态
curl http://localhost:8000/health
```

## 📋 功能特性

### 核心功能

- **数据上传**: 支持CSV格式的压力数据文件上传
- **智能分析**: 基于R语言的统计分析和数据处理
- **图表生成**: 自动生成35种不同类型的数据可视化图表
- **AI辅助**: 集成DeepSeek AI，提供智能数据分析建议
- **任务管理**: 分析任务的创建、监控和管理
- **数据管理**: 历史数据查看、导出和清理

### 技术特性

- **容器化部署**: 基于Docker的一键部署
- **微服务架构**: 前后端分离，易于扩展
- **响应式设计**: 支持桌面和移动设备
- **实时更新**: WebSocket支持的实时状态更新
- **多环境支持**: 开发、测试、生产环境配置

## 🔧 配置说明

### 端口配置

系统支持灵活的端口配置：

| 配置方式 | 示例 | 说明 |
|---------|------|------|
| 环境变量 | `FRONTEND_PORT=8080` | 推荐方式 |
| .env文件 | `FRONTEND_PORT=8080` | 持久化配置 |
| docker-compose | `"8080:80"` | 直接修改配置文件 |

### 常用端口示例

| 环境 | 前端端口 | 后端端口 | 配置 |
|------|----------|----------|------|
| 生产环境 | 80 | 8000 | `FRONTEND_PORT=80` |
| 开发环境 | 3000 | 8000 | `FRONTEND_PORT=3000` |
| 测试环境 | 8080 | 8000 | `FRONTEND_PORT=8080` |

### AI配置

支持两种配置方式：

1. **环境变量配置**（推荐）：
```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

2. **前端界面配置**：
   - 访问"系统设置"页面
   - 在"DeepSeek AI 配置"部分输入API信息
   - 点击"测试连接"验证配置

## 🛠️ 开发环境

### 本地开发

**前端开发：**

```bash
cd frontend
npm install
npm run dev
```

**后端开发：**

```bash
cd backend
pip install -r requirements.txt
python run_server.py
```

### 构建优化

系统已针对构建速度进行优化：

- **后端构建时间**: ~9分钟（使用预编译R包）
- **前端构建时间**: ~30秒（使用esbuild）
- **总构建时间**: ~10分钟

## 📊 使用指南

### 数据分析流程

1. **上传数据**: 在"数据分析"页面上传CSV文件
2. **配置参数**: 设置分析参数和选项
3. **开始分析**: 点击"开始分析"按钮
4. **查看结果**: 实时查看分析进度和结果
5. **下载报告**: 下载生成的图表和分析报告

### 支持的数据格式

- **文件格式**: CSV
- **编码格式**: UTF-8
- **数据要求**: 包含时间戳和压力值列
- **文件大小**: 最大100MB

### 生成的图表类型

系统自动生成35种图表，包括：

- 基础统计图表（直方图、箱线图、散点图等）
- 时间序列分析图表
- 相关性分析图表
- 高级统计图表（密度图、QQ图等）
- 交互式图表（基于Plotly）

## 🔍 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 查看端口占用
lsof -i :80
netstat -tulpn | grep :80

# 解决方案：使用其他端口
FRONTEND_PORT=8080 docker-compose up -d
```

**2. 容器启动失败**
```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**3. R分析失败**
```bash
# 检查R包安装
docker exec pressure-backend-fast R -e "library(tidyverse)"

# 重新安装R包
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

**4. 前端无法访问后端**
- 检查网络连接
- 确认后端服务正常运行
- 检查防火墙设置

### 性能优化

**内存优化：**
- 建议分配至少4GB内存给Docker
- 大文件分析时可能需要更多内存

**存储优化：**
- 定期清理历史数据和缓存
- 使用"数据管理"功能进行清理

## 📝 更新日志

### v1.0.0 (2024-01-XX)

**新功能：**
- ✅ 完整的数据分析流程
- ✅ 35种图表自动生成
- ✅ DeepSeek AI集成
- ✅ 容器化部署
- ✅ 灵活的端口配置
- ✅ 实时分析进度显示

**优化：**
- ✅ 构建时间优化（50%提升）
- ✅ 前端性能优化
- ✅ R包安装优化
- ✅ 错误处理改进

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查 [Issues](../../issues) 中是否有类似问题
3. 创建新的Issue描述您的问题

---

**快速部署命令：**

```bash
# 克隆项目
git clone <repository-url>
cd pressure-analysis-system

# 启动服务（默认端口80）
docker-compose up -d

# 或使用自定义端口
FRONTEND_PORT=8080 docker-compose up -d

# 访问应用
open http://localhost  # 或 http://localhost:8080
``` 