#!/usr/bin/env python3
"""
评论系统功能测试脚本
"""
import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE_URL = "http://localhost:8000/api/v1"

def test_comment_system():
    """测试评论系统功能"""
    print("开始测试评论系统功能...")
    
    # 测试用户登录
    print("\n1. 测试用户登录...")
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print("✓ 用户登录成功")
    else:
        print(f"✗ 用户登录失败: {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取用户的旅游计划
    print("\n2. 获取用户旅游计划...")
    response = requests.get(f"{API_BASE_URL}/plans", headers=headers)
    if response.status_code == 200:
        plans = response.json()
        if plans:
            plan_id = plans[0]["id"]
            print(f"✓ 找到旅游计划: {plans[0]['title']} (ID: {plan_id})")
        else:
            print("✗ 没有找到旅游计划")
            return
    else:
        print(f"✗ 获取旅游计划失败: {response.text}")
        return
    
    # 测试创建评论
    print("\n3. 测试创建评论...")
    comment_data = {
        "content": "这个旅游计划很不错！我很期待这次旅行。",
        "plan_id": plan_id
    }
    
    response = requests.post(f"{API_BASE_URL}/comments", 
                           json=comment_data, headers=headers)
    if response.status_code == 200:
        comment = response.json()
        comment_id = comment["id"]
        print(f"✓ 评论创建成功 (ID: {comment_id})")
    else:
        print(f"✗ 评论创建失败: {response.text}")
        return
    
    print("\n评论系统功能测试完成！")

if __name__ == "__main__":
    try:
        test_comment_system()
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
