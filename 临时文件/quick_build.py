#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力分析系统快速打包脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """执行命令"""
    print(f"执行: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return False

def main():
    """主函数"""
    base_dir = Path(__file__).parent
    frontend_dir = base_dir / "frontend"
    
    print("压力分析系统快速打包")
    print("=" * 40)
    
    # 1. 构建前端
    print("\n1. 构建前端...")
    if not run_command("npm run build", cwd=frontend_dir):
        print("前端构建失败")
        return False
    
    # 2. 安装PyInstaller（如果没有）
    print("\n2. 检查PyInstaller...")
    run_command("pip install pyinstaller")
    
    # 3. 检查主入口文件
    print("\n3. 检查主入口文件...")
    main_file = base_dir / "app_main.py"
    if not main_file.exists():
        print("创建主入口文件...")
        main_content = '''#!/usr/bin/env python3
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

def main():
    print("压力分析系统 v1.0.0")
    print("服务器启动中...")
    
    # 启动浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        import uvicorn
        from backend.main import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
'''
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
    else:
        print("主入口文件已存在，跳过创建")
    
    # 4. 使用PyInstaller打包
    print("\n4. 打包可执行文件...")
    import platform
    sep = ";" if platform.system() == "Windows" else ":"
    command = f'''pyinstaller --onefile --name="压力分析系统" --add-data="frontend/dist{sep}frontend_dist" --add-data="backend/r_analysis{sep}r_analysis" --add-data="backend/static{sep}static" --hidden-import=uvicorn --hidden-import=fastapi --hidden-import=pandas --hidden-import=numpy --hidden-import=rpy2 app_main.py'''
    
    if not run_command(command, cwd=base_dir):
        print("打包失败")
        return False
    
    print("\n打包完成！")
    print(f"可执行文件位置: {base_dir / 'dist'}")
    
    return True

if __name__ == "__main__":
    main() 