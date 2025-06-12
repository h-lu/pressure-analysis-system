#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力分析系统打包脚本
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from build_config import *

class BuildManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        BUILD_DIR.mkdir(exist_ok=True)
        DIST_DIR.mkdir(exist_ok=True)
        
    def run_command(self, command, cwd=None, shell=True):
        """执行命令并处理错误"""
        print(f"执行命令: {command}")
        if cwd:
            print(f"工作目录: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            if e.stdout:
                print(f"标准输出: {e.stdout}")
            if e.stderr:
                print(f"错误输出: {e.stderr}")
            return False
    
    def check_dependencies(self):
        """检查必要的依赖"""
        print("检查依赖...")
        
        # 检查Node.js
        if not self.run_command("node --version"):
            print("错误: 未找到Node.js，请先安装Node.js")
            return False
        
        # 检查npm
        if not self.run_command("npm --version"):
            print("错误: 未找到npm，请先安装npm")
            return False
        
        # 检查Python
        if not self.run_command("python --version"):
            print("错误: 未找到Python，请先安装Python")
            return False
        
        print("依赖检查完成")
        return True
    
    def install_build_dependencies(self):
        """安装打包依赖"""
        print("安装打包依赖...")
        
        # 安装PyInstaller
        if not self.run_command("pip install pyinstaller"):
            print("错误: PyInstaller安装失败")
            return False
        
        # 安装后端依赖
        if not self.run_command("pip install -r requirements.txt", cwd=BACKEND_DIR):
            print("错误: 后端依赖安装失败")
            return False
        
        # 安装前端依赖
        if not self.run_command("npm install", cwd=FRONTEND_DIR):
            print("错误: 前端依赖安装失败")
            return False
        
        print("依赖安装完成")
        return True
    
    def build_frontend(self):
        """构建前端"""
        print("构建前端...")
        
        # 清理之前的构建
        dist_path = FRONTEND_DIR / "dist"
        if dist_path.exists():
            shutil.rmtree(dist_path)
        
        # 构建前端
        if not self.run_command("npm run build", cwd=FRONTEND_DIR):
            print("错误: 前端构建失败")
            return False
        
        # 检查构建结果
        if not dist_path.exists():
            print("错误: 前端构建产物不存在")
            return False
        
        print("前端构建完成")
        return True
    
    def create_main_entry(self):
        """创建主入口文件"""
        print("创建主入口文件...")
        
        main_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力分析系统主入口文件
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# 添加当前目录到Python路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    application_path = Path(sys.executable).parent
    sys.path.insert(0, str(application_path))
else:
    # 如果是开发环境
    application_path = Path(__file__).parent
    sys.path.insert(0, str(application_path / "backend"))

# 设置环境变量
os.environ["PYTHONPATH"] = str(application_path)

def setup_static_files():
    """设置静态文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        static_dir = application_path / "static"
        frontend_dir = application_path / "frontend_dist"
        r_analysis_dir = application_path / "r_analysis"
    else:
        # 开发环境
        static_dir = application_path / "backend" / "static"
        frontend_dir = application_path / "frontend" / "dist"
        r_analysis_dir = application_path / "backend" / "r_analysis"
    
    # 确保目录存在
    static_dir.mkdir(exist_ok=True)
    (static_dir / "charts").mkdir(exist_ok=True)
    (static_dir / "reports").mkdir(exist_ok=True)
    
    return static_dir, frontend_dir, r_analysis_dir

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open("http://localhost:8000")

def main():
    """主函数"""
    print("=" * 50)
    print("压力分析系统 v1.0.0")
    print("=" * 50)
    
    # 设置静态文件路径
    static_dir, frontend_dir, r_analysis_dir = setup_static_files()
    
    print(f"应用路径: {application_path}")
    print(f"静态文件路径: {static_dir}")
    print(f"前端文件路径: {frontend_dir}")
    print(f"R分析路径: {r_analysis_dir}")
    
    # 检查必要文件
    if not frontend_dir.exists():
        print(f"错误: 前端文件不存在: {frontend_dir}")
        input("按回车键退出...")
        return
    
    if not r_analysis_dir.exists():
        print(f"错误: R分析文件不存在: {r_analysis_dir}")
        input("按回车键退出...")
        return
    
    # 启动浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("正在启动服务器...")
    print("服务器地址: http://localhost:8000")
    print("按 Ctrl+C 停止服务器")
    
    try:
        # 导入并启动FastAPI应用
        import uvicorn
        from backend.main import app
        
        # 配置静态文件服务
        from fastapi.staticfiles import StaticFiles
        
        # 挂载前端静态文件
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
        
        # 启动服务器
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
'''
        
        main_file = BASE_DIR / "main.py"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        print("主入口文件创建完成")
        return True
    
    def create_spec_file(self):
        """创建PyInstaller spec文件"""
        print("创建PyInstaller spec文件...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# 项目路径
base_dir = Path(r"{BASE_DIR}")
backend_dir = base_dir / "backend"
frontend_dir = base_dir / "frontend"

# 数据文件
datas = [
    (str(backend_dir / "r_analysis"), "r_analysis"),
    (str(backend_dir / "static"), "static"),
    (str(frontend_dir / "dist"), "frontend_dist"),
]

# 二进制文件
binaries = []

# 隐藏导入
hiddenimports = {HIDDEN_IMPORTS}

a = Analysis(
    ['main.py'],
    pathex=[str(base_dir), str(backend_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={EXCLUDES},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{EXECUTABLE_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        spec_file = BASE_DIR / f"{EXECUTABLE_NAME}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print("spec文件创建完成")
        return spec_file
    
    def build_executable(self):
        """构建可执行文件"""
        print("构建可执行文件...")
        
        # 创建spec文件
        spec_file = self.create_spec_file()
        
        # 使用PyInstaller构建
        command = f"pyinstaller {spec_file}"
        if not self.run_command(command, cwd=BASE_DIR):
            print("错误: 可执行文件构建失败")
            return False
        
        # 检查构建结果
        if self.system == "windows":
            exe_name = f"{EXECUTABLE_NAME}.exe"
        else:
            exe_name = EXECUTABLE_NAME
        
        exe_path = BASE_DIR / "dist" / exe_name
        if not exe_path.exists():
            print(f"错误: 可执行文件不存在: {exe_path}")
            return False
        
        print(f"可执行文件构建完成: {exe_path}")
        return True
    
    def create_installer_script(self):
        """创建安装脚本"""
        print("创建安装脚本...")
        
        if self.system == "windows":
            # Windows批处理脚本
            installer_content = f'''@echo off
echo 压力分析系统安装程序
echo.

set INSTALL_DIR=%USERPROFILE%\\{PROJECT_NAME}
echo 安装目录: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 复制文件...
copy "{EXECUTABLE_NAME}.exe" "%INSTALL_DIR%\\"
copy "README.md" "%INSTALL_DIR%\\"

echo 创建桌面快捷方式...
set DESKTOP=%USERPROFILE%\\Desktop
echo [InternetShortcut] > "%DESKTOP%\\{PROJECT_NAME}.url"
echo URL=file:///%INSTALL_DIR%\\{EXECUTABLE_NAME}.exe >> "%DESKTOP%\\{PROJECT_NAME}.url"

echo 安装完成！
echo 可执行文件位置: %INSTALL_DIR%\\{EXECUTABLE_NAME}.exe
pause
'''
            installer_file = BASE_DIR / "install.bat"
        else:
            # Unix shell脚本
            installer_content = f'''#!/bin/bash
echo "压力分析系统安装程序"
echo

INSTALL_DIR="$HOME/{PROJECT_NAME}"
echo "安装目录: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"

echo "复制文件..."
cp "{EXECUTABLE_NAME}" "$INSTALL_DIR/"
cp "README.md" "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/{EXECUTABLE_NAME}"

echo "创建桌面快捷方式..."
DESKTOP="$HOME/Desktop"
if [ -d "$DESKTOP" ]; then
    cat > "$DESKTOP/{PROJECT_NAME}.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name={PROJECT_NAME}
Comment={PROJECT_DESCRIPTION}
Exec=$INSTALL_DIR/{EXECUTABLE_NAME}
Icon=application-x-executable
Terminal=true
Categories=Utility;
EOF
    chmod +x "$DESKTOP/{PROJECT_NAME}.desktop"
fi

echo "安装完成！"
echo "可执行文件位置: $INSTALL_DIR/{EXECUTABLE_NAME}"
read -p "按回车键继续..."
'''
            installer_file = BASE_DIR / "install.sh"
        
        with open(installer_file, 'w', encoding='utf-8') as f:
            f.write(installer_content)
        
        if self.system != "windows":
            os.chmod(installer_file, 0o755)
        
        print(f"安装脚本创建完成: {installer_file}")
        return True
    
    def create_package(self):
        """创建发布包"""
        print("创建发布包...")
        
        # 创建发布目录
        release_dir = BASE_DIR / "release"
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()
        
        # 复制可执行文件
        if self.system == "windows":
            exe_name = f"{EXECUTABLE_NAME}.exe"
        else:
            exe_name = EXECUTABLE_NAME
        
        src_exe = BASE_DIR / "dist" / exe_name
        dst_exe = release_dir / exe_name
        shutil.copy2(src_exe, dst_exe)
        
        # 复制文档
        docs_to_copy = ["README.md", "使用说明.md", "使用指南.md"]
        for doc in docs_to_copy:
            doc_path = BASE_DIR / doc
            if doc_path.exists():
                shutil.copy2(doc_path, release_dir)
        
        # 复制示例数据
        demo_files = ["demo_data.csv", "test_data.csv"]
        for demo in demo_files:
            demo_path = BASE_DIR / demo
            if demo_path.exists():
                shutil.copy2(demo_path, release_dir)
        
        # 复制安装脚本
        if self.system == "windows":
            install_script = BASE_DIR / "install.bat"
        else:
            install_script = BASE_DIR / "install.sh"
        
        if install_script.exists():
            shutil.copy2(install_script, release_dir)
        
        print(f"发布包创建完成: {release_dir}")
        return release_dir
    
    def build_all(self):
        """完整构建流程"""
        print("开始完整构建流程...")
        
        steps = [
            ("检查依赖", self.check_dependencies),
            ("安装构建依赖", self.install_build_dependencies),
            ("构建前端", self.build_frontend),
            ("创建主入口文件", self.create_main_entry),
            ("构建可执行文件", self.build_executable),
            ("创建安装脚本", self.create_installer_script),
            ("创建发布包", self.create_package),
        ]
        
        for step_name, step_func in steps:
            print(f"\\n{'='*20} {step_name} {'='*20}")
            if not step_func():
                print(f"构建失败: {step_name}")
                return False
        
        print("\\n" + "="*50)
        print("构建完成！")
        print("="*50)
        
        # 显示构建结果
        release_dir = BASE_DIR / "release"
        if release_dir.exists():
            print(f"发布包位置: {release_dir}")
            print("发布包内容:")
            for item in release_dir.iterdir():
                print(f"  - {item.name}")
        
        return True

def main():
    """主函数"""
    print("压力分析系统打包工具")
    print("="*50)
    
    builder = BuildManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "frontend":
            builder.build_frontend()
        elif command == "backend":
            builder.build_executable()
        elif command == "package":
            builder.create_package()
        elif command == "clean":
            # 清理构建文件
            for dir_to_clean in [BUILD_DIR, DIST_DIR, BASE_DIR / "release"]:
                if dir_to_clean.exists():
                    shutil.rmtree(dir_to_clean)
                    print(f"已清理: {dir_to_clean}")
        else:
            print(f"未知命令: {command}")
            print("可用命令: frontend, backend, package, clean")
    else:
        # 完整构建
        builder.build_all()

if __name__ == "__main__":
    main() 