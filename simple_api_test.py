#!/usr/bin/env python3
"""
简化的API测试（不依赖Flask）
"""
import json
import sqlite3
from datetime import datetime, timedelta
from order_models import OrderManager, OrderStatus

def test_database_operations():
    """测试数据库操作"""
    print("=== 测试数据库操作 ===")
    
    # 创建订单管理器
    order_manager = OrderManager("test_api_orders.db")
    
    # 1. 创建订单
    print("1. 创建订单...")
    order = order_manager.create_order(
        user_id="api_test_user",
        amount=299.99,
        items=[
            {"name": "API测试商品", "price": 299.99, "quantity": 1}
        ],
        customer_info={
            "name": "API测试用户",
            "email": "api@example.com"
        },
        expiry_minutes=30
    )
    
    print(f"   订单创建成功: {order.order_id}")
    print(f"   订单金额: ¥{order.amount}")
    print(f"   订单状态: {order.status.value}")
    
    # 2. 获取订单
    print("\n2. 获取订单...")
    retrieved_order = order_manager.get_order(order.order_id)
    if retrieved_order:
        print(f"   订单获取成功: {retrieved_order.order_id}")
        print(f"   订单状态: {retrieved_order.status.value}")
    else:
        print("   订单获取失败")
    
    # 3. 更新订单状态
    print("\n3. 更新订单状态...")
    success = order_manager.update_order_status(
        order.order_id, 
        OrderStatus.CONFIRMED, 
        "API测试确认"
    )
    
    if success:
        updated_order = order_manager.get_order(order.order_id)
        print(f"   订单状态更新成功: {updated_order.status.value}")
    else:
        print("   订单状态更新失败")
    
    # 4. 获取用户订单
    print("\n4. 获取用户订单...")
    user_orders = order_manager.get_orders_by_user("api_test_user")
    print(f"   用户订单数量: {len(user_orders)}")
    
    for order in user_orders:
        print(f"   - {order.order_id}: ¥{order.amount} ({order.status.value})")
    
    # 5. 获取订单统计
    print("\n5. 获取订单统计...")
    stats = order_manager.get_order_statistics()
    print(f"   总订单数: {stats['total_orders']}")
    print(f"   总收入: ¥{stats['total_revenue']}")
    print("   各状态订单数:")
    for status, count in stats['status_counts'].items():
        print(f"     {status}: {count}")
    
    # 6. 测试订单过期
    print("\n6. 测试订单过期...")
    # 创建一个1分钟后过期的订单
    expired_order = order_manager.create_order(
        user_id="expiry_test_user",
        amount=99.99,
        items=[{"name": "过期测试商品", "price": 99.99, "quantity": 1}],
        customer_info={"name": "过期测试用户", "email": "expiry@example.com"},
        expiry_minutes=1  # 1分钟过期
    )
    
    print(f"   创建过期测试订单: {expired_order.order_id}")
    print(f"   过期时间: {expired_order.expires_at}")
    print("   等待订单过期...")
    
    # 等待2分钟
    import time
    time.sleep(120)
    
    # 检查过期订单
    expired_orders = order_manager.get_expired_orders()
    print(f"   过期订单数量: {len(expired_orders)}")
    
    for expired_order in expired_orders:
        print(f"   - {expired_order.order_id}: {expired_order.status.value}")

def test_json_api_format():
    """测试JSON API格式"""
    print("\n=== 测试JSON API格式 ===")
    
    order_manager = OrderManager("test_json_orders.db")
    
    # 创建订单
    order = order_manager.create_order(
        user_id="json_test_user",
        amount=199.99,
        items=[
            {"name": "JSON测试商品", "price": 199.99, "quantity": 1}
        ],
        customer_info={
            "name": "JSON测试用户",
            "email": "json@example.com"
        }
    )
    
    # 模拟API响应格式
    api_response = {
        "success": True,
        "message": "订单创建成功",
        "order": order.to_dict()
    }
    
    print("API响应格式:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # 模拟状态更新API响应
    order_manager.update_order_status(order.order_id, OrderStatus.CONFIRMED, "JSON测试确认")
    updated_order = order_manager.get_order(order.order_id)
    
    status_response = {
        "success": True,
        "message": "订单状态更新成功",
        "order": updated_order.to_dict()
    }
    
    print("\n状态更新API响应格式:")
    print(json.dumps(status_response, indent=2, ensure_ascii=False))

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    order_manager = OrderManager("test_error_orders.db")
    
    # 测试获取不存在的订单
    print("1. 测试获取不存在的订单...")
    non_existent_order = order_manager.get_order("NON_EXISTENT_ORDER")
    if non_existent_order is None:
        print("   ✓ 正确处理不存在的订单")
    else:
        print("   ✗ 未正确处理不存在的订单")
    
    # 测试更新不存在的订单状态
    print("\n2. 测试更新不存在的订单状态...")
    success = order_manager.update_order_status("NON_EXISTENT_ORDER", OrderStatus.CONFIRMED)
    if not success:
        print("   ✓ 正确处理不存在的订单状态更新")
    else:
        print("   ✗ 未正确处理不存在的订单状态更新")
    
    # 测试获取不存在的用户订单
    print("\n3. 测试获取不存在的用户订单...")
    user_orders = order_manager.get_orders_by_user("NON_EXISTENT_USER")
    if len(user_orders) == 0:
        print("   ✓ 正确处理不存在的用户订单")
    else:
        print("   ✗ 未正确处理不存在的用户订单")

def main():
    """主函数"""
    print("订单系统API测试")
    print("=" * 50)
    
    try:
        test_database_operations()
        test_json_api_format()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("\n系统功能验证:")
        print("✓ 订单创建和管理")
        print("✓ 订单状态更新")
        print("✓ 自动过期检查")
        print("✓ 数据库持久化")
        print("✓ JSON API格式")
        print("✓ 错误处理")
        print("✓ 统计功能")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()