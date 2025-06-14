# 部署配置说明

## 环境变量配置

### 前端端口配置

您可以通过环境变量 `FRONTEND_PORT` 来设置前端访问端口：

#### 方法1: 使用 .env 文件

1. 复制环境变量示例文件：
```bash
cp env.example .env
```

2. 编辑 `.env` 文件，设置前端端口：
```bash
# 前端访问端口 (默认: 80)
FRONTEND_PORT=8080  # 修改为您想要的端口
```

3. 启动服务：
```bash
docker-compose up -d
```

#### 方法2: 直接设置环境变量

```bash
# 设置前端端口为8080
FRONTEND_PORT=8080 docker-compose up -d

# 或者导出环境变量
export FRONTEND_PORT=8080
docker-compose up -d
```

#### 方法3: 修改 docker-compose.yml

直接编辑 `docker-compose.yml` 文件中的端口映射：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 将80改为您想要的端口
```

### 常用端口配置示例

| 用途 | 端口 | 配置 |
|------|------|------|
| 默认HTTP | 80 | `FRONTEND_PORT=80` |
| 开发环境 | 8080 | `FRONTEND_PORT=8080` |
| 测试环境 | 3000 | `FRONTEND_PORT=3000` |
| 生产环境 | 80 | `FRONTEND_PORT=80` |

### 完整部署流程

1. **克隆项目**
```bash
git clone <repository-url>
cd pressure-analysis-system
```

2. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，设置所需的配置
```

3. **启动服务**
```bash
# 使用默认端口 (80)
docker-compose up -d

# 或使用自定义端口
FRONTEND_PORT=8080 docker-compose up -d
```

4. **访问应用**
- 前端: `http://localhost:端口号`
- 后端API: `http://localhost:8000`
- API文档: `http://localhost:8000/docs`

### 注意事项

1. **端口冲突**: 确保选择的端口没有被其他服务占用
2. **防火墙**: 确保防火墙允许访问选择的端口
3. **反向代理**: 如果使用nginx等反向代理，需要相应调整配置
4. **SSL/HTTPS**: 生产环境建议配置HTTPS

### 故障排除

#### 端口被占用
```bash
# 查看端口占用情况
lsof -i :80
netstat -tulpn | grep :80

# 停止占用端口的服务或选择其他端口
```

#### 容器启动失败
```bash
# 查看容器日志
docker-compose logs frontend
docker-compose logs backend

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 无法访问服务
1. 检查容器状态：`docker-compose ps`
2. 检查端口映射：`docker port pressure-frontend-fast`
3. 检查防火墙设置
4. 检查网络连接

### 高级配置

#### 使用自定义域名

1. 配置DNS解析到服务器IP
2. 修改nginx配置（如果需要）
3. 配置SSL证书（推荐使用Let's Encrypt）

#### 负载均衡

如果需要部署多个实例，可以使用nginx或其他负载均衡器：

```nginx
upstream pressure_frontend {
    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://pressure_frontend;
    }
}
``` 