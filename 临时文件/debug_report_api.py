#!/usr/bin/env python3
"""
调试报告生成API的脚本
"""

import requests
import json

def debug_report_api():
    """调试报告API"""
    
    task_id = "4514bcbf-1459-409c-8e17-710e6b73ab31"
    
    print(f"🔍 调试报告生成API")
    print(f"📊 任务ID: {task_id}")
    
    try:
        response = requests.post(
            f"http://localhost:8000/api/deepseek/generate-comprehensive-word-report?task_id={task_id}",
            timeout=600
        )
        
        print(f"\n📋 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ JSON响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(f"\n📄 文本响应:")
                print(response.text)
        else:
            print(f"\n❌ 错误响应:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    debug_report_api() 