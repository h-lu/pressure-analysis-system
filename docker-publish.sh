#!/bin/bash

# 压力采集数据分析系统 - Docker Hub 发布脚本

set -e

echo "===========================================" 
echo "压力采集数据分析系统 Docker Hub 发布脚本"
echo "==========================================="

# 配置变量
DOCKER_USERNAME="${DOCKER_USERNAME:-your-username}"
PROJECT_NAME="pressure-analysis-system"
VERSION="${1:-latest}"

# 检查是否已登录Docker Hub
if ! docker info | grep -q "Username"; then
    echo "请先登录Docker Hub:"
    echo "docker login"
    exit 1
fi

echo "发布版本: $VERSION"
echo "Docker用户: $DOCKER_USERNAME"

# 构建镜像
echo "构建后端镜像..."
docker build -f Dockerfile.backend -t ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:${VERSION} .
docker tag ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:${VERSION} ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:latest

echo "构建前端镜像..."
docker build -f Dockerfile.frontend -t ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:${VERSION} .
docker tag ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:${VERSION} ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:latest

# 推送镜像到Docker Hub
echo "推送后端镜像到Docker Hub..."
docker push ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:${VERSION}
docker push ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:latest

echo "推送前端镜像到Docker Hub..."
docker push ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:${VERSION}
docker push ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:latest

# 创建docker-compose.hub.yml用于从Docker Hub部署
cat > docker-compose.hub.yml << EOF
services:
  # 后端API服务
  backend:
    image: ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:latest
    container_name: pressure-backend
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - DEBUG=false
      - HOST=0.0.0.0
      - PORT=8000
      # DeepSeek AI配置通过前端系统设置页面配置，无需环境变量
    volumes:
      # 持久化数据目录
      - ./data/uploads:/app/backend/uploads
      - ./data/output:/app/backend/output
      - ./data/logs:/app/logs
    ports:
      - "8000:8000"
    networks:
      - pressure-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 前端Web服务
  frontend:
    image: ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:latest
    container_name: pressure-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - pressure-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  pressure-network:
    driver: bridge
EOF

echo "==========================================="
echo "发布成功！"
echo ""
echo "镜像信息:"
echo "  后端镜像: ${DOCKER_USERNAME}/${PROJECT_NAME}-backend:${VERSION}"
echo "  前端镜像: ${DOCKER_USERNAME}/${PROJECT_NAME}-frontend:${VERSION}"
echo ""
echo "使用Docker Hub镜像部署:"
echo "  mkdir -p data/uploads data/output data/logs"
echo "  docker-compose -f docker-compose.hub.yml up -d"
echo ""
echo "Docker Hub地址:"
echo "  https://hub.docker.com/r/${DOCKER_USERNAME}/${PROJECT_NAME}-backend"
echo "  https://hub.docker.com/r/${DOCKER_USERNAME}/${PROJECT_NAME}-frontend"
echo "===========================================" 