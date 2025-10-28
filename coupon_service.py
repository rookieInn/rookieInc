"""
电商优惠券系统 - 业务逻辑服务
包含优惠券的创建、验证、使用等核心业务逻辑
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from coupon_models import (
    Coupon, CouponUsage, UserCoupon, CouponRule, CouponTemplate,
    CouponType, CouponStatus, UsageStatus, Base
)


@dataclass
class CouponValidationResult:
    """优惠券验证结果"""
    is_valid: bool
    error_message: str = ""
    discount_amount: Decimal = Decimal('0')
    final_amount: Decimal = Decimal('0')


@dataclass
class CouponCreateRequest:
    """优惠券创建请求"""
    name: str
    description: str
    coupon_type: CouponType
    discount_value: Decimal
    min_order_amount: Decimal = Decimal('0')
    max_discount_amount: Optional[Decimal] = None
    total_quantity: int = 0
    per_user_limit: int = 1
    valid_days: int = 30
    applicable_products: List[int] = None
    applicable_categories: List[int] = None
    excluded_products: List[int] = None
    is_public: bool = True
    priority: int = 0


class CouponService:
    """优惠券业务服务类"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def generate_coupon_code(self, prefix: str = "COUPON") -> str:
        """生成优惠券代码"""
        timestamp = str(int(datetime.now().timestamp()))
        random_str = str(uuid.uuid4()).replace('-', '')[:8]
        code = f"{prefix}{timestamp[-6:]}{random_str}".upper()
        return code
    
    def create_coupon(self, request: CouponCreateRequest, created_by: int) -> Coupon:
        """创建优惠券"""
        # 生成优惠券代码
        code = self.generate_coupon_code()
        
        # 计算有效期
        valid_from = datetime.utcnow()
        valid_until = valid_from + timedelta(days=request.valid_days)
        
        # 创建优惠券对象
        coupon = Coupon(
            code=code,
            name=request.name,
            description=request.description,
            coupon_type=request.coupon_type.value,
            discount_value=request.discount_value,
            min_order_amount=request.min_order_amount,
            max_discount_amount=request.max_discount_amount,
            total_quantity=request.total_quantity,
            per_user_limit=request.per_user_limit,
            valid_from=valid_from,
            valid_until=valid_until,
            applicable_products=request.applicable_products or [],
            applicable_categories=request.applicable_categories or [],
            excluded_products=request.excluded_products or [],
            status=CouponStatus.ACTIVE.value,
            is_public=request.is_public,
            priority=request.priority,
            created_by=created_by
        )
        
        self.db.add(coupon)
        self.db.commit()
        return coupon
    
    def validate_coupon(self, coupon_code: str, user_id: int, 
                       order_amount: Decimal, product_ids: List[int] = None) -> CouponValidationResult:
        """验证优惠券是否可用"""
        try:
            # 查找优惠券
            coupon = self.db.query(Coupon).filter(
                Coupon.code == coupon_code,
                Coupon.status == CouponStatus.ACTIVE.value
            ).first()
            
            if not coupon:
                return CouponValidationResult(False, "优惠券不存在或已失效")
            
            # 检查有效期
            now = datetime.utcnow()
            if now < coupon.valid_from or now > coupon.valid_until:
                return CouponValidationResult(False, "优惠券已过期")
            
            # 检查使用数量限制
            if coupon.total_quantity > 0 and coupon.used_quantity >= coupon.total_quantity:
                return CouponValidationResult(False, "优惠券已用完")
            
            # 检查用户使用次数限制
            user_usage_count = self.db.query(CouponUsage).filter(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.user_id == user_id,
                CouponUsage.status == UsageStatus.USED.value
            ).count()
            
            if user_usage_count >= coupon.per_user_limit:
                return CouponValidationResult(False, f"您已达到使用次数限制（{coupon.per_user_limit}次）")
            
            # 检查最低订单金额
            if order_amount < coupon.min_order_amount:
                return CouponValidationResult(False, f"订单金额需满{coupon.min_order_amount}元")
            
            # 检查商品适用范围
            if product_ids:
                if coupon.applicable_products and not any(pid in coupon.applicable_products for pid in product_ids):
                    return CouponValidationResult(False, "优惠券不适用于当前商品")
                
                if coupon.excluded_products and any(pid in coupon.excluded_products for pid in product_ids):
                    return CouponValidationResult(False, "优惠券不适用于当前商品")
            
            # 计算折扣金额
            discount_amount = self._calculate_discount_amount(coupon, order_amount)
            final_amount = order_amount - discount_amount
            
            return CouponValidationResult(
                is_valid=True,
                discount_amount=discount_amount,
                final_amount=max(final_amount, Decimal('0'))
            )
            
        except Exception as e:
            return CouponValidationResult(False, f"验证优惠券时发生错误: {str(e)}")
    
    def _calculate_discount_amount(self, coupon: Coupon, order_amount: Decimal) -> Decimal:
        """计算折扣金额"""
        if coupon.coupon_type == CouponType.FIXED_AMOUNT.value:
            # 固定金额减免
            discount = coupon.discount_value
        elif coupon.coupon_type == CouponType.PERCENTAGE.value:
            # 百分比折扣
            discount = order_amount * (coupon.discount_value / 100)
        elif coupon.coupon_type == CouponType.FREE_SHIPPING.value:
            # 免运费（这里假设运费是固定值，实际应该从订单中获取）
            discount = Decimal('10')  # 示例运费
        else:
            discount = Decimal('0')
        
        # 应用最大折扣金额限制
        if coupon.max_discount_amount and discount > coupon.max_discount_amount:
            discount = coupon.max_discount_amount
        
        # 折扣不能超过订单金额
        return min(discount, order_amount)
    
    def use_coupon(self, coupon_code: str, user_id: int, order_id: str, 
                   order_amount: Decimal, product_ids: List[int] = None) -> Tuple[bool, str, Decimal]:
        """使用优惠券"""
        try:
            # 验证优惠券
            validation_result = self.validate_coupon(coupon_code, user_id, order_amount, product_ids)
            if not validation_result.is_valid:
                return False, validation_result.error_message, Decimal('0')
            
            # 查找优惠券
            coupon = self.db.query(Coupon).filter(Coupon.code == coupon_code).first()
            
            # 创建使用记录
            usage = CouponUsage(
                coupon_id=coupon.id,
                user_id=user_id,
                order_id=order_id,
                discount_amount=validation_result.discount_amount,
                order_amount=order_amount,
                final_amount=validation_result.final_amount,
                status=UsageStatus.USED.value,
                used_at=datetime.utcnow()
            )
            
            self.db.add(usage)
            
            # 更新优惠券使用数量
            coupon.used_quantity += 1
            
            # 更新用户优惠券状态
            user_coupon = self.db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon.id,
                UserCoupon.status == UsageStatus.UNUSED.value
            ).first()
            
            if user_coupon:
                user_coupon.status = UsageStatus.USED.value
                user_coupon.used_at = datetime.utcnow()
            
            self.db.commit()
            
            return True, "优惠券使用成功", validation_result.discount_amount
            
        except Exception as e:
            self.db.rollback()
            return False, f"使用优惠券时发生错误: {str(e)}", Decimal('0')
    
    def get_user_coupons(self, user_id: int, status: UsageStatus = None) -> List[Dict]:
        """获取用户优惠券列表"""
        query = self.db.query(UserCoupon, Coupon).join(Coupon).filter(
            UserCoupon.user_id == user_id
        )
        
        if status:
            query = query.filter(UserCoupon.status == status.value)
        
        results = query.all()
        
        coupons = []
        for user_coupon, coupon in results:
            coupons.append({
                'id': user_coupon.id,
                'coupon_id': coupon.id,
                'code': coupon.code,
                'name': coupon.name,
                'description': coupon.description,
                'coupon_type': coupon.coupon_type,
                'discount_value': float(coupon.discount_value),
                'min_order_amount': float(coupon.min_order_amount),
                'valid_until': coupon.valid_until,
                'status': user_coupon.status,
                'received_at': user_coupon.received_at,
                'used_at': user_coupon.used_at,
                'expired_at': user_coupon.expired_at
            })
        
        return coupons
    
    def claim_coupon(self, coupon_id: int, user_id: int) -> Tuple[bool, str]:
        """用户领取优惠券"""
        try:
            # 查找优惠券
            coupon = self.db.query(Coupon).filter(
                Coupon.id == coupon_id,
                Coupon.status == CouponStatus.ACTIVE.value
            ).first()
            
            if not coupon:
                return False, "优惠券不存在或已失效"
            
            # 检查是否公开
            if not coupon.is_public:
                return False, "该优惠券不可领取"
            
            # 检查有效期
            now = datetime.utcnow()
            if now < coupon.valid_from or now > coupon.valid_until:
                return False, "优惠券已过期"
            
            # 检查用户是否已领取
            existing_user_coupon = self.db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id
            ).first()
            
            if existing_user_coupon:
                return False, "您已领取过该优惠券"
            
            # 检查用户领取次数限制
            user_claim_count = self.db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon_id
            ).count()
            
            if user_claim_count >= coupon.per_user_limit:
                return False, f"您已达到领取次数限制（{coupon.per_user_limit}次）"
            
            # 创建用户优惠券记录
            user_coupon = UserCoupon(
                user_id=user_id,
                coupon_id=coupon_id,
                expired_at=coupon.valid_until
            )
            
            self.db.add(user_coupon)
            self.db.commit()
            
            return True, "优惠券领取成功"
            
        except Exception as e:
            self.db.rollback()
            return False, f"领取优惠券时发生错误: {str(e)}"
    
    def get_available_coupons(self, user_id: int, order_amount: Decimal = None) -> List[Dict]:
        """获取可用优惠券列表"""
        now = datetime.utcnow()
        
        # 查询公开的、有效的优惠券
        query = self.db.query(Coupon).filter(
            Coupon.status == CouponStatus.ACTIVE.value,
            Coupon.is_public == True,
            Coupon.valid_from <= now,
            Coupon.valid_until >= now
        )
        
        # 如果有订单金额，过滤最低订单金额
        if order_amount:
            query = query.filter(Coupon.min_order_amount <= order_amount)
        
        coupons = query.all()
        
        result = []
        for coupon in coupons:
            # 检查用户是否已领取
            user_coupon = self.db.query(UserCoupon).filter(
                UserCoupon.user_id == user_id,
                UserCoupon.coupon_id == coupon.id
            ).first()
            
            result.append({
                'id': coupon.id,
                'code': coupon.code,
                'name': coupon.name,
                'description': coupon.description,
                'coupon_type': coupon.coupon_type,
                'discount_value': float(coupon.discount_value),
                'min_order_amount': float(coupon.min_order_amount),
                'max_discount_amount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
                'valid_until': coupon.valid_until,
                'is_claimed': user_coupon is not None,
                'remaining_quantity': coupon.total_quantity - coupon.used_quantity if coupon.total_quantity > 0 else None
            })
        
        return result
    
    def cancel_coupon_usage(self, usage_id: int) -> Tuple[bool, str]:
        """取消优惠券使用"""
        try:
            usage = self.db.query(CouponUsage).filter(
                CouponUsage.id == usage_id,
                CouponUsage.status == UsageStatus.USED.value
            ).first()
            
            if not usage:
                return False, "使用记录不存在或已取消"
            
            # 更新使用记录状态
            usage.status = UsageStatus.CANCELLED.value
            usage.updated_at = datetime.utcnow()
            
            # 更新优惠券使用数量
            coupon = self.db.query(Coupon).filter(Coupon.id == usage.coupon_id).first()
            if coupon:
                coupon.used_quantity = max(0, coupon.used_quantity - 1)
            
            # 更新用户优惠券状态
            user_coupon = self.db.query(UserCoupon).filter(
                UserCoupon.user_id == usage.user_id,
                UserCoupon.coupon_id == usage.coupon_id,
                UserCoupon.status == UsageStatus.USED.value
            ).first()
            
            if user_coupon:
                user_coupon.status = UsageStatus.UNUSED.value
                user_coupon.used_at = None
            
            self.db.commit()
            
            return True, "优惠券使用已取消"
            
        except Exception as e:
            self.db.rollback()
            return False, f"取消优惠券使用时发生错误: {str(e)}"
    
    def get_coupon_statistics(self, coupon_id: int) -> Dict:
        """获取优惠券统计信息"""
        coupon = self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            return {}
        
        # 使用统计
        total_usage = self.db.query(CouponUsage).filter(
            CouponUsage.coupon_id == coupon_id,
            CouponUsage.status == UsageStatus.USED.value
        ).count()
        
        # 今日使用
        today = datetime.utcnow().date()
        today_usage = self.db.query(CouponUsage).filter(
            CouponUsage.coupon_id == coupon_id,
            CouponUsage.status == UsageStatus.USED.value,
            CouponUsage.used_at >= today
        ).count()
        
        # 总折扣金额
        total_discount = self.db.query(CouponUsage).filter(
            CouponUsage.coupon_id == coupon_id,
            CouponUsage.status == UsageStatus.USED.value
        ).with_entities(CouponUsage.discount_amount).all()
        
        total_discount_amount = sum([float(amount[0]) for amount in total_discount])
        
        return {
            'coupon_id': coupon_id,
            'coupon_name': coupon.name,
            'total_quantity': coupon.total_quantity,
            'used_quantity': total_usage,
            'remaining_quantity': coupon.total_quantity - total_usage if coupon.total_quantity > 0 else None,
            'today_usage': today_usage,
            'total_discount_amount': total_discount_amount,
            'usage_rate': (total_usage / coupon.total_quantity * 100) if coupon.total_quantity > 0 else 0
        }