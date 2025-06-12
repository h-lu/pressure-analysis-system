#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建发布包脚本
"""

import os
import shutil
import platform
from pathlib import Path
from datetime import datetime

def create_release_package():
    """创建发布包"""
    base_dir = Path(__file__).parent
    release_dir = base_dir / "release"
    
    print("创建发布包...")
    print("=" * 40)
    
    # 清理并创建发布目录
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    system = platform.system().lower()
    
    # 复制可执行文件
    if system == "windows":
        exe_name = "压力分析系统.exe"
        start_script = "start_app.bat"
    else:
        exe_name = "压力分析系统"
        start_script = "start_app.sh"
    
    exe_path = base_dir / "dist" / exe_name
    if not exe_path.exists():
        print(f"错误: 可执行文件不存在: {exe_path}")
        print("请先运行: python quick_build.py")
        return False
    
    # 复制文件到发布目录
    print("复制可执行文件...")
    shutil.copy2(exe_path, release_dir / exe_name)
    
    print("复制启动脚本...")
    start_script_path = base_dir / start_script
    if start_script_path.exists():
        shutil.copy2(start_script_path, release_dir / start_script)
        if system != "windows":
            os.chmod(release_dir / start_script, 0o755)
    
    # 复制文档
    print("复制文档...")
    docs = ["README.md", "使用说明.md", "使用指南.md", "打包说明.md"]
    for doc in docs:
        doc_path = base_dir / doc
        if doc_path.exists():
            shutil.copy2(doc_path, release_dir / doc)
    
    # 复制示例数据
    print("复制示例数据...")
    demo_files = ["demo_data.csv", "test_data.csv"]
    for demo in demo_files:
        demo_path = base_dir / demo
        if demo_path.exists():
            shutil.copy2(demo_path, release_dir / demo)
    
    # 创建版本信息文件
    print("创建版本信息...")
    version_info = f"""压力分析系统 v1.0.0
构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统平台: {platform.system()} {platform.machine()}
Python版本: {platform.python_version()}

文件说明:
- {exe_name}: 主程序可执行文件
- {start_script}: 启动脚本
- README.md: 项目说明
- 使用说明.md: 使用指南
- demo_data.csv: 示例数据文件

使用方法:
1. 确保系统已安装R语言环境
2. 运行 {start_script} 启动程序
3. 程序会自动在浏览器中打开
4. 如果没有自动打开，请访问 http://localhost:8000

注意事项:
- 程序需要R语言环境支持
- 首次启动可能需要较长时间
- 确保8000端口未被占用
"""
    
    with open(release_dir / "版本信息.txt", 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    # 创建安装说明
    install_guide = f"""安装和使用指南

1. 系统要求:
   - 操作系统: Windows 10+, macOS 10.14+, 或 Linux
   - R语言环境 (必需)
   - 至少2GB可用内存
   - 至少1GB可用磁盘空间

2. 安装步骤:
   - 解压发布包到任意目录
   - 确保R语言已正确安装
   - 双击运行 {start_script}

3. 使用说明:
   - 程序启动后会自动打开浏览器
   - 上传CSV格式的压力数据文件
   - 系统会自动进行分析并生成报告
   - 可以下载分析报告和图表

4. 故障排除:
   - 如果程序无法启动，检查R语言是否正确安装
   - 如果浏览器没有自动打开，手动访问 http://localhost:8000
   - 如果端口被占用，请关闭占用8000端口的其他程序

5. 技术支持:
   - 查看日志文件了解错误信息
   - 确保数据文件格式正确
   - 联系技术支持获取帮助
"""
    
    with open(release_dir / "安装使用指南.txt", 'w', encoding='utf-8') as f:
        f.write(install_guide)
    
    # 显示发布包信息
    print("\n发布包创建完成!")
    print(f"发布包位置: {release_dir}")
    print("\n发布包内容:")
    for item in sorted(release_dir.iterdir()):
        size = item.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"
        print(f"  - {item.name} ({size_str})")
    
    total_size = sum(item.stat().st_size for item in release_dir.iterdir())
    print(f"\n总大小: {total_size / (1024 * 1024):.1f} MB")
    
    return True

def main():
    """主函数"""
    print("压力分析系统发布包生成工具")
    print("=" * 50)
    
    if create_release_package():
        print("\n发布包生成成功!")
        print("可以将release目录打包分发给用户")
    else:
        print("\n发布包生成失败!")

if __name__ == "__main__":
    main() 