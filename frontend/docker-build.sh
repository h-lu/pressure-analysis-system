#!/bin/bash

# 压力采集数据分析系统 - 前端Docker构建脚本

set -e

echo "🚀 开始构建前端Docker镜像..."

# 设置构建参数
BUILD_ARGS=""

# 生产环境配置
if [ "$NODE_ENV" = "production" ]; then
    echo "📦 生产环境构建"
    BUILD_ARGS="--build-arg NODE_ENV=production"
    BUILD_ARGS="$BUILD_ARGS --build-arg VITE_API_BASE_URL="
else
    echo "🔧 开发环境构建"
    BUILD_ARGS="--build-arg NODE_ENV=development"
    BUILD_ARGS="$BUILD_ARGS --build-arg VITE_API_BASE_URL=http://localhost:8000"
fi

# 构建镜像
docker build \
    $BUILD_ARGS \
    -f Dockerfile.frontend \
    -t pressure-analysis-frontend:latest \
    .

echo "✅ 前端Docker镜像构建完成！"

# 显示镜像信息
docker images | grep pressure-analysis-frontend 