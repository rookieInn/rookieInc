"""
订单系统测试用例和示例代码
"""
import time
import json
import requests
import threading
from datetime import datetime, timedelta
from order_models import OrderManager, OrderStatus, Order
from order_notifications import OrderNotificationService, NotificationConfig

def test_order_creation():
    """测试订单创建"""
    print("=== 测试订单创建 ===")
    
    order_manager = OrderManager("test_orders.db")
    
    # 创建测试订单
    order = order_manager.create_order(
        user_id="user_001",
        amount=99.99,
        items=[
            {"name": "商品A", "price": 49.99, "quantity": 1},
            {"name": "商品B", "price": 50.00, "quantity": 1}
        ],
        customer_info={
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000"
        },
        expiry_minutes=1  # 1分钟过期，便于测试
    )
    
    print(f"订单创建成功: {order.order_id}")
    print(f"订单金额: ¥{order.amount}")
    print(f"订单状态: {order.status.value}")
    print(f"过期时间: {order.expires_at}")
    
    return order

def test_order_status_update():
    """测试订单状态更新"""
    print("\n=== 测试订单状态更新 ===")
    
    order_manager = OrderManager("test_orders.db")
    
    # 获取第一个订单
    orders = order_manager.get_orders_by_user("user_001")
    if not orders:
        print("没有找到订单")
        return
    
    order = orders[0]
    print(f"当前订单状态: {order.status.value}")
    
    # 更新为已确认
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.CONFIRMED, 
        "订单已确认"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"订单状态更新成功: {updated_order.status.value}")
    else:
        print("订单状态更新失败")

def test_order_expiry():
    """测试订单过期"""
    print("\n=== 测试订单过期 ===")
    
    order_manager = OrderManager("test_orders.db")
    
    # 创建一个1分钟后过期的订单
    order = order_manager.create_order(
        user_id="user_002",
        amount=199.99,
        items=[{"name": "测试商品", "price": 199.99, "quantity": 1}],
        customer_info={"name": "李四", "email": "lisi@example.com"},
        expiry_minutes=1  # 1分钟过期
    )
    
    print(f"创建测试订单: {order.order_id}")
    print(f"过期时间: {order.expires_at}")
    print("等待订单过期...")
    
    # 等待2分钟让订单过期
    time.sleep(120)
    
    # 检查订单状态
    expired_orders = order_manager.get_expired_orders()
    print(f"过期订单数量: {len(expired_orders)}")
    
    for expired_order in expired_orders:
        print(f"过期订单: {expired_order.order_id} - {expired_order.status.value}")

def test_order_statistics():
    """测试订单统计"""
    print("\n=== 测试订单统计 ===")
    
    order_manager = OrderManager("test_orders.db")
    stats = order_manager.get_order_statistics()
    
    print("订单统计信息:")
    print(f"总订单数: {stats['total_orders']}")
    print(f"今日订单数: {stats['today_orders']}")
    print(f"总收入: ¥{stats['total_revenue']}")
    print("各状态订单数:")
    for status, count in stats['status_counts'].items():
        print(f"  {status}: {count}")

