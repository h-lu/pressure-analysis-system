#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载API
"""
import requests

def test_download_api():
    """测试下载API"""
    task_id = "test_1749429573"
    url = f"http://localhost:8000/api/download-comprehensive-report/{task_id}"
    
    print(f"测试URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 下载成功")
            print(f"文件大小: {len(response.content)} 字节")
        else:
            print("❌ 下载失败")
            print(f"错误内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_download_api() 