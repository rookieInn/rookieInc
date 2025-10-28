#!/usr/bin/env python3
"""
订单系统启动脚本
"""
import os
import sys
import time
import threading
import subprocess
from order_models import OrderManager
from order_notifications import NotificationConfig

def start_api_server():
    """启动API服务器"""
    print("启动订单API服务器...")
    try:
        import order_api
        order_api.app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"启动API服务器失败: {e}")

def start_order_manager():
    """启动订单管理器"""
    print("启动订单管理器...")
    order_manager = OrderManager()
    print("订单管理器已启动，自动过期检查器正在运行...")
    
    # 保持运行
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n订单管理器已停止")

def create_sample_config():
    """创建示例配置文件"""
    config = {
        "database": {
            "path": "orders.db"
        },
        "notifications": {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "your-email@gmail.com",
                "smtp_password": "your-app-password",
                "from_email": "your-email@gmail.com"
            },
            "webhook": {
                "url": "https://your-webhook-url.com/order-notifications"
            }
        },
        "api": {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False
        },
        "order": {
            "default_expiry_minutes": 30,
            "expiry_check_interval": 30
        }
    }
    
    with open("order_config.json", "w", encoding="utf-8") as f:
        import json
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("示例配置文件已创建: order_config.json")

def show_usage():
    """显示使用说明"""
    print("""
订单系统使用说明
================

1. 启动API服务器:
   python start_order_system.py api

2. 启动订单管理器:
   python start_order_system.py manager

3. 同时启动API服务器和订单管理器:
   python start_order_system.py all

4. 创建示例配置:
   python start_order_system.py config

5. 运行测试:
   python test_order_system.py

6. 运行示例:
   python order_example.py

API接口说明
===========

POST /api/orders - 创建订单
GET /api/orders/<order_id> - 获取订单详情
PUT /api/orders/<order_id>/status - 更新订单状态
GET /api/orders/user/<user_id> - 获取用户订单
GET /api/orders/statistics - 获取订单统计
POST /api/orders/<order_id>/cancel - 取消订单
POST /api/orders/<order_id>/confirm - 确认订单
GET /api/health - 健康检查

订单状态
========

pending - 待处理
confirmed - 已确认
processing - 处理中
completed - 已完成
cancelled - 已取消
expired - 已过期（30分钟自动关闭）

特性
====

- 订单创建和管理
- 30分钟自动过期关闭
- 状态变更日志
- 邮件和Webhook通知
- RESTful API接口
- 订单统计和分析
- 多用户支持
- 数据库持久化

""")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "api":
        start_api_server()
    elif command == "manager":
        start_order_manager()
    elif command == "all":
        print("同时启动API服务器和订单管理器...")
        
        # 在后台线程启动订单管理器
        manager_thread = threading.Thread(target=start_order_manager, daemon=True)
        manager_thread.start()
        
        # 启动API服务器（主线程）
        start_api_server()
    elif command == "config":
        create_sample_config()
    elif command == "help":
        show_usage()
    else:
        print(f"未知命令: {command}")
        show_usage()

if __name__ == "__main__":
    main()