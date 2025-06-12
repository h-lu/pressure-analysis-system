#!/bin/bash

echo "启动压力分析系统..."
echo "================================"

# 检查可执行文件是否存在
if [ ! -f "dist/压力分析系统" ]; then
    echo "错误: 可执行文件不存在，请先运行打包脚本"
    echo "运行: python quick_build.py"
    exit 1
fi

# 给可执行文件添加执行权限
chmod +x "dist/压力分析系统"

echo "正在启动应用程序..."
echo "应用程序将在浏览器中自动打开"
echo "如果没有自动打开，请手动访问: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止应用程序"
echo "================================"

# 运行应用程序
"./dist/压力分析系统" 