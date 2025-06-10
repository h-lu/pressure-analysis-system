#!/bin/bash
# 腾讯云轻量应用服务器部署脚本
# 适用于已安装Docker的Ubuntu/CentOS服务器

set -e

echo "🚀 开始部署压力数据分析系统到腾讯云..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}警告: 建议使用非root用户运行此脚本${NC}"
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    echo "安装命令: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose未安装，正在安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose安装完成${NC}"
fi

# 获取用户输入
echo "📝 请输入配置信息:"
read -p "DeepSeek API Key: " DEEPSEEK_API_KEY
read -p "应用端口 (默认8000): " APP_PORT
APP_PORT=${APP_PORT:-8000}

# 验证API Key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${RED}错误: DeepSeek API Key不能为空${NC}"
    exit 1
fi

# 克隆或更新项目
PROJECT_DIR="pressure-analysis-system"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}项目目录已存在，正在更新...${NC}"
    cd $PROJECT_DIR
    git pull origin main
else
    echo -e "${GREEN}正在克隆项目...${NC}"
    git clone https://github.com/h-lu/pressure-analysis-system.git
    cd $PROJECT_DIR
fi

# 创建环境变量文件
echo "🔧 配置环境变量..."
cat > .env << EOF
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
HOST=0.0.0.0
PORT=$APP_PORT
DEBUG=false
EOF

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/{uploads,charts,reports}

# 构建和启动服务
echo -e "${GREEN}🔨 构建Docker镜像...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}🚀 启动服务...${NC}"
docker-compose up -d

# 检查服务状态
echo "⏰ 等待服务启动..."
sleep 10

if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ 服务启动成功!${NC}"
    
    # 获取服务器公网IP
    PUBLIC_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "获取IP失败")
    
    echo "🌍 访问信息:"
    echo "  应用地址: http://$PUBLIC_IP:$APP_PORT"
    echo "  API文档: http://$PUBLIC_IP:$APP_PORT/docs"
    
    # 防火墙提醒
    echo -e "${YELLOW}⚠️  请确保在腾讯云控制台的安全组中开放端口 $APP_PORT${NC}"
    echo "   登录腾讯云控制台 -> 轻量应用服务器 -> 防火墙设置"
    
    # 显示服务状态
    echo ""
    echo "📊 服务状态:"
    docker-compose ps
    
    # 显示日志查看命令
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo "  停止服务: docker-compose down"
    echo "  更新服务: git pull && docker-compose build --no-cache && docker-compose up -d"
    
else
    echo -e "${RED}❌ 服务启动失败，请检查日志${NC}"
    docker-compose logs
    exit 1
fi

echo -e "${GREEN}🎉 部署完成!${NC}"