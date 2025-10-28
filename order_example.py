"""
订单系统使用示例
"""
from order_models import OrderManager, OrderStatus
from order_notifications import OrderNotificationService, NotificationConfig
import time
import json

def simple_example():
    """简单使用示例"""
    print("=== 订单系统简单示例 ===")
    
    # 1. 创建订单管理器
    order_manager = OrderManager("example_orders.db")
    
    # 2. 创建订单
    print("创建订单...")
    order = order_manager.create_order(
        user_id="user_123",
        amount=199.99,
        items=[
            {"name": "iPhone 15", "price": 199.99, "quantity": 1}
        ],
        customer_info={
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000"
        },
        expiry_minutes=30  # 30分钟后自动关闭
    )
    
    print(f"订单创建成功: {order.order_id}")
    print(f"订单金额: ¥{order.amount}")
    print(f"过期时间: {order.expires_at}")
    
    # 3. 查询订单
    print("\n查询订单...")
    found_order = order_manager.get_order(order.order_id)
    if found_order:
        print(f"找到订单: {found_order.order_id}")
        print(f"订单状态: {found_order.status.value}")
    
    # 4. 更新订单状态
    print("\n更新订单状态...")
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.CONFIRMED, 
        "订单已确认"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"订单状态更新为: {updated_order.status.value}")
    
    # 5. 获取用户订单
    print("\n获取用户所有订单...")
    user_orders = order_manager.get_orders_by_user("user_123")
    print(f"用户共有 {len(user_orders)} 个订单")
    
    for order in user_orders:
        print(f"  - {order.order_id}: ¥{order.amount} ({order.status.value})")
    
    # 6. 获取订单统计
    print("\n订单统计...")
    stats = order_manager.get_order_statistics()
    print(f"总订单数: {stats['total_orders']}")
    print(f"总收入: ¥{stats['total_revenue']}")
    print("各状态订单数:")
    for status, count in stats['status_counts'].items():
        print(f"  {status}: {count}")

def notification_example():
    """通知系统示例"""
    print("\n=== 通知系统示例 ===")
    
    # 配置通知（需要真实的邮件配置）
    config = NotificationConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-app-password",
        from_email="your-email@gmail.com",
        webhook_url="https://your-webhook-url.com/notifications"
    )
    
    # 创建带通知的订单服务
    order_manager = OrderManager("notification_orders.db")
    notification_service = OrderNotificationService(order_manager, config)
    
    # 创建订单并自动发送通知
    print("创建订单并发送通知...")
    order = notification_service.create_order_with_notification(
        user_id="notification_user",
        amount=299.99,
        items=[{"name": "测试商品", "price": 299.99, "quantity": 1}],
        customer_info={
            "name": "测试用户",
            "email": "test@example.com"
        }
    )
    
    print(f"订单创建成功: {order.order_id}")
    
    # 更新订单状态并发送通知
    print("更新订单状态并发送通知...")
    success = notification_service.update_order_status_with_notification(
        order.order_id,
        OrderStatus.CONFIRMED,
        "订单已确认",
        "test@example.com"
    )
    
    if success:
        print("订单状态更新并通知发送成功")

def auto_expiry_demo():
    """自动过期演示"""
    print("\n=== 自动过期演示 ===")
    
    order_manager = OrderManager("expiry_demo.db")
    
    # 创建一个1分钟后过期的订单
    print("创建1分钟后过期的测试订单...")
    order = order_manager.create_order(
        user_id="expiry_test_user",
        amount=99.99,
        items=[{"name": "测试商品", "price": 99.99, "quantity": 1}],
        customer_info={"name": "过期测试用户", "email": "expiry@example.com"},
        expiry_minutes=1  # 1分钟过期
    )
    
    print(f"订单创建: {order.order_id}")
    print(f"过期时间: {order.expires_at}")
    print("等待订单自动过期...")
    
    # 等待2分钟
    time.sleep(120)
    
    # 检查过期订单
    expired_orders = order_manager.get_expired_orders()
    print(f"过期订单数量: {len(expired_orders)}")
    
    for expired_order in expired_orders:
        print(f"过期订单: {expired_order.order_id} - {expired_order.status.value}")

def api_usage_example():
    """API使用示例"""
    print("\n=== API使用示例 ===")
    
    base_url = "http://localhost:5000/api"
    
    # 创建订单
    order_data = {
        "user_id": "api_user",
        "amount": 399.99,
        "items": [
            {"name": "API测试商品", "price": 399.99, "quantity": 1}
        ],
        "customer_info": {
            "name": "API用户",
            "email": "api@example.com"
        },
        "expiry_minutes": 30
    }
    
    try:
        import requests
        
        print("发送创建订单请求...")
        response = requests.post(f"{base_url}/orders", json=order_data)
        
        if response.status_code == 201:
            result = response.json()
            order_id = result['order']['order_id']
            print(f"订单创建成功: {order_id}")
            
            # 获取订单详情
            print("获取订单详情...")
            response = requests.get(f"{base_url}/orders/{order_id}")
            if response.status_code == 200:
                order_info = response.json()
                print(f"订单状态: {order_info['order']['status']}")
            
            # 确认订单
            print("确认订单...")
            update_data = {"status": "confirmed", "message": "API确认"}
            response = requests.put(f"{base_url}/orders/{order_id}/status", json=update_data)
            if response.status_code == 200:
                print("订单确认成功")
            
            # 获取订单统计
            print("获取订单统计...")
            response = requests.get(f"{base_url}/orders/statistics")
            if response.status_code == 200:
                stats = response.json()
                print(f"总订单数: {stats['statistics']['total_orders']}")
                
        else:
            print(f"API请求失败: {response.status_code}")
            
    except ImportError:
        print("需要安装 requests 库: pip install requests")
    except Exception as e:
        print(f"API示例出错: {e}")

if __name__ == "__main__":
    print("订单系统使用示例")
    print("=" * 50)
    
    # 运行各种示例
    simple_example()
    notification_example()
    auto_expiry_demo()
    api_usage_example()
    
    print("\n示例运行完成！")
    print("\n要启动API服务，请运行: python order_api.py")
    print("要运行完整测试，请运行: python test_order_system.py")