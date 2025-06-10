# 腾讯云部署指南

## 方案一：腾讯云容器服务 TKE 部署（推荐）

### 1. 准备工作

1. **注册腾讯云账号**并完成实名认证
2. **开通以下服务**：
   - 容器镜像服务（TCR）
   - 容器服务（TKE）
   - 云服务器（CVM）
   - 负载均衡（CLB）

### 2. 创建容器镜像仓库

```bash
# 登录腾讯云容器镜像服务
docker login ccr.ccs.tencentyun.com

# 构建并推送镜像
docker build -t pressure-analysis .
docker tag pressure-analysis ccr.ccs.tencentyun.com/your-namespace/pressure-analysis:latest
docker push ccr.ccs.tencentyun.com/your-namespace/pressure-analysis:latest
```

### 3. 创建 TKE 集群

1. 登录腾讯云控制台
2. 进入容器服务 TKE
3. 创建集群：
   - 选择托管集群
   - 配置网络（VPC/子网）
   - 选择节点规格（推荐2核4G以上）

### 4. 部署应用

创建 `k8s-deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pressure-analysis
  labels:
    app: pressure-analysis
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pressure-analysis
  template:
    metadata:
      labels:
        app: pressure-analysis
    spec:
      containers:
      - name: pressure-analysis
        image: ccr.ccs.tencentyun.com/your-namespace/pressure-analysis:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEEPSEEK_API_KEY
          valueFrom:
            secretKeyRef:
              name: pressure-secrets
              key: deepseek-api-key
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        - name: DEBUG
          value: "false"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: pressure-analysis-service
spec:
  selector:
    app: pressure-analysis
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: pressure-secrets
type: Opaque
data:
  deepseek-api-key: <base64-encoded-api-key>
```

部署命令：
```bash
kubectl apply -f k8s-deployment.yaml
```

## 方案二：腾讯云轻量应用服务器（简单快速）

### 1. 创建轻量应用服务器

1. 选择Docker应用镜像
2. 配置规格（推荐2核4G，40GB存储）
3. 配置网络和安全组

### 2. 连接服务器并部署

```bash
# SSH连接到服务器
ssh lighthouse@your-server-ip

# 克隆项目
git clone https://github.com/h-lu/pressure-analysis-system.git
cd pressure-analysis-system

# 设置环境变量
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env

# 使用Docker Compose部署
docker-compose up -d

# 查看状态
docker-compose ps
```

### 3. 配置安全组

开放端口：
- 8000（应用端口）
- 22（SSH管理）
- 80/443（HTTP/HTTPS，可选）

## 方案三：腾讯云服务器 CVM 部署

### 1. 创建云服务器

1. 选择操作系统：Ubuntu 20.04 LTS
2. 配置规格：
   - CPU: 2核以上
   - 内存: 4GB以上
   - 存储: 40GB以上
3. 配置网络和安全组

### 2. 安装环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重启登录以应用用户组更改
logout
```

### 3. 部署应用

```bash
# 重新SSH连接
ssh username@your-server-ip

# 克隆项目
git clone https://github.com/h-lu/pressure-analysis-system.git
cd pressure-analysis-system

# 配置环境变量
export DEEPSEEK_API_KEY="your_api_key_here"

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
docker-compose logs
```

## 方案四：腾讯云 Serverless（按需付费）

### 1. 使用腾讯云函数 SCF

创建 `serverless.yml`：

```yaml
service: pressure-analysis

provider:
  name: tencent
  runtime: Custom
  region: ap-guangzhou

functions:
  pressure-analysis:
    handler: index.main_handler
    runtime: CustomRuntime
    environment:
      DEEPSEEK_API_KEY: ${env:DEEPSEEK_API_KEY}
    events:
      - apigw:
          path: /
          method: ANY
      - apigw:
          path: /{proxy+}
          method: ANY

package:
  exclude:
    - .git/**
    - node_modules/**
    - __pycache__/**
```

### 2. 使用 Serverless Framework 部署

```bash
# 安装 Serverless Framework
npm install -g serverless

# 配置腾讯云凭证
serverless config credentials --provider tencent --key <your-key> --secret <your-secret>

# 部署
serverless deploy
```

## 性能优化建议

### 1. 镜像优化

```dockerfile
# 多阶段构建优化
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
# ... 其他配置
# 只复制生产文件
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/
```

### 2. 资源配置

- **开发环境**: 1核2G
- **生产环境**: 2核4G
- **高并发环境**: 4核8G + 负载均衡

### 3. 数据持久化

```yaml
# 使用腾讯云CFS文件存储
volumes:
  - name: data-storage
    persistentVolumeClaim:
      claimName: pressure-data-pvc
```

## 监控和日志

### 1. 使用腾讯云监控

```yaml
# 添加健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 2. 日志收集

```bash
# 查看容器日志
docker-compose logs -f

# 使用腾讯云日志服务CLS
# 在控制台配置日志收集规则
```

## 域名和SSL

### 1. 绑定域名

1. 在腾讯云DNS解析添加A记录
2. 指向服务器公网IP
3. 配置CDN加速（可选）

### 2. 配置SSL证书

```bash
# 使用Let's Encrypt免费SSL
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 配置Nginx反向代理
sudo apt install nginx
```

Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 成本估算

| 方案 | 月费用估算 | 适用场景 |
|------|------------|----------|
| 轻量应用服务器 | ¥30-100 | 个人项目、小团队 |
| CVM + 负载均衡 | ¥100-300 | 中小企业 |
| TKE托管集群 | ¥200-500 | 企业级应用 |
| Serverless | 按使用量计费 | 低频访问应用 |

选择建议：
- **初学者/个人**: 轻量应用服务器
- **小团队**: CVM方案
- **企业应用**: TKE容器服务
- **成本敏感**: Serverless方案 