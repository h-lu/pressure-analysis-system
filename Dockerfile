# 压力采集数据分析系统 Docker 镜像
# 多阶段构建: 前端构建 -> 后端运行时

# ================================
# 阶段1: 前端构建
# ================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖（包括开发依赖用于构建）
RUN npm ci

# 复制前端源码
COPY frontend/ ./

# 构建前端静态文件
RUN npm run build

# ================================
# 阶段2: 后端运行时
# ================================
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装完整的系统依赖，以确保R包能正确编译
# 增加编译工具和多个dev库
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # System essentials
    build-essential \
    # Networking tools for debugging and SSL certificates
    curl \
    iputils-ping \
    ca-certificates \
    # 时区设置工具
    tzdata \
    # Python C extension build dependencies
    libssl-dev \
    libffi-dev \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    libcairo2-dev \
    libgit2-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg62-turbo-dev \
    locales \
    fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

# 设置时区为上海时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置环境变量以支持中文
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8
ENV DEEPSEEK_API_KEY="your_deepseek_api_key_here"

# 预安装R包，使用最可靠的官方CRAN镜像
RUN R -e "install.packages(c('tidyverse', 'readr', 'ggplot2', 'dplyr', 'slider', 'broom', 'GGally', 'plotly', 'patchwork', 'cluster', 'jsonlite'), repos='https://cloud.r-project.org/')" && \
    R -e "if(!require('tidyverse')) { quit(status=1, save='no') }"

# 复制并安装Python依赖
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制后端代码
COPY backend/ ./backend/
COPY run_server.py ./

# 从前端构建阶段复制静态文件到正确位置
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# 创建必要的目录
RUN mkdir -p backend/uploads backend/output 临时文件

# 设置环境变量
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动应用
CMD ["python", "run_server.py"] 