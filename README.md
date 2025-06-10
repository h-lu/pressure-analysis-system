# 压力采集数据分析系统

一个基于Vue.js + FastAPI + R的全栈数据分析平台，专为压力数据采集、处理和可视化分析而设计。

## 🚀 技术栈

### 前端
- **Vue 3** - 现代化前端框架
- **Element Plus** - UI组件库
- **ECharts** - 数据可视化
- **Vite** - 构建工具
- **Pinia** - 状态管理

### 后端
- **FastAPI** - 高性能Python Web框架
- **R** - 统计分析和数据处理
- **rpy2** - Python与R的桥接
- **Pandas** - 数据处理
- **OpenAI API** - AI辅助分析

## 📦 项目结构

```
pressure-analysis-system/
├── frontend/           # Vue.js前端应用
│   ├── src/           # 源代码
│   ├── package.json   # 前端依赖
│   └── vite.config.js # Vite配置
├── backend/           # FastAPI后端应用
│   ├── api/          # API路由
│   ├── core/         # 核心功能
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   ├── r_analysis/   # R分析脚本
│   └── requirements.txt # Python依赖
├── Dockerfile        # Docker镜像构建文件
├── docker-compose.yml # Docker编排文件
└── run_server.py     # 应用启动入口
```

## ☁️ 腾讯云部署（推荐生产环境）

### 🚀 一键部署到腾讯云

[![Deploy to Tencent Cloud](https://img.shields.io/badge/Deploy%20to-Tencent%20Cloud-00A971?style=for-the-badge&logo=tencentcloud)](https://console.cloud.tencent.com/)

**轻量应用服务器（最简单）:**
```bash
# SSH连接到腾讯云服务器后执行
wget https://raw.githubusercontent.com/h-lu/pressure-analysis-system/main/tencent-deploy.sh
chmod +x tencent-deploy.sh
./tencent-deploy.sh
```

**详细部署指南**: 📖 [腾讯云部署快速开始](./TENCENT_QUICK_START.md)

## 🌐 Render部署指南

### 一键部署到Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### 手动部署步骤

1. **Fork此仓库**到您的GitHub账户

2. **在Render创建新的Web Service**
   - 访问 [Render Dashboard](https://dashboard.render.com)
   - 点击 "New +" → "Web Service"
   - 连接您的GitHub仓库

3. **配置部署设置**
   ```
   Name: pressure-analysis-system
   Environment: Docker
   Branch: main
   ```

4. **设置环境变量**
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   PORT=8000
   HOST=0.0.0.0
   DEBUG=false
   ```

5. **部署配置**
   - Build Command: `docker build -t pressure-analysis .`
   - Start Command: `python run_server.py`
   - Port: `8000`

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥（用于AI分析） | 必填 |
| `PORT` | 服务端口 | 8000 |
| `HOST` | 服务主机 | 0.0.0.0 |
| `DEBUG` | 调试模式 | false |

## 🐳 本地Docker部署

### 使用Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/h-lu/pressure-analysis-system.git
cd pressure-analysis-system

# 启动服务
docker-compose up -d

# 访问应用
open http://localhost:8000
```

### 使用Docker

```bash
# 构建镜像
docker build -t pressure-analysis .

# 运行容器
docker run -d \
  --name pressure-analysis \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY=your_api_key \
  pressure-analysis

# 访问应用
open http://localhost:8000
```

## 🛠️ 本地开发

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
cd ..
python run_server.py
```

## 📊 功能特性

- **数据上传**: 支持多种格式的压力数据文件上传
- **数据预处理**: 自动化数据清洗和格式化
- **统计分析**: 基于R的专业统计分析
- **可视化**: 交互式图表和报告生成
- **AI辅助**: 智能数据解读和建议
- **报告导出**: 支持多种格式的分析报告导出

## 🔧 系统要求

### 生产环境（Render）
- 自动配置，无需手动设置

### 本地开发
- **Node.js** >= 18.0
- **Python** >= 3.11
- **R** >= 4.0
- **Docker** >= 20.0（可选）

## 📝 API文档

部署后访问 `/docs` 查看完整的API文档（Swagger UI）

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

如果您遇到任何问题，请：

1. 查看 [Issues](https://github.com/h-lu/pressure-analysis-system/issues)
2. 创建新的 Issue
3. 联系维护团队

## 🔗 相关链接

- [腾讯云部署文档](./TENCENT_QUICK_START.md)
- [Render部署文档](https://render.com/docs)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Vue.js文档](https://vuejs.org/)
- [R语言文档](https://www.r-project.org/)

---

**快速开始**: 点击上方的 "Deploy to Tencent Cloud" 或 "Deploy to Render" 按钮，几分钟内即可拥有您自己的压力数据分析平台！