"""
测试单点登录功能
"""
import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpass123"

def test_single_session_login():
    """测试单点登录功能"""
    print("=== 单点登录功能测试 ===\n")
    
    # 1. 注册测试用户
    print("1. 注册测试用户...")
    register_data = {
        "username": USERNAME,
        "email": "test@example.com",
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✓ 用户注册成功")
        elif response.status_code == 400 and "已存在" in response.json().get("detail", ""):
            print("✓ 用户已存在，继续测试")
        else:
            print(f"✗ 用户注册失败: {response.text}")
            return
    except Exception as e:
        print(f"✗ 注册请求失败: {e}")
        return
    
    # 2. 第一次登录
    print("\n2. 第一次登录...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token1 = response.json()["access_token"]
            print(f"✓ 第一次登录成功，获得token: {token1[:20]}...")
        else:
            print(f"✗ 第一次登录失败: {response.text}")
            return
    except Exception as e:
        print(f"✗ 登录请求失败: {e}")
        return
    
    # 3. 使用第一个token访问受保护资源
    print("\n3. 使用第一个token访问受保护资源...")
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers1)
        if response.status_code == 200:
            print("✓ 第一个token可以正常访问受保护资源")
        else:
            print(f"✗ 第一个token访问失败: {response.text}")
    except Exception as e:
        print(f"✗ 访问请求失败: {e}")
    
    # 4. 第二次登录（应该使第一个token失效）
    print("\n4. 第二次登录（应该使第一个token失效）...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token2 = response.json()["access_token"]
            print(f"✓ 第二次登录成功，获得新token: {token2[:20]}...")
        else:
            print(f"✗ 第二次登录失败: {response.text}")
            return
    except Exception as e:
        print(f"✗ 第二次登录请求失败: {e}")
        return
    
    # 5. 验证第一个token是否失效
    print("\n5. 验证第一个token是否失效...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers1)
        if response.status_code == 401:
            print("✓ 第一个token已失效（符合预期）")
        else:
            print(f"✗ 第一个token仍然有效（不符合预期）: {response.text}")
    except Exception as e:
        print(f"✗ 验证请求失败: {e}")
    
    # 6. 验证第二个token是否有效
    print("\n6. 验证第二个token是否有效...")
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
        if response.status_code == 200:
            print("✓ 第二个token可以正常访问受保护资源")
        else:
            print(f"✗ 第二个token访问失败: {response.text}")
    except Exception as e:
        print(f"✗ 访问请求失败: {e}")
    
    # 7. 测试登出功能
    print("\n7. 测试登出功能...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers2)
        if response.status_code == 200:
            print("✓ 登出成功")
        else:
            print(f"✗ 登出失败: {response.text}")
    except Exception as e:
        print(f"✗ 登出请求失败: {e}")
    
    # 8. 验证登出后token是否失效
    print("\n8. 验证登出后token是否失效...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
        if response.status_code == 401:
            print("✓ 登出后token已失效（符合预期）")
        else:
            print(f"✗ 登出后token仍然有效（不符合预期）: {response.text}")
    except Exception as e:
        print(f"✗ 验证请求失败: {e}")
    
    print("\n=== 测试完成 ===")

def test_concurrent_login():
    """测试并发登录"""
    print("\n=== 并发登录测试 ===\n")
    
    import threading
    import queue
    
    results = queue.Queue()
    
    def login_worker(worker_id):
        """登录工作线程"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", data={
                "username": USERNAME,
                "password": PASSWORD
            })
            results.put((worker_id, response.status_code, response.json() if response.status_code == 200 else response.text))
        except Exception as e:
            results.put((worker_id, "error", str(e)))
    
    # 创建多个并发登录线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=login_worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 收集结果
    print("并发登录结果:")
    while not results.empty():
        worker_id, status, data = results.get()
        if status == 200:
            token = data["access_token"][:20] + "..."
            print(f"  工作线程 {worker_id}: 登录成功，token: {token}")
        else:
            print(f"  工作线程 {worker_id}: 登录失败 - {data}")

if __name__ == "__main__":
    print(f"开始测试单点登录功能 - {datetime.now()}")
    print(f"测试服务器: {BASE_URL}")
    print(f"测试用户: {USERNAME}")
    print("=" * 50)
    
    # 基础单点登录测试
    test_single_session_login()
    
    # 并发登录测试
    test_concurrent_login()
    
    print(f"\n测试完成 - {datetime.now()}")