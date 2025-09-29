#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
幂等性功能测试脚本
测试接口幂等性、频率限制和重复请求检测
"""

import requests
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://localhost:5000"  # Flask应用
FASTAPI_URL = "http://localhost:8000"  # FastAPI应用
TEST_USER_ID = "test_user_123"
TEST_SESSION_ID = "test_session_456"

def test_flask_idempotency():
    """测试Flask应用的幂等性"""
    print("\n=== 测试Flask应用幂等性 ===")
    
    # 测试数据
    test_data = {
        "user_id": TEST_USER_ID,
        "session_id": TEST_SESSION_ID,
        "event_type": "test_event",
        "page_url": "http://test.com",
        "page_title": "测试页面",
        "custom_data": {"test": "data"}
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID,
        "X-Session-ID": TEST_SESSION_ID
    }
    
    # 第一次请求
    print("发送第一次请求...")
    response1 = requests.post(
        f"{BASE_URL}/api/track/event",
        json=test_data,
        headers=headers
    )
    print(f"第一次请求状态码: {response1.status_code}")
    print(f"第一次请求响应: {response1.json()}")
    
    # 立即发送第二次相同请求（应该被识别为重复）
    print("\n发送第二次相同请求...")
    response2 = requests.post(
        f"{BASE_URL}/api/track/event",
        json=test_data,
        headers=headers
    )
    print(f"第二次请求状态码: {response2.status_code}")
    print(f"第二次请求响应: {response2.json()}")
    
    # 等待一段时间后发送第三次请求
    print("\n等待5秒后发送第三次请求...")
    time.sleep(5)
    response3 = requests.post(
        f"{BASE_URL}/api/track/event",
        json=test_data,
        headers=headers
    )
    print(f"第三次请求状态码: {response3.status_code}")
    print(f"第三次请求响应: {response3.json()}")

def test_fastapi_idempotency():
    """测试FastAPI应用的幂等性"""
    print("\n=== 测试FastAPI应用幂等性 ===")
    
    # 测试数据
    test_data = {
        "destination": "北京",
        "start_date": "2024-01-01",
        "end_date": "2024-01-03",
        "budget": 5000,
        "travel_type": "休闲",
        "preferences": {"categories": ["人文景观", "自然风光"]}
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID,
        "X-Session-ID": TEST_SESSION_ID
    }
    
    # 第一次请求
    print("发送第一次请求...")
    response1 = requests.post(
        f"{FASTAPI_URL}/api/v1/route/plan",
        json=test_data,
        headers=headers
    )
    print(f"第一次请求状态码: {response1.status_code}")
    print(f"第一次请求响应: {response1.json()}")
    
    # 立即发送第二次相同请求（应该被识别为重复）
    print("\n发送第二次相同请求...")
    response2 = requests.post(
        f"{FASTAPI_URL}/api/v1/route/plan",
        json=test_data,
        headers=headers
    )
    print(f"第二次请求状态码: {response2.status_code}")
    print(f"第二次请求响应: {response2.json()}")

def test_rate_limiting():
    """测试频率限制"""
    print("\n=== 测试频率限制 ===")
    
    test_data = {
        "user_id": TEST_USER_ID,
        "session_id": TEST_SESSION_ID,
        "event_type": "rate_limit_test",
        "page_url": "http://test.com",
        "page_title": "频率限制测试"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": TEST_USER_ID,
        "X-Session-ID": TEST_SESSION_ID
    }
    
    # 快速发送多个请求
    print("快速发送10个请求...")
    responses = []
    for i in range(10):
        response = requests.post(
            f"{BASE_URL}/api/track/event",
            json=test_data,
            headers=headers
        )
        responses.append(response)
        print(f"请求 {i+1}: 状态码 {response.status_code}")
        time.sleep(0.1)  # 短暂延迟
    
    # 统计结果
    success_count = sum(1 for r in responses if r.status_code == 200)
    rate_limited_count = sum(1 for r in responses if r.status_code == 429)
    duplicate_count = sum(1 for r in responses if r.status_code == 409)
    
    print(f"\n结果统计:")
    print(f"成功请求: {success_count}")
    print(f"频率限制: {rate_limited_count}")
    print(f"重复请求: {duplicate_count}")

def test_concurrent_requests():
    """测试并发请求"""
    print("\n=== 测试并发请求 ===")
    
    def send_request(request_id):
        test_data = {
            "user_id": f"user_{request_id}",
            "session_id": f"session_{request_id}",
            "event_type": "concurrent_test",
            "page_url": "http://test.com",
            "page_title": f"并发测试 {request_id}"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": f"user_{request_id}",
            "X-Session-ID": f"session_{request_id}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/track/event",
            json=test_data,
            headers=headers
        )
        return {
            "request_id": request_id,
            "status_code": response.status_code,
            "response": response.json()
        }
    
    # 使用线程池发送并发请求
    print("发送20个并发请求...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request, i) for i in range(20)]
        results = [future.result() for future in futures]
    
    # 统计结果
    success_count = sum(1 for r in results if r["status_code"] == 200)
    rate_limited_count = sum(1 for r in results if r["status_code"] == 429)
    duplicate_count = sum(1 for r in results if r["status_code"] == 409)
    
    print(f"\n并发请求结果:")
    print(f"成功请求: {success_count}")
    print(f"频率限制: {rate_limited_count}")
    print(f"重复请求: {duplicate_count}")

def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    
    try:
        # Flask健康检查
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Flask健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Flask健康检查失败: {e}")
    
    try:
        # FastAPI健康检查
        response = requests.get(f"{FASTAPI_URL}/health")
        print(f"FastAPI健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"FastAPI健康检查失败: {e}")

def main():
    """主测试函数"""
    print("开始幂等性功能测试...")
    
    # 检查服务是否运行
    test_health_check()
    
    # 测试Flask应用
    try:
        test_flask_idempotency()
    except Exception as e:
        print(f"Flask测试失败: {e}")
    
    # 测试FastAPI应用
    try:
        test_fastapi_idempotency()
    except Exception as e:
        print(f"FastAPI测试失败: {e}")
    
    # 测试频率限制
    try:
        test_rate_limiting()
    except Exception as e:
        print(f"频率限制测试失败: {e}")
    
    # 测试并发请求
    try:
        test_concurrent_requests()
    except Exception as e:
        print(f"并发请求测试失败: {e}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()