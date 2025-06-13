#!/bin/bash

# 压力采集数据分析系统 - Docker部署脚本

set -e  # 遇到错误立即退出

echo "===========================================" 
echo "压力采集数据分析系统 Docker部署脚本"
echo "==========================================="

# 启用Docker BuildKit以获得更快的构建速度
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建必要的数据目录
echo "创建数据目录..."
mkdir -p data/uploads data/output data/logs

# 设置目录权限
echo "设置目录权限..."
chmod 755 data/uploads data/output data/logs

# DeepSeek AI配置通过前端系统设置页面进行，无需.env文件
echo "提示: DeepSeek AI配置请在前端系统设置页面进行配置"

# 清理现有容器和镜像（可选）
if [ "$1" = "--clean" ]; then
    echo "清理现有容器和镜像..."
    docker-compose down --remove-orphans --volumes || true
    docker system prune -f
    docker volume prune -f
fi

# 停止现有容器
echo "停止现有容器..."
docker-compose down --remove-orphans || true

# 并行构建镜像以提高速度
echo "并行构建镜像..."
docker-compose build --parallel

# 启动服务
echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 快速健康检查
echo "执行健康检查..."

# 检查后端服务
echo "检查后端服务..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✓ 后端服务健康"
        break
    else
        echo "等待后端服务启动... ($i/5)"
        sleep 5
    fi
    if [ $i -eq 5 ]; then
        echo "✗ 后端服务启动失败，查看日志："
        docker-compose logs --tail=20 backend
        exit 1
    fi
done

# 检查前端服务
echo "检查前端服务..."
for i in {1..3}; do
    if curl -f http://localhost/ >/dev/null 2>&1; then
        echo "✓ 前端服务健康"
        break
    else
        echo "等待前端服务启动... ($i/3)"
        sleep 3
    fi
    if [ $i -eq 3 ]; then
        echo "✗ 前端服务启动失败，查看日志："
        docker-compose logs --tail=20 frontend
        exit 1
    fi
done

echo "==========================================="
echo "部署成功！"
echo ""
echo "访问地址:"
echo "  前端应用: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "管理命令:"
echo "  查看日志: docker-compose logs -f [service]"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
echo "重要提示:"
echo "  - 系统包含中文字体支持，支持中文图表生成"
echo "  - DeepSeek AI配置请在前端系统设置页面进行"
echo "  - 数据文件存储在 ./data 目录下"
echo "===========================================" 