# Docker 部署指南

## 📦 镜像信息

### 镜像特性
- **中文字体支持**: 内置文泉驿微米黑、文泉驿正黑、Noto CJK等中文字体
- **完整R环境**: 预装tidyverse、ggplot2、dplyr等35+分析包
- **快速构建**: 优化后构建时间从2.4小时减少到2分钟
- **生产就绪**: 包含nginx、健康检查、自动重启等生产特性

### 镜像大小
- 后端镜像: ~1.3GB (包含完整R环境和字体)
- 前端镜像: ~52MB (nginx + Vue构建产物)

## 🚀 快速部署

### 方式1: 一键部署脚本
```bash
./docker-deploy.sh
```

### 方式2: 手动Docker Compose
```bash
docker-compose up -d
```

### 方式3: 从Docker Hub部署 (发布后)
```bash
# 设置Docker用户名
export DOCKER_USERNAME=your-username

# 运行发布脚本
./docker-publish.sh v2.0.0

# 使用发布的镜像部署
mkdir -p data/uploads data/output data/logs
docker-compose -f docker-compose.hub.yml up -d
```

## 🔧 配置说明

### 目录结构
```
data/
├── uploads/     # 上传的CSV文件
├── output/      # 分析结果和图表
└── logs/        # 系统日志
```

### 端口配置
- 前端: 80 (http://localhost)
- 后端: 8000 (http://localhost:8000)
- API文档: http://localhost:8000/docs

### 环境变量
后端服务支持以下环境变量：
- `DEBUG`: 调试模式 (默认: false)
- `HOST`: 绑定地址 (默认: 0.0.0.0)
- `PORT`: 端口号 (默认: 8000)
- `PYTHONPATH`: Python路径 (默认: /app)

**注意**: DeepSeek AI配置通过前端系统设置页面进行，无需环境变量。

## 🐛 故障排除

### 1. 中文字体问题
如果R图表中文显示异常：
```bash
# 检查字体安装
docker exec pressure-backend fc-list | grep -i "wqy\|noto"

# 重新生成字体缓存
docker exec pressure-backend fc-cache -fv
```

### 2. R包缺失问题
检查关键R包是否安装：
```bash
docker exec pressure-backend R -e "library(tidyverse); cat('OK\n')"
```

### 3. 网络连接问题
检查容器间网络：
```bash
docker network inspect pressure-analysis-system_pressure-network
```

### 4. 权限问题
确保数据目录权限正确：
```bash
chmod 755 data/uploads data/output data/logs
```

## 📊 性能优化

### 内存使用
- 最低要求: 2GB
- 推荐配置: 4GB
- R分析过程中可能占用较多内存

### 存储空间
- 系统镜像: ~1.4GB
- 运行数据: 根据分析文件大小而定
- 建议预留: 5GB以上

### 网络要求
- DeepSeek AI服务需要稳定的外网连接
- 内网部署时确保AI功能配置正确

## 🔄 更新升级

### 更新镜像
```bash
# 停止服务
docker-compose down

# 拉取最新镜像 (如果使用Docker Hub)
docker-compose pull

# 重新构建 (如果本地构建)
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

### 数据备份
```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf backup-20240613.tar.gz
```

## 🔐 安全建议

### 生产环境部署
1. **反向代理**: 使用nginx或traefik作为反向代理
2. **HTTPS**: 配置SSL证书
3. **防火墙**: 限制端口访问
4. **备份**: 定期备份数据

### 网络安全
1. **内网部署**: 建议在内网环境部署
2. **API密钥**: DeepSeek API密钥仅存储在浏览器本地
3. **数据隔离**: 分析数据不会上传到外部服务

## 📈 监控运维

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查前端状态
curl http://localhost/

# 查看容器状态
docker-compose ps
```

### 日志管理
```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 限制日志大小
docker-compose logs --tail=100
```

### 资源监控
```bash
# 查看资源使用
docker stats

# 查看磁盘使用
du -sh data/

# 清理旧数据
docker system prune -f
```

## 🛠️ 定制化

### 修改配置
- 编辑 `docker-compose.yml` 修改服务配置
- 编辑 `nginx.conf` 修改前端代理配置
- 编辑 Dockerfile 修改镜像构建

### 添加功能
- 后端: 修改 `backend/` 目录下的代码
- 前端: 修改 `frontend/` 目录下的代码
- R分析: 修改 `backend/r_analysis/` 下的R脚本

### 环境变量
创建 `.env` 文件进行环境配置：
```env
# 调试模式
DEBUG=false

# 服务端口
BACKEND_PORT=8000
FRONTEND_PORT=80

# 数据目录
DATA_DIR=./data
```

## 📚 相关文档

- [README.md](README.md) - 项目总体介绍
- [API文档](http://localhost:8000/docs) - 后端API文档
- [前端组件文档](frontend/README.md) - 前端开发文档
- [R分析文档](backend/r_analysis/README.md) - R脚本说明

---

💡 **提示**: 如果遇到问题，请先查看日志，然后参考故障排除部分，或提交Issue寻求帮助。 