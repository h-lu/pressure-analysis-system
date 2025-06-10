# 腾讯云部署快速开始指南

## 🚀 3分钟快速部署

### 方案选择

| 方案 | 难度 | 成本 | 适用场景 |
|------|------|------|----------|
| 轻量应用服务器 | ⭐ | ¥30-100/月 | 个人/小团队 |
| 云服务器CVM | ⭐⭐ | ¥100-300/月 | 中小企业 |
| 容器服务TKE | ⭐⭐⭐ | ¥200-500/月 | 企业级 |

## 🎯 方案一：轻量应用服务器（推荐新手）

### 第一步：创建服务器
1. 登录[腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入轻量应用服务器
3. 创建实例：
   - **应用镜像**: Docker CE
   - **实例套餐**: 2核4G（¥60/月）
   - **系统盘**: 40GB SSD

### 第二步：配置安全组
1. 点击实例 → 防火墙
2. 添加规则：
   ```
   端口: 8000
   协议: TCP
   策略: 允许
   来源: 0.0.0.0/0
   ```

### 第三步：一键部署
```bash
# SSH连接到服务器
ssh lighthouse@your-server-ip

# 下载并运行部署脚本
wget https://raw.githubusercontent.com/h-lu/pressure-analysis-system/main/tencent-deploy.sh
chmod +x tencent-deploy.sh
./tencent-deploy.sh
```

**部署完成！** 访问 `http://your-server-ip:8000`

---

## 🏢 方案二：容器服务TKE（企业级）

### 第一步：创建TKE集群
1. 进入容器服务TKE控制台
2. 创建集群：
   - **集群类型**: 托管集群
   - **节点规格**: 2核4G
   - **节点数量**: 2个

### 第二步：推送镜像到TCR
```bash
# 克隆项目
git clone https://github.com/h-lu/pressure-analysis-system.git
cd pressure-analysis-system

# 运行推送脚本
./push-to-tcr.sh
```

### 第三步：部署应用
```bash
# 配置API Key (base64编码)
echo -n "your_deepseek_api_key" | base64

# 编辑k8s-deployment.yaml，替换：
# 1. 镜像地址
# 2. base64编码的API key

# 部署到集群
kubectl apply -f k8s-deployment.yaml

# 查看状态
kubectl get pods
kubectl get services
```

详细部署指南请查看 [tencent-cloud-deploy.md](./tencent-cloud-deploy.md)