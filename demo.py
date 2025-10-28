#!/usr/bin/env python3
"""
直播间管理系统演示脚本
展示系统的主要功能
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:5001"

def test_api():
    """测试API接口"""
    print("=" * 50)
    print("直播间管理系统功能演示")
    print("=" * 50)
    
    # 1. 获取房间列表
    print("\n1. 获取房间列表:")
    response = requests.get(f"{BASE_URL}/api/rooms")
    rooms = response.json()
    print(json.dumps(rooms, indent=2, ensure_ascii=False))
    
    # 2. 创建预约
    print("\n2. 创建预约:")
    now = datetime.now()
    start_time = now + timedelta(minutes=1)  # 1分钟后开始
    end_time = now + timedelta(hours=2)      # 2小时后结束
    
    booking_data = {
        "room_id": 1,
        "user_name": "张三",
        "user_phone": "13800138000",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/api/bookings", json=booking_data)
    booking = response.json()
    print(f"预约创建成功: {booking['id']}")
    
    # 3. 获取预约列表
    print("\n3. 获取预约列表:")
    response = requests.get(f"{BASE_URL}/api/bookings")
    bookings = response.json()
    print(f"当前预约数量: {len(bookings)}")
    
    # 4. 等待预约时间到达并测试门禁
    print("\n4. 等待预约时间到达...")
    print("等待60秒让预约时间到达...")
    time.sleep(60)
    
    # 5. 测试门禁访问
    print("\n5. 测试门禁访问:")
    access_data = {"user_phone": "13800138000"}
    response = requests.post(f"{BASE_URL}/api/access/1", json=access_data)
    result = response.json()
    print(f"访问验证结果: {result}")
    
    # 6. 获取房间状态
    print("\n6. 获取房间状态:")
    response = requests.get(f"{BASE_URL}/api/rooms")
    rooms = response.json()
    print(json.dumps(rooms, indent=2, ensure_ascii=False))
    
    # 7. 获取访问日志
    print("\n7. 获取访问日志:")
    response = requests.get(f"{BASE_URL}/api/logs")
    logs = response.json()
    print(f"访问日志数量: {len(logs)}")
    for log in logs[:3]:  # 显示最近3条日志
        print(f"- {log['timestamp']}: {log['action']} - {log['reason']}")
    
    print("\n演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器")
        print("请确保系统正在运行: python3 run.py --init-db --no-hardware --port 5001")
    except Exception as e:
        print(f"演示过程中出现错误: {e}")