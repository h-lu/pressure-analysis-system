#!/usr/bin/env python3
"""
测试DeepSeek检查和获取API的脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_deepseek_check_api():
    """测试DeepSeek检查API"""
    print("=" * 50)
    print("测试DeepSeek检查和获取API")
    print("=" * 50)
    
    # 使用一个已知的任务ID（应该已经存在deepseek分析）
    test_task_id = "211e241c-197d-45a2-9904-bcf1fe052917"
    
    # 1. 测试检查API
    print(f"\n1. 测试检查API: /api/deepseek/check/{test_task_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/deepseek/check/{test_task_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("检查结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("exists"):
                # 2. 如果存在，测试获取API
                print(f"\n2. 测试获取API: /api/deepseek/get/{test_task_id}")
                get_response = requests.get(f"{BASE_URL}/api/deepseek/get/{test_task_id}")
                print(f"状态码: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    get_result = get_response.json()
                    print("获取结果（前500字符）:")
                    report_content = get_result.get("data", {}).get("report", "")
                    print(f"报告内容: {report_content[:500]}...")
                    print(f"报告总长度: {len(report_content)} 字符")
                else:
                    print(f"获取失败: {get_response.text}")
            else:
                print("DeepSeek分析不存在，这是正常的")
        else:
            print(f"检查失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
    
    # 3. 测试不存在的任务ID
    print(f"\n3. 测试不存在的任务ID")
    fake_task_id = "nonexistent-task-id"
    try:
        response = requests.get(f"{BASE_URL}/api/deepseek/check/{fake_task_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("检查结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"检查失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

def test_download_report_with_auto_deepseek():
    """测试带自动DeepSeek生成的下载报告功能"""
    print("\n" + "=" * 50)
    print("测试自动DeepSeek生成的下载报告功能")
    print("=" * 50)
    
    # 使用一个已知的任务ID
    test_task_id = "211e241c-197d-45a2-9904-bcf1fe052917"
    
    print(f"\n测试下载报告: /api/download-report/{test_task_id}")
    try:
        # 测试下载报告（应该会自动检查并可能生成DeepSeek分析）
        response = requests.get(f"{BASE_URL}/api/download-report/{test_task_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {response.headers.get('content-length')}")
            print(f"Content-Disposition: {response.headers.get('content-disposition')}")
            
            # 检查是否是Word文档
            if "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers.get('content-type', ''):
                print("✓ 成功生成Word文档")
                print(f"文档大小: {len(response.content)} 字节")
                
                # 可选：保存文件以便检查
                filename = f"test_report_{test_task_id}.docx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"报告已保存为: {filename}")
            else:
                print("✗ 返回的不是Word文档")
        else:
            print(f"下载失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)
    
    # 检查服务器是否可用
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ 服务器正常运行")
        else:
            print("✗ 服务器似乎有问题")
            exit(1)
    except:
        print("✗ 无法连接到服务器")
        exit(1)
    
    # 运行测试
    test_deepseek_check_api()
    test_download_report_with_auto_deepseek()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50) 