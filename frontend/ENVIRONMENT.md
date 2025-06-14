# 前端环境配置说明

## 环境变量配置

前端应用支持通过环境变量进行配置，以适应不同的部署环境。

### 支持的环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `VITE_API_BASE_URL` | API基础URL | 开发环境: `http://localhost:8000`<br>生产环境: `""` (相对路径) | `http://localhost:8000` |
| `VITE_APP_TITLE` | 应用标题 | `压力采集数据分析系统` | `压力采集数据分析系统` |
| `VITE_APP_VERSION` | 应用版本 | `1.0.0` | `1.0.0` |
| `VITE_DEBUG` | 调试模式 | `false` | `true` |

### 环境配置

#### 开发环境

创建 `.env` 文件：

```bash
# 开发环境配置
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=压力采集数据分析系统
VITE_APP_VERSION=1.0.0
VITE_DEBUG=true
```

#### 生产环境

生产环境中，API通过nginx反向代理，使用相对路径：

```bash
# 生产环境配置
VITE_API_BASE_URL=
VITE_APP_TITLE=压力采集数据分析系统
VITE_APP_VERSION=1.0.0
VITE_DEBUG=false
```

### Docker部署配置

#### 使用docker-compose

在 `docker-compose.yml` 中配置环境变量：

```yaml
services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      args:
        - VITE_API_BASE_URL=
        - VITE_APP_TITLE=压力采集数据分析系统
        - VITE_APP_VERSION=1.0.0
```

#### 使用构建脚本

```bash
# 生产环境构建
NODE_ENV=production ./frontend/docker-build.sh

# 开发环境构建
NODE_ENV=development ./frontend/docker-build.sh
```

### API配置说明

#### 开发环境
- 前端运行在 `http://localhost:5173`
- 后端运行在 `http://localhost:8000`
- 前端直接访问后端API

#### 生产环境（Docker + Nginx）
- 前端和后端都运行在Docker容器中
- Nginx作为反向代理，统一处理前端静态文件和API请求
- 前端使用相对路径访问API，通过nginx代理到后端

### 网络架构

```
生产环境:
浏览器 -> Nginx (80端口) -> 前端静态文件 (Vue.js)
                        -> API请求 (/api/*) -> 后端 (8000端口)

开发环境:
浏览器 -> 前端开发服务器 (5173端口) -> API请求 -> 后端 (8000端口)
```

### 故障排除

1. **API请求失败**
   - 检查 `VITE_API_BASE_URL` 配置是否正确
   - 确认后端服务是否正常运行
   - 检查nginx配置是否正确代理API请求

2. **开发环境跨域问题**
   - 确认vite.config.js中的proxy配置
   - 或者设置 `VITE_API_BASE_URL=http://localhost:8000`

3. **生产环境API访问问题**
   - 确认nginx配置中的upstream和proxy_pass设置
   - 检查Docker网络配置
   - 确认 `VITE_API_BASE_URL` 为空字符串或未设置 