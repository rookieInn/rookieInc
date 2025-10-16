"""
JWT单点登录使用示例
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"

def example_usage():
    """单点登录使用示例"""
    print("=== JWT单点登录使用示例 ===\n")
    
    # 1. 注册用户
    print("1. 注册用户...")
    register_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "demo123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✓ 用户注册成功")
        elif response.status_code == 400 and "已存在" in response.json().get("detail", ""):
            print("✓ 用户已存在，继续使用")
        else:
            print(f"✗ 注册失败: {response.text}")
            return
    except Exception as e:
        print(f"✗ 注册请求失败: {e}")
        return
    
    # 2. 第一次登录
    print("\n2. 第一次登录...")
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            token1 = data["access_token"]
            session_id1 = data["session_id"]
            print(f"✓ 登录成功")
            print(f"  Token: {token1[:50]}...")
            print(f"  Session ID: {session_id1}")
        else:
            print(f"✗ 登录失败: {response.text}")
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
            user_info = response.json()
            print("✓ 访问成功")
            print(f"  用户信息: {user_info['username']} ({user_info['email']})")
        else:
            print(f"✗ 访问失败: {response.text}")
    except Exception as e:
        print(f"✗ 访问请求失败: {e}")
    
    # 4. 第二次登录（挤掉第一次）
    print("\n4. 第二次登录（挤掉第一次）...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            token2 = data["access_token"]
            session_id2 = data["session_id"]
            print(f"✓ 重新登录成功")
            print(f"  新Token: {token2[:50]}...")
            print(f"  新Session ID: {session_id2}")
        else:
            print(f"✗ 重新登录失败: {response.text}")
            return
    except Exception as e:
        print(f"✗ 重新登录请求失败: {e}")
        return
    
    # 5. 验证第一个token失效
    print("\n5. 验证第一个token失效...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers1)
        if response.status_code == 401:
            print("✓ 第一个token已失效（符合预期）")
            print(f"  错误信息: {response.json().get('detail', '')}")
        else:
            print(f"✗ 第一个token仍然有效（不符合预期）: {response.text}")
    except Exception as e:
        print(f"✗ 验证请求失败: {e}")
    
    # 6. 验证第二个token有效
    print("\n6. 验证第二个token有效...")
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
        if response.status_code == 200:
            user_info = response.json()
            print("✓ 第二个token有效")
            print(f"  用户信息: {user_info['username']} ({user_info['email']})")
        else:
            print(f"✗ 第二个token无效: {response.text}")
    except Exception as e:
        print(f"✗ 验证请求失败: {e}")
    
    # 7. 测试登出
    print("\n7. 测试登出...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers2)
        if response.status_code == 200:
            print("✓ 登出成功")
            print(f"  消息: {response.json().get('message', '')}")
        else:
            print(f"✗ 登出失败: {response.text}")
    except Exception as e:
        print(f"✗ 登出请求失败: {e}")
    
    # 8. 验证登出后token失效
    print("\n8. 验证登出后token失效...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
        if response.status_code == 401:
            print("✓ 登出后token已失效（符合预期）")
            print(f"  错误信息: {response.json().get('detail', '')}")
        else:
            print(f"✗ 登出后token仍然有效（不符合预期）: {response.text}")
    except Exception as e:
        print(f"✗ 验证请求失败: {e}")
    
    print("\n=== 示例完成 ===")

def example_admin_force_logout():
    """管理员强制登出示例"""
    print("\n=== 管理员强制登出示例 ===\n")
    
    # 注意：这个示例需要管理员账户
    print("注意：此示例需要管理员账户")
    print("1. 首先需要创建一个管理员账户")
    print("2. 或者将现有用户设置为管理员")
    print("3. 然后可以使用管理员token强制登出其他用户")
    
    # 示例代码（需要实际的管理员账户）
    admin_headers = {"Authorization": "Bearer <admin_token>"}
    target_user_id = 1
    
    print(f"\n强制登出用户ID {target_user_id} 的示例代码：")
    print(f"requests.post('{BASE_URL}/auth/force-logout/{target_user_id}', headers={admin_headers})")

def example_curl_commands():
    """cURL命令示例"""
    print("\n=== cURL命令示例 ===\n")
    
    print("1. 用户注册：")
    print(f"""curl -X POST "{BASE_URL}/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "testuser", "email": "test@example.com", "password": "testpass123"}}'""")
    
    print("\n2. 用户登录：")
    print(f"""curl -X POST "{BASE_URL}/auth/login" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=testuser&password=testpass123" """)
    
    print("\n3. 访问受保护资源：")
    print(f"""curl -X GET "{BASE_URL}/auth/me" \\
  -H "Authorization: Bearer <your_token>" """)
    
    print("\n4. 用户登出：")
    print(f"""curl -X POST "{BASE_URL}/auth/logout" \\
  -H "Authorization: Bearer <your_token>" """)
    
    print("\n5. 管理员强制登出：")
    print(f"""curl -X POST "{BASE_URL}/auth/force-logout/1" \\
  -H "Authorization: Bearer <admin_token>" """)

if __name__ == "__main__":
    print(f"JWT单点登录使用示例 - {datetime.now()}")
    print(f"服务器地址: {BASE_URL}")
    print("=" * 60)
    
    # 基础使用示例
    example_usage()
    
    # 管理员功能示例
    example_admin_force_logout()
    
    # cURL命令示例
    example_curl_commands()
    
    print(f"\n示例完成 - {datetime.now()}")