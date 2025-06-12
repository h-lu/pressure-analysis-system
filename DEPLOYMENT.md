# 压力采集数据分析系统部署指南

## 部署概述

本文档详细说明了如何在不同环境中部署压力采集数据分析系统，包括开发环境、测试环境和生产环境的配置。

## 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最低 4GB，推荐 8GB+
- **存储**: 最低 10GB 可用空间
- **网络**: 需要访问互联网（用于DeepSeek AI服务）

### 软件依赖
- **Python**: 3.8+ (推荐 3.9 或 3.10)
- **R**: 4.0+ (推荐 4.3+)
- **Node.js**: 16.0+ (推荐 18.0+)
- **Git**: 2.0+

## 开发环境部署

### 1. 代码获取

```bash
git clone https://github.com/your-username/pressure-analysis-system.git
cd pressure-analysis-system
```

### 2. Python环境配置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装Python依赖
cd backend
pip install -r requirements.txt
```

### 3. R环境配置

打开R控制台，安装必要的包：

```r
# 设置CRAN镜像（可选）
options(repos = c(CRAN = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/"))

# 安装核心包
install.packages(c("tidyverse", "slider", "GGally", "plotly", "patchwork", "cluster", 
                   "tools", "jsonlite", "argparse"))

```

### 4. 前端环境配置

```bash
cd frontend
npm install

# 启动开发服务器
npm run dev
```

### 5. 启动后端服务

```bash
cd backend
python run_server.py
```

### 6. 访问应用

- **前端开发服务器**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 生产环境部署

### 方案一：单机部署

#### 1. 系统准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv r-base nodejs npm git

# CentOS/RHEL
sudo yum install python3 python3-pip r-base nodejs npm git

# macOS (使用Homebrew)
brew install python r node git
```

#### 2. 应用部署

```bash
# 创建应用目录
sudo mkdir -p /opt/pressure-analysis
sudo chown $USER:$USER /opt/pressure-analysis
cd /opt/pressure-analysis

# 克隆代码
git clone https://github.com/your-username/pressure-analysis-system.git .

# 安装Python依赖
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt

# 构建前端
cd ../frontend
npm install
npm run build

# 前端文件将自动集成到后端服务
```

#### 3. 配置文件

创建生产环境配置：

```bash
# 创建环境变量文件（可选）
cat > backend/.env << EOF
# 应用配置
ENV=production
DEBUG=false

# DeepSeek AI配置（可选，也可通过前端配置）
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 文件上传配置
MAX_FILE_SIZE=104857600
UPLOAD_PATH=/opt/pressure-analysis/backend/static/uploads
EOF
```

#### 4. 启动服务

```bash
cd /opt/pressure-analysis/backend

# 直接启动（适合测试）
python run_server.py

# 使用nohup后台运行
nohup python run_server.py > ../logs/app.log 2>&1 &

# 或使用screen
screen -S pressure-analysis
python run_server.py
# Ctrl+A, D 分离会话
```

### 方案二：Docker部署

#### 1. 创建Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装R包
RUN R -e "install.packages(c('ggplot2', 'dplyr', 'tidyr', 'corrplot', 'VIM', 'forecast', 'changepoint', 'nortest', 'car'), repos='https://cloud.r-project.org/')"

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p output temp static/uploads config

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "run_server.py"]
```

#### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  pressure-analysis:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/output
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - ENV=production
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - pressure-analysis
    restart: unless-stopped
```

#### 3. 启动Docker服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方案三：云服务部署

#### 阿里云/腾讯云部署

1. **购买云服务器**
   - 配置：2核4GB，系统盘40GB
   - 系统：Ubuntu 20.04 LTS

2. **配置安全组**
   - 开放端口：80, 443, 8000

3. **部署脚本**

```bash
#!/bin/bash
# deploy.sh

set -e

echo "开始部署压力分析系统..."

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv r-base nodejs npm git nginx

# 克隆代码
cd /opt
sudo git clone https://github.com/your-username/pressure-analysis-system.git
sudo chown -R $USER:$USER pressure-analysis-system
cd pressure-analysis-system

# 安装Python依赖
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt

# 安装R包
sudo R -e "install.packages(c('ggplot2', 'dplyr', 'tidyr', 'corrplot', 'VIM', 'forecast', 'changepoint', 'nortest', 'car'), repos='https://cloud.r-project.org/')"

# 构建前端
cd ../frontend
npm install
npm run build

# 配置Nginx
sudo tee /etc/nginx/sites-available/pressure-analysis << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    client_max_body_size 100M;
}
EOF

sudo ln -s /etc/nginx/sites-available/pressure-analysis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 创建systemd服务
sudo tee /etc/systemd/system/pressure-analysis.service << EOF
[Unit]
Description=Pressure Analysis System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/pressure-analysis-system/backend
Environment=PATH=/opt/pressure-analysis-system/venv/bin
ExecStart=/opt/pressure-analysis-system/venv/bin/python run_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable pressure-analysis
sudo systemctl start pressure-analysis

echo "部署完成！访问 http://your-server-ip 查看应用"
```

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| ENV | 运行环境 | development | 否 |
| DEBUG | 调试模式 | true | 否 |
| DEEPSEEK_API_KEY | DeepSeek API密钥 | - | 否* |
| DEEPSEEK_BASE_URL | DeepSeek API地址 | https://api.deepseek.com | 否 |
| MAX_FILE_SIZE | 最大文件大小(字节) | 104857600 | 否 |

*注：可通过前端界面配置

### 目录结构

```
/opt/pressure-analysis-system/
├── backend/                # 后端应用
│   ├── output/            # 分析结果输出
│   ├── temp/              # 临时文件
│   ├── static/            # 静态文件
│   ├── config/            # 配置文件
│   └── logs/              # 日志文件
├── frontend/              # 前端源码
├── data/                  # 数据文件
└── logs/                  # 应用日志
```

## 监控和维护

### 日志管理

```bash
# 查看应用日志
tail -f /opt/pressure-analysis-system/logs/app.log

# 查看系统服务日志
sudo journalctl -u pressure-analysis -f

# 日志轮转配置
sudo tee /etc/logrotate.d/pressure-analysis << EOF
/opt/pressure-analysis-system/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### 备份策略

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/pressure-analysis"
APP_DIR="/opt/pressure-analysis-system"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置和数据
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
    $APP_DIR/backend/config \
    $APP_DIR/backend/output \
    $APP_DIR/logs

# 保留最近30天的备份
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: backup_$DATE.tar.gz"
```

### 性能监控

```bash
# 系统资源监控
htop

# 应用端口检查
netstat -tlnp | grep 8000

# 磁盘空间监控
df -h /opt/pressure-analysis-system

# 内存使用监控
free -h
```

## 故障排除

### 常见问题

1. **R包安装失败**
   ```bash
   # 确保R版本正确
   R --version
   
   # 手动安装失败的包
   sudo R -e "install.packages('package_name', repos='https://cloud.r-project.org/')"
   ```

2. **前端构建失败**
   ```bash
   # 清除node_modules重新安装
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

3. **DeepSeek API连接失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 检查API配额是否充足

4. **文件上传失败**
   - 检查文件大小限制
   - 确认上传目录权限
   - 验证磁盘空间充足

### 性能优化

1. **系统级优化**
   ```bash
   # 增加文件描述符限制
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   echo "* hard nofile 65536" >> /etc/security/limits.conf
   
   # 优化TCP参数
   echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
   sysctl -p
   ```

2. **应用级优化**
   - 启用Redis缓存（可选）
   - 配置CDN加速静态资源
   - 启用gzip压缩

## 安全配置

### 基础安全

```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

### SSL证书配置

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

---

有关更多部署问题，请查看项目文档或提交Issue。 