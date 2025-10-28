"""
电商优惠券系统 - API接口
提供RESTful API接口用于优惠券的增删改查和使用
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List
import logging

from coupon_service import CouponService, CouponCreateRequest, CouponType
from coupon_models import CouponStatus, UsageStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupon_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
coupon_service = CouponService(db.session)


def validate_request_data(data: Dict, required_fields: List[str]) -> tuple[bool, str]:
    """验证请求数据"""
    for field in required_fields:
        if field not in data:
            return False, f"缺少必需字段: {field}"
    return True, ""


def format_coupon_response(coupon) -> Dict:
    """格式化优惠券响应数据"""
    return {
        'id': coupon.id,
        'code': coupon.code,
        'name': coupon.name,
        'description': coupon.description,
        'coupon_type': coupon.coupon_type,
        'discount_value': float(coupon.discount_value),
        'min_order_amount': float(coupon.min_order_amount),
        'max_discount_amount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
        'total_quantity': coupon.total_quantity,
        'used_quantity': coupon.used_quantity,
        'per_user_limit': coupon.per_user_limit,
        'valid_from': coupon.valid_from.isoformat(),
        'valid_until': coupon.valid_until.isoformat(),
        'status': coupon.status,
        'is_public': coupon.is_public,
        'priority': coupon.priority,
        'created_at': coupon.created_at.isoformat(),
        'updated_at': coupon.updated_at.isoformat()
    }


# ==================== 优惠券管理API ====================

@app.route('/api/coupons', methods=['POST'])
def create_coupon():
    """创建优惠券"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'coupon_type', 'discount_value']
        is_valid, error_msg = validate_request_data(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # 验证优惠券类型
        try:
            coupon_type = CouponType(data['coupon_type'])
        except ValueError:
            return jsonify({'success': False, 'message': '无效的优惠券类型'}), 400
        
        # 创建请求对象
        create_request = CouponCreateRequest(
            name=data['name'],
            description=data.get('description', ''),
            coupon_type=coupon_type,
            discount_value=Decimal(str(data['discount_value'])),
            min_order_amount=Decimal(str(data.get('min_order_amount', 0))),
            max_discount_amount=Decimal(str(data['max_discount_amount'])) if data.get('max_discount_amount') else None,
            total_quantity=data.get('total_quantity', 0),
            per_user_limit=data.get('per_user_limit', 1),
            valid_days=data.get('valid_days', 30),
            applicable_products=data.get('applicable_products', []),
            applicable_categories=data.get('applicable_categories', []),
            excluded_products=data.get('excluded_products', []),
            is_public=data.get('is_public', True),
            priority=data.get('priority', 0)
        )
        
        # 创建优惠券
        created_by = data.get('created_by', 1)  # 实际应用中从认证信息获取
        coupon = coupon_service.create_coupon(create_request, created_by)
        
        return jsonify({
            'success': True,
            'message': '优惠券创建成功',
            'data': format_coupon_response(coupon)
        }), 201
        
    except Exception as e:
        logger.error(f"创建优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建优惠券失败: {str(e)}'}), 500


@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    """获取优惠券列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')
        coupon_type = request.args.get('coupon_type')
        
        # 构建查询
        query = db.session.query(Coupon)
        
        if status:
            query = query.filter(Coupon.status == status)
        
        if coupon_type:
            query = query.filter(Coupon.coupon_type == coupon_type)
        
        # 分页
        total = query.count()
        coupons = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': {
                'coupons': [format_coupon_response(coupon) for coupon in coupons],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取优惠券列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取优惠券列表失败: {str(e)}'}), 500


@app.route('/api/coupons/<int:coupon_id>', methods=['GET'])
def get_coupon(coupon_id):
    """获取单个优惠券详情"""
    try:
        coupon = db.session.query(Coupon).filter(Coupon.id == coupon_id).first()
        
        if not coupon:
            return jsonify({'success': False, 'message': '优惠券不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': format_coupon_response(coupon)
        })
        
    except Exception as e:
        logger.error(f"获取优惠券详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取优惠券详情失败: {str(e)}'}), 500


@app.route('/api/coupons/<int:coupon_id>', methods=['PUT'])
def update_coupon(coupon_id):
    """更新优惠券"""
    try:
        coupon = db.session.query(Coupon).filter(Coupon.id == coupon_id).first()
        
        if not coupon:
            return jsonify({'success': False, 'message': '优惠券不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            coupon.name = data['name']
        if 'description' in data:
            coupon.description = data['description']
        if 'status' in data:
            coupon.status = data['status']
        if 'is_public' in data:
            coupon.is_public = data['is_public']
        if 'priority' in data:
            coupon.priority = data['priority']
        
        coupon.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '优惠券更新成功',
            'data': format_coupon_response(coupon)
        })
        
    except Exception as e:
        logger.error(f"更新优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新优惠券失败: {str(e)}'}), 500


@app.route('/api/coupons/<int:coupon_id>', methods=['DELETE'])
def delete_coupon(coupon_id):
    """删除优惠券"""
    try:
        coupon = db.session.query(Coupon).filter(Coupon.id == coupon_id).first()
        
        if not coupon:
            return jsonify({'success': False, 'message': '优惠券不存在'}), 404
        
        # 软删除
        coupon.status = CouponStatus.DELETED.value
        coupon.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '优惠券删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除优惠券失败: {str(e)}'}), 500


# ==================== 优惠券使用API ====================

@app.route('/api/coupons/validate', methods=['POST'])
def validate_coupon():
    """验证优惠券"""
    try:
        data = request.get_json()
        
        required_fields = ['coupon_code', 'user_id', 'order_amount']
        is_valid, error_msg = validate_request_data(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        result = coupon_service.validate_coupon(
            coupon_code=data['coupon_code'],
            user_id=data['user_id'],
            order_amount=Decimal(str(data['order_amount'])),
            product_ids=data.get('product_ids', [])
        )
        
        return jsonify({
            'success': result.is_valid,
            'message': result.error_message if not result.is_valid else '优惠券验证成功',
            'data': {
                'is_valid': result.is_valid,
                'discount_amount': float(result.discount_amount),
                'final_amount': float(result.final_amount)
            }
        })
        
    except Exception as e:
        logger.error(f"验证优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'验证优惠券失败: {str(e)}'}), 500


@app.route('/api/coupons/use', methods=['POST'])
def use_coupon():
    """使用优惠券"""
    try:
        data = request.get_json()
        
        required_fields = ['coupon_code', 'user_id', 'order_id', 'order_amount']
        is_valid, error_msg = validate_request_data(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        success, message, discount_amount = coupon_service.use_coupon(
            coupon_code=data['coupon_code'],
            user_id=data['user_id'],
            order_id=data['order_id'],
            order_amount=Decimal(str(data['order_amount'])),
            product_ids=data.get('product_ids', [])
        )
        
        return jsonify({
            'success': success,
            'message': message,
            'data': {
                'discount_amount': float(discount_amount)
            }
        })
        
    except Exception as e:
        logger.error(f"使用优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'使用优惠券失败: {str(e)}'}), 500


@app.route('/api/coupons/claim', methods=['POST'])
def claim_coupon():
    """领取优惠券"""
    try:
        data = request.get_json()
        
        required_fields = ['coupon_id', 'user_id']
        is_valid, error_msg = validate_request_data(data, required_fields)
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        success, message = coupon_service.claim_coupon(
            coupon_id=data['coupon_id'],
            user_id=data['user_id']
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"领取优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'领取优惠券失败: {str(e)}'}), 500


@app.route('/api/users/<int:user_id>/coupons', methods=['GET'])
def get_user_coupons(user_id):
    """获取用户优惠券列表"""
    try:
        status = request.args.get('status')
        usage_status = UsageStatus(status) if status else None
        
        coupons = coupon_service.get_user_coupons(user_id, usage_status)
        
        return jsonify({
            'success': True,
            'data': coupons
        })
        
    except Exception as e:
        logger.error(f"获取用户优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取用户优惠券失败: {str(e)}'}), 500


@app.route('/api/coupons/available', methods=['GET'])
def get_available_coupons():
    """获取可用优惠券列表"""
    try:
        user_id = int(request.args.get('user_id', 0))
        order_amount = request.args.get('order_amount')
        order_amount = Decimal(str(order_amount)) if order_amount else None
        
        coupons = coupon_service.get_available_coupons(user_id, order_amount)
        
        return jsonify({
            'success': True,
            'data': coupons
        })
        
    except Exception as e:
        logger.error(f"获取可用优惠券失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取可用优惠券失败: {str(e)}'}), 500


# ==================== 优惠券统计API ====================

@app.route('/api/coupons/<int:coupon_id>/statistics', methods=['GET'])
def get_coupon_statistics(coupon_id):
    """获取优惠券统计信息"""
    try:
        statistics = coupon_service.get_coupon_statistics(coupon_id)
        
        if not statistics:
            return jsonify({'success': False, 'message': '优惠券不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        logger.error(f"获取优惠券统计失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取优惠券统计失败: {str(e)}'}), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500


# ==================== 数据库初始化 ====================

def init_database():
    """初始化数据库"""
    with app.app_context():
        from coupon_models import Base
        Base.metadata.create_all(bind=db.engine)
        logger.info("数据库初始化完成")


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)