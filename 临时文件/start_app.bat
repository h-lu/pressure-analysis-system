@echo off
chcp 65001 >nul

echo 启动压力分析系统...
echo ================================

REM 检查可执行文件是否存在
if not exist "dist\压力分析系统.exe" (
    echo 错误: 可执行文件不存在，请先运行打包脚本
    echo 运行: python quick_build.py
    pause
    exit /b 1
)

echo 正在启动应用程序...
echo 应用程序将在浏览器中自动打开
echo 如果没有自动打开，请手动访问: http://localhost:8000
echo.
echo 按 Ctrl+C 停止应用程序
echo ================================

REM 运行应用程序
"dist\压力分析系统.exe"

pause 