#!/usr/bin/env python3
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
