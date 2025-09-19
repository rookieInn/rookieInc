"""
订单管理API接口
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from order_models import OrderManager, OrderStatus, Order
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
order_manager = OrderManager()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['user_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 创建订单
        order = order_manager.create_order(
            user_id=data['user_id'],
            amount=float(data['amount']),
            items=data.get('items', []),
            customer_info=data.get('customer_info', {}),
            expiry_minutes=data.get('expiry_minutes', 30)
        )
        
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"创建订单失败: {e}")
        return jsonify({'error': '创建订单失败', 'details': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """获取订单详情"""
    try:
        order = order_manager.get_order(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取订单失败: {e}")
        return jsonify({'error': '获取订单失败', 'details': str(e)}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新订单状态"""
    try:
        data = request.get_json()
        new_status_str = data.get('status')
        message = data.get('message', '')
        
        if not new_status_str:
            return jsonify({'error': '缺少状态字段'}), 400
        
        try:
            new_status = OrderStatus(new_status_str)
        except ValueError:
            return jsonify({'error': '无效的订单状态'}), 400
        
        # 检查订单是否存在
        order = order_manager.get_order(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        # 更新状态
        success = order_manager.update_order_status(order_id, new_status, message)
        if not success:
            return jsonify({'error': '更新订单状态失败'}), 500
        
        # 返回更新后的订单
        updated_order = order_manager.get_order(order_id)
        return jsonify({
            'success': True,
            'message': '订单状态更新成功',
            'order': updated_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"更新订单状态失败: {e}")
        return jsonify({'error': '更新订单状态失败', 'details': str(e)}), 500

@app.route('/api/orders/user/<user_id>', methods=['GET'])
def get_user_orders(user_id):
    """获取用户的所有订单"""
    try:
        orders = order_manager.get_orders_by_user(user_id)
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders],
            'count': len(orders)
        })
        
    except Exception as e:
        logger.error(f"获取用户订单失败: {e}")
        return jsonify({'error': '获取用户订单失败', 'details': str(e)}), 500

@app.route('/api/orders/statistics', methods=['GET'])
def get_order_statistics():
    """获取订单统计信息"""
    try:
        stats = order_manager.get_order_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"获取订单统计失败: {e}")
        return jsonify({'error': '获取订单统计失败', 'details': str(e)}), 500

@app.route('/api/orders/expired', methods=['GET'])
def get_expired_orders():
    """获取已过期的订单"""
    try:
        expired_orders = order_manager.get_expired_orders()
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in expired_orders],
            'count': len(expired_orders)
        })
        
    except Exception as e:
        logger.error(f"获取过期订单失败: {e}")
        return jsonify({'error': '获取过期订单失败', 'details': str(e)}), 500

@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', '用户取消')
        
        # 检查订单是否存在
        order = order_manager.get_order(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        # 检查订单是否可以取消
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.EXPIRED]:
            return jsonify({'error': '订单无法取消'}), 400
        
        # 取消订单
        success = order_manager.update_order_status(order_id, OrderStatus.CANCELLED, reason)
        if not success:
            return jsonify({'error': '取消订单失败'}), 500
        
        # 返回更新后的订单
        updated_order = order_manager.get_order(order_id)
        return jsonify({
            'success': True,
            'message': '订单取消成功',
            'order': updated_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"取消订单失败: {e}")
        return jsonify({'error': '取消订单失败', 'details': str(e)}), 500

@app.route('/api/orders/<order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    """确认订单"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '订单确认')
        
        # 检查订单是否存在
        order = order_manager.get_order(order_id)
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        # 检查订单是否可以确认
        if order.status != OrderStatus.PENDING:
            return jsonify({'error': '订单无法确认'}), 400
        
        # 确认订单
        success = order_manager.update_order_status(order_id, OrderStatus.CONFIRMED, message)
        if not success:
            return jsonify({'error': '确认订单失败'}), 500
        
        # 返回更新后的订单
        updated_order = order_manager.get_order(order_id)
        return jsonify({
            'success': True,
            'message': '订单确认成功',
            'order': updated_order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"确认订单失败: {e}")
        return jsonify({'error': '确认订单失败', 'details': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'order-management-api'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    logger.info("订单管理API服务启动中...")
    app.run(host='0.0.0.0', port=5000, debug=True)