def test_api_endpoints():
    """测试API接口"""
    print("\n=== 测试API接口 ===")
    
    base_url = "http://localhost:5000/api"
    
    # 测试创建订单
    order_data = {
        "user_id": "api_user_001",
        "amount": 299.99,
        "items": [
            {"name": "API测试商品", "price": 299.99, "quantity": 1}
        ],
        "customer_info": {
            "name": "API测试用户",
            "email": "api@example.com"
        },
        "expiry_minutes": 2
    }
    
    try:
        # 创建订单
        response = requests.post(f"{base_url}/orders", json=order_data)
        if response.status_code == 201:
            result = response.json()
            order_id = result['order']['order_id']
            print(f"API创建订单成功: {order_id}")
            
            # 获取订单详情
            response = requests.get(f"{base_url}/orders/{order_id}")
            if response.status_code == 200:
                print("API获取订单详情成功")
            
            # 更新订单状态
            update_data = {"status": "confirmed", "message": "API测试确认"}
            response = requests.put(f"{base_url}/orders/{order_id}/status", json=update_data)
            if response.status_code == 200:
                print("API更新订单状态成功")
            
            # 获取用户订单
            response = requests.get(f"{base_url}/orders/user/api_user_001")
            if response.status_code == 200:
                result = response.json()
                print(f"API获取用户订单成功，共{result['count']}个订单")
            
            # 获取订单统计
            response = requests.get(f"{base_url}/orders/statistics")
            if response.status_code == 200:
                print("API获取订单统计成功")
                
        else:
            print(f"API创建订单失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("API服务未启动，跳过API测试")
    except Exception as e:
        print(f"API测试出错: {e}")

def test_notification_system():
    """测试通知系统"""
    print("\n=== 测试通知系统 ===")
    
    # 创建通知配置（使用测试配置）
    config = NotificationConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="test@example.com",
        smtp_password="test_password",
        from_email="test@example.com",
        webhook_url="https://webhook.site/test"
    )
    
    order_manager = OrderManager("test_orders.db")
    notification_service = OrderNotificationService(order_manager, config)
    
    # 创建订单并发送通知
    order = notification_service.create_order_with_notification(
        user_id="notification_user_001",
        amount=399.99,
        items=[{"name": "通知测试商品", "price": 399.99, "quantity": 1}],
        customer_info={
            "name": "通知测试用户",
            "email": "notification@example.com"
        }
    )
    
    print(f"创建订单并发送通知: {order.order_id}")
    
    # 更新订单状态并发送通知
    success = notification_service.update_order_status_with_notification(
        order.order_id,
        OrderStatus.CONFIRMED,
        "通知测试确认",
        "notification@example.com"
    )
    
    if success:
        print("订单状态更新并发送通知成功")
    else:
        print("订单状态更新失败")

def demo_complete_workflow():
    """演示完整的工作流程"""
    print("\n=== 完整工作流程演示 ===")
    
    order_manager = OrderManager("demo_orders.db")
    
    # 1. 创建订单
    print("1. 创建订单...")
    order = order_manager.create_order(
        user_id="demo_user",
        amount=599.99,
        items=[
            {"name": "笔记本电脑", "price": 4999.99, "quantity": 1},
            {"name": "鼠标", "price": 99.99, "quantity": 1}
        ],
        customer_info={
            "name": "演示用户",
            "email": "demo@example.com",
            "phone": "13900139000",
            "address": "北京市朝阳区"
        },
        expiry_minutes=1  # 1分钟过期，便于演示
    )
    
    print(f"   订单创建成功: {order.order_id}")
    print(f"   订单金额: ¥{order.amount}")
    print(f"   过期时间: {order.expires_at}")
    
    # 2. 确认订单
    print("\n2. 确认订单...")
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.CONFIRMED, 
        "订单已确认，开始处理"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"   订单状态: {updated_order.status.value}")
    
    # 3. 处理订单
    print("\n3. 处理订单...")
    time.sleep(2)  # 模拟处理时间
    
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.PROCESSING, 
        "订单处理中"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"   订单状态: {updated_order.status.value}")
    
    # 4. 完成订单
    print("\n4. 完成订单...")
    time.sleep(2)  # 模拟处理时间
    
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.COMPLETED, 
        "订单处理完成"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"   订单状态: {updated_order.status.value}")
        print(f"   完成时间: {updated_order.updated_at}")
    
    # 5. 显示最终统计
    print("\n5. 订单统计...")
    stats = order_manager.get_order_statistics()
    print(f"   总订单数: {stats['total_orders']}")
    print(f"   总收入: ¥{stats['total_revenue']}")

def run_all_tests():
    """运行所有测试"""
    print("开始运行订单系统测试...")
    
    try:
        # 基础功能测试
        test_order_creation()
        test_order_status_update()
        test_order_statistics()
        
        # API测试
        test_api_endpoints()
        
        # 通知系统测试
        test_notification_system()
        
        # 完整工作流程演示
        demo_complete_workflow()
        
        print("\n所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    run_all_tests()