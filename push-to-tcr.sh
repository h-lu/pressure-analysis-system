#!/bin/bash
# 推送Docker镜像到腾讯云容器镜像服务(TCR)
# 使用前需要先在腾讯云控制台创建命名空间和镜像仓库

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 腾讯云容器镜像服务(TCR)推送脚本${NC}"
echo "============================================"

# 获取用户输入
read -p "请输入TCR实例域名 (例如: your-instance.tencentcloudcr.com): " TCR_DOMAIN
read -p "请输入命名空间 (例如: pressure-system): " NAMESPACE
read -p "请输入镜像名称 (默认: pressure-analysis): " IMAGE_NAME
read -p "请输入镜像标签 (默认: latest): " TAG

# 设置默认值
IMAGE_NAME=${IMAGE_NAME:-pressure-analysis}
TAG=${TAG:-latest}

# 验证输入
if [ -z "$TCR_DOMAIN" ] || [ -z "$NAMESPACE" ]; then
    echo -e "${RED}错误: TCR域名和命名空间不能为空${NC}"
    exit 1
fi

# 构造完整的镜像地址
FULL_IMAGE_NAME="$TCR_DOMAIN/$NAMESPACE/$IMAGE_NAME:$TAG"
LOCAL_IMAGE_NAME="$IMAGE_NAME:$TAG"

echo ""
echo -e "${YELLOW}📋 配置信息:${NC}"
echo "  TCR域名: $TCR_DOMAIN"
echo "  命名空间: $NAMESPACE"
echo "  镜像名称: $IMAGE_NAME"
echo "  标签: $TAG"
echo "  完整地址: $FULL_IMAGE_NAME"
echo ""

# 检查Docker是否登录TCR
echo -e "${BLUE}🔐 检查TCR登录状态...${NC}"
if ! docker login $TCR_DOMAIN 2>/dev/null; then
    echo -e "${YELLOW}需要登录TCR，请输入访问凭证:${NC}"
    echo "提示: 在腾讯云控制台 -> 容器镜像服务 -> 访问凭证 中获取"
    docker login $TCR_DOMAIN
fi

# 构建镜像
echo -e "${GREEN}🔨 构建Docker镜像...${NC}"
docker build -t $LOCAL_IMAGE_NAME .

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 镜像构建成功${NC}"
else
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
fi

# 标记镜像
echo -e "${BLUE}🏷️  标记镜像...${NC}"
docker tag $LOCAL_IMAGE_NAME $FULL_IMAGE_NAME

# 推送镜像
echo -e "${GREEN}📤 推送镜像到TCR...${NC}"
docker push $FULL_IMAGE_NAME

# 检查推送是否成功
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 镜像推送成功!${NC}"
    echo ""
    echo -e "${YELLOW}📝 后续步骤:${NC}"
    echo "1. 在TKE中部署应用时使用镜像地址: $FULL_IMAGE_NAME"
    echo "2. 或者修改 k8s-deployment.yaml 中的镜像地址"
    echo "3. 使用以下命令部署到TKE:"
    echo "   kubectl apply -f k8s-deployment.yaml"
    
    # 生成部署命令
    echo ""
    echo -e "${BLUE}🚀 快速部署命令:${NC}"
    echo "# 更新deployment中的镜像地址"
    echo "sed -i 's|ccr.ccs.tencentyun.com/your-namespace/pressure-analysis:latest|$FULL_IMAGE_NAME|g' k8s-deployment.yaml"
    echo ""
    echo "# 部署到Kubernetes"
    echo "kubectl apply -f k8s-deployment.yaml"
    
else
    echo -e "${RED}❌ 镜像推送失败${NC}"
    exit 1
fi

# 清理本地镜像标签（可选）
read -p "是否清理本地镜像标签? (y/N): " CLEANUP
if [[ $CLEANUP =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理本地镜像标签...${NC}"
    docker rmi $FULL_IMAGE_NAME || true
    echo -e "${GREEN}✅ 清理完成${NC}"
fi

echo ""
echo -e "${GREEN}🎉 操作完成!${NC}"
echo -e "${BLUE}💡 提示: 可以在腾讯云控制台的容器镜像服务中查看推送的镜像${NC}" 