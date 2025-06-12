#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试综合报告下载功能
"""
import requests
from pathlib import Path

def test_download_comprehensive():
    """测试综合报告下载功能"""
    task_id = "9ea02dd3-9e29-4309-ab3e-1c2172909982"
    
    print(f"🔧 测试综合报告下载功能，task_id: {task_id}")
    print("=" * 60)
    
    # 1. 检查本地文件是否存在
    local_file = Path(f"temp/reports/comprehensive_analysis_report_{task_id}.docx")
    if local_file.exists():
        file_size = local_file.stat().st_size
        print(f"✅ 本地文件存在: {local_file}")
        print(f"📊 文件大小: {file_size:,} 字节")
    else:
        print(f"❌ 本地文件不存在: {local_file}")
        return False
    
    # 2. 测试下载API
    download_url = f"http://localhost:8000/api/download-comprehensive-report/{task_id}"
    print(f"\n🔗 测试下载URL: {download_url}")
    
    try:
        response = requests.get(download_url, timeout=30)
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 下载成功!")
            print(f"📊 下载文件大小: {len(response.content):,} 字节")
            
            # 保存下载的文件进行验证
            download_file = Path(f"temp/downloaded_comprehensive_report_{task_id}.docx")
            with open(download_file, 'wb') as f:
                f.write(response.content)
            
            print(f"💾 下载文件已保存到: {download_file}")
            
            # 验证文件内容
            if download_file.stat().st_size == local_file.stat().st_size:
                print("✅ 下载文件大小与本地文件一致")
                return True
            else:
                print("⚠️ 下载文件大小与本地文件不一致")
                return False
        else:
            print(f"❌ 下载失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 下载请求异常: {e}")
        return False

if __name__ == "__main__":
    success = test_download_comprehensive()
    
    if success:
        print("\n🎉 综合报告下载测试成功!")
    else:
        print("\n❌ 综合报告下载测试失败") 