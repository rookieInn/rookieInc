"""
电商优惠券系统 - 高级验证和使用逻辑
包含复杂的优惠券规则验证、批量操作、定时任务等
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

from coupon_models import Coupon, CouponUsage, UserCoupon, CouponRule, CouponType, CouponStatus, UsageStatus
from coupon_service import CouponService, CouponValidationResult

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """规则类型枚举"""
    TIME_LIMIT = "time_limit"           # 时间限制
    USER_LIMIT = "user_limit"           # 用户限制
    PRODUCT_LIMIT = "product_limit"     # 商品限制
    CATEGORY_LIMIT = "category_limit"   # 分类限制
    AMOUNT_LIMIT = "amount_limit"       # 金额限制
    FREQUENCY_LIMIT = "frequency_limit" # 频率限制
    COMBINATION_LIMIT = "combination_limit" # 组合限制


@dataclass
class ValidationContext:
    """验证上下文"""
    user_id: int
    order_amount: Decimal
    product_ids: List[int]
    category_ids: List[int]
    order_time: datetime
    user_level: str = "normal"
    user_registration_time: datetime = None
    user_total_orders: int = 0
    user_total_amount: Decimal = Decimal('0')


class AdvancedCouponValidator:
    """高级优惠券验证器"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.coupon_service = CouponService(db_session)
    
    async def validate_coupon_advanced(self, coupon_code: str, context: ValidationContext) -> CouponValidationResult:
        """高级优惠券验证"""
        try:
            # 基础验证
            basic_result = self.coupon_service.validate_coupon(
                coupon_code=coupon_code,
                user_id=context.user_id,
                order_amount=context.order_amount,
                product_ids=context.product_ids
            )
            
            if not basic_result.is_valid:
                return basic_result
            
            # 查找优惠券
            coupon = self.db.query(Coupon).filter(
                Coupon.code == coupon_code,
                Coupon.status == CouponStatus.ACTIVE.value
            ).first()
            
            if not coupon:
                return CouponValidationResult(False, "优惠券不存在")
            
            # 高级规则验证
            advanced_result = await self._validate_advanced_rules(coupon, context)
            if not advanced_result.is_valid:
                return advanced_result
            
            # 重新计算折扣金额（考虑高级规则）
            discount_amount = await self._calculate_advanced_discount(coupon, context)
            final_amount = context.order_amount - discount_amount
            
            return CouponValidationResult(
                is_valid=True,
                discount_amount=discount_amount,
                final_amount=max(final_amount, Decimal('0'))
            )
            
        except Exception as e:
            logger.error(f"高级优惠券验证失败: {str(e)}")
            return CouponValidationResult(False, f"验证失败: {str(e)}")
    
    async def _validate_advanced_rules(self, coupon: Coupon, context: ValidationContext) -> CouponValidationResult:
        """验证高级规则"""
        try:
            # 获取优惠券的所有规则
            rules = self.db.query(CouponRule).filter(
                CouponRule.coupon_id == coupon.id,
                CouponRule.is_active == True
            ).order_by(CouponRule.priority.desc()).all()
            
            for rule in rules:
                rule_result = await self._validate_single_rule(rule, context)
                if not rule_result.is_valid:
                    return rule_result
            
            return CouponValidationResult(True)
            
        except Exception as e:
            logger.error(f"验证高级规则失败: {str(e)}")
            return CouponValidationResult(False, f"规则验证失败: {str(e)}")
    
    async def _validate_single_rule(self, rule: CouponRule, context: ValidationContext) -> CouponValidationResult:
        """验证单个规则"""
        try:
            rule_config = rule.rule_config
            rule_type = rule.rule_type
            
            if rule_type == RuleType.TIME_LIMIT.value:
                return await self._validate_time_limit(rule_config, context)
            elif rule_type == RuleType.USER_LIMIT.value:
                return await self._validate_user_limit(rule_config, context)
            elif rule_type == RuleType.PRODUCT_LIMIT.value:
                return await self._validate_product_limit(rule_config, context)
            elif rule_type == RuleType.CATEGORY_LIMIT.value:
                return await self._validate_category_limit(rule_config, context)
            elif rule_type == RuleType.AMOUNT_LIMIT.value:
                return await self._validate_amount_limit(rule_config, context)
            elif rule_type == RuleType.FREQUENCY_LIMIT.value:
                return await self._validate_frequency_limit(rule_config, context)
            elif rule_type == RuleType.COMBINATION_LIMIT.value:
                return await self._validate_combination_limit(rule_config, context)
            else:
                return CouponValidationResult(True)
                
        except Exception as e:
            logger.error(f"验证规则失败: {str(e)}")
            return CouponValidationResult(False, f"规则验证失败: {str(e)}")
    
    async def _validate_time_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证时间限制规则"""
        try:
            # 检查特定时间段限制
            if 'allowed_hours' in config:
                current_hour = context.order_time.hour
                if current_hour not in config['allowed_hours']:
                    return CouponValidationResult(False, "当前时间段不可使用此优惠券")
            
            # 检查星期限制
            if 'allowed_weekdays' in config:
                current_weekday = context.order_time.weekday()
                if current_weekday not in config['allowed_weekdays']:
                    return CouponValidationResult(False, "当前日期不可使用此优惠券")
            
            # 检查特定日期限制
            if 'blackout_dates' in config:
                order_date = context.order_time.date()
                if order_date in [datetime.strptime(d, '%Y-%m-%d').date() for d in config['blackout_dates']]:
                    return CouponValidationResult(False, "当前日期不可使用此优惠券")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"时间限制验证失败: {str(e)}")
    
    async def _validate_user_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证用户限制规则"""
        try:
            # 检查用户等级限制
            if 'min_user_level' in config:
                level_priority = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4, 'diamond': 5}
                user_level_priority = level_priority.get(context.user_level, 0)
                min_level_priority = level_priority.get(config['min_user_level'], 0)
                if user_level_priority < min_level_priority:
                    return CouponValidationResult(False, "用户等级不足，无法使用此优惠券")
            
            # 检查用户注册时间限制
            if 'min_registration_days' in config and context.user_registration_time:
                days_since_registration = (context.order_time - context.user_registration_time).days
                if days_since_registration < config['min_registration_days']:
                    return CouponValidationResult(False, "用户注册时间不足，无法使用此优惠券")
            
            # 检查用户历史订单限制
            if 'min_total_orders' in config:
                if context.user_total_orders < config['min_total_orders']:
                    return CouponValidationResult(False, "用户订单数量不足，无法使用此优惠券")
            
            if 'min_total_amount' in config:
                if context.user_total_amount < Decimal(str(config['min_total_amount'])):
                    return CouponValidationResult(False, "用户消费金额不足，无法使用此优惠券")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"用户限制验证失败: {str(e)}")
    
    async def _validate_product_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证商品限制规则"""
        try:
            # 检查必需商品
            if 'required_products' in config:
                if not any(pid in config['required_products'] for pid in context.product_ids):
                    return CouponValidationResult(False, "订单中必须包含指定商品")
            
            # 检查商品数量限制
            if 'min_product_quantity' in config:
                if len(context.product_ids) < config['min_product_quantity']:
                    return CouponValidationResult(False, "商品数量不足")
            
            # 检查商品价格限制
            if 'min_product_price' in config:
                # 这里需要从订单中获取商品价格，暂时跳过
                pass
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"商品限制验证失败: {str(e)}")
    
    async def _validate_category_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证分类限制规则"""
        try:
            # 检查必需分类
            if 'required_categories' in config:
                if not any(cid in config['required_categories'] for cid in context.category_ids):
                    return CouponValidationResult(False, "订单中必须包含指定分类的商品")
            
            # 检查分类数量限制
            if 'min_category_count' in config:
                if len(context.category_ids) < config['min_category_count']:
                    return CouponValidationResult(False, "分类数量不足")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"分类限制验证失败: {str(e)}")
    
    async def _validate_amount_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证金额限制规则"""
        try:
            # 检查订单金额范围
            if 'min_amount' in config:
                if context.order_amount < Decimal(str(config['min_amount'])):
                    return CouponValidationResult(False, f"订单金额需满{config['min_amount']}元")
            
            if 'max_amount' in config:
                if context.order_amount > Decimal(str(config['max_amount'])):
                    return CouponValidationResult(False, f"订单金额不能超过{config['max_amount']}元")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"金额限制验证失败: {str(e)}")
    
    async def _validate_frequency_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证频率限制规则"""
        try:
            # 检查每日使用次数限制
            if 'daily_limit' in config:
                today = context.order_time.date()
                daily_usage = self.db.query(CouponUsage).filter(
                    CouponUsage.user_id == context.user_id,
                    CouponUsage.used_at >= today,
                    CouponUsage.status == UsageStatus.USED.value
                ).count()
                
                if daily_usage >= config['daily_limit']:
                    return CouponValidationResult(False, "今日使用次数已达上限")
            
            # 检查每周使用次数限制
            if 'weekly_limit' in config:
                week_start = context.order_time - timedelta(days=context.order_time.weekday())
                weekly_usage = self.db.query(CouponUsage).filter(
                    CouponUsage.user_id == context.user_id,
                    CouponUsage.used_at >= week_start,
                    CouponUsage.status == UsageStatus.USED.value
                ).count()
                
                if weekly_usage >= config['weekly_limit']:
                    return CouponValidationResult(False, "本周使用次数已达上限")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"频率限制验证失败: {str(e)}")
    
    async def _validate_combination_limit(self, config: Dict, context: ValidationContext) -> CouponValidationResult:
        """验证组合限制规则"""
        try:
            # 检查与其他优惠券的组合使用限制
            if 'excluded_coupons' in config:
                # 检查用户是否同时使用了被排除的优惠券
                excluded_usage = self.db.query(CouponUsage).filter(
                    CouponUsage.user_id == context.user_id,
                    CouponUsage.coupon_id.in_(config['excluded_coupons']),
                    CouponUsage.status == UsageStatus.USED.value
                ).first()
                
                if excluded_usage:
                    return CouponValidationResult(False, "此优惠券不能与其他优惠券同时使用")
            
            # 检查必需组合优惠券
            if 'required_coupons' in config:
                required_usage = self.db.query(CouponUsage).filter(
                    CouponUsage.user_id == context.user_id,
                    CouponUsage.coupon_id.in_(config['required_coupons']),
                    CouponUsage.status == UsageStatus.USED.value
                ).count()
                
                if required_usage < len(config['required_coupons']):
                    return CouponValidationResult(False, "必须先使用指定的优惠券")
            
            return CouponValidationResult(True)
            
        except Exception as e:
            return CouponValidationResult(False, f"组合限制验证失败: {str(e)}")
    
    async def _calculate_advanced_discount(self, coupon: Coupon, context: ValidationContext) -> Decimal:
        """计算高级折扣金额"""
        try:
            # 基础折扣计算
            base_discount = self.coupon_service._calculate_discount_amount(coupon, context.order_amount)
            
            # 应用高级规则调整
            rules = self.db.query(CouponRule).filter(
                CouponRule.coupon_id == coupon.id,
                CouponRule.is_active == True,
                CouponRule.rule_type == 'discount_adjustment'
            ).all()
            
            adjusted_discount = base_discount
            
            for rule in rules:
                rule_config = rule.rule_config
                
                # 用户等级折扣调整
                if 'user_level_multiplier' in rule_config:
                    level_multiplier = rule_config['user_level_multiplier'].get(context.user_level, 1.0)
                    adjusted_discount *= Decimal(str(level_multiplier))
                
                # 时间折扣调整
                if 'time_multiplier' in rule_config:
                    current_hour = context.order_time.hour
                    time_multiplier = rule_config['time_multiplier'].get(str(current_hour), 1.0)
                    adjusted_discount *= Decimal(str(time_multiplier))
                
                # 订单金额折扣调整
                if 'amount_multiplier' in rule_config:
                    for amount_range, multiplier in rule_config['amount_multiplier'].items():
                        min_amount, max_amount = map(Decimal, amount_range.split('-'))
                        if min_amount <= context.order_amount <= max_amount:
                            adjusted_discount *= Decimal(str(multiplier))
                            break
            
            # 确保折扣不超过订单金额
            return min(adjusted_discount, context.order_amount)
            
        except Exception as e:
            logger.error(f"计算高级折扣失败: {str(e)}")
            return base_discount


class CouponBatchProcessor:
    """优惠券批量处理器"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.coupon_service = CouponService(db_session)
    
    async def batch_create_coupons(self, template_id: int, count: int, created_by: int) -> List[Coupon]:
        """批量创建优惠券"""
        try:
            # 获取模板
            template = self.db.query(CouponTemplate).filter(
                CouponTemplate.id == template_id,
                CouponTemplate.is_active == True
            ).first()
            
            if not template:
                raise ValueError("优惠券模板不存在")
            
            template_config = template.template_config
            created_coupons = []
            
            for i in range(count):
                # 生成优惠券代码
                code = self.coupon_service.generate_coupon_code()
                
                # 创建优惠券
                coupon = Coupon(
                    code=code,
                    name=f"{template_config['name']} #{i+1}",
                    description=template_config.get('description', ''),
                    coupon_type=template_config['coupon_type'],
                    discount_value=Decimal(str(template_config['discount_value'])),
                    min_order_amount=Decimal(str(template_config.get('min_order_amount', 0))),
                    max_discount_amount=Decimal(str(template_config['max_discount_amount'])) if template_config.get('max_discount_amount') else None,
                    total_quantity=template_config.get('total_quantity', 0),
                    per_user_limit=template_config.get('per_user_limit', 1),
                    valid_from=datetime.utcnow(),
                    valid_until=datetime.utcnow() + timedelta(days=template_config.get('valid_days', 30)),
                    applicable_products=template_config.get('applicable_products', []),
                    applicable_categories=template_config.get('applicable_categories', []),
                    excluded_products=template_config.get('excluded_products', []),
                    status=CouponStatus.ACTIVE.value,
                    is_public=template_config.get('is_public', True),
                    priority=template_config.get('priority', 0),
                    created_by=created_by
                )
                
                self.db.add(coupon)
                created_coupons.append(coupon)
            
            self.db.commit()
            return created_coupons
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量创建优惠券失败: {str(e)}")
            raise
    
    async def batch_update_coupon_status(self, coupon_ids: List[int], status: CouponStatus) -> int:
        """批量更新优惠券状态"""
        try:
            updated_count = self.db.query(Coupon).filter(
                Coupon.id.in_(coupon_ids)
            ).update({
                'status': status.value,
                'updated_at': datetime.utcnow()
            }, synchronize_session=False)
            
            self.db.commit()
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量更新优惠券状态失败: {str(e)}")
            raise
    
    async def batch_assign_coupons_to_users(self, coupon_id: int, user_ids: List[int]) -> int:
        """批量分配优惠券给用户"""
        try:
            # 检查优惠券是否存在
            coupon = self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
            if not coupon:
                raise ValueError("优惠券不存在")
            
            assigned_count = 0
            for user_id in user_ids:
                # 检查用户是否已领取
                existing = self.db.query(UserCoupon).filter(
                    UserCoupon.user_id == user_id,
                    UserCoupon.coupon_id == coupon_id
                ).first()
                
                if not existing:
                    user_coupon = UserCoupon(
                        user_id=user_id,
                        coupon_id=coupon_id,
                        expired_at=coupon.valid_until
                    )
                    self.db.add(user_coupon)
                    assigned_count += 1
            
            self.db.commit()
            return assigned_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量分配优惠券失败: {str(e)}")
            raise


class CouponScheduler:
    """优惠券定时任务处理器"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def expire_coupons(self) -> int:
        """过期优惠券处理"""
        try:
            now = datetime.utcnow()
            
            # 更新过期的优惠券状态
            expired_coupons = self.db.query(Coupon).filter(
                Coupon.status == CouponStatus.ACTIVE.value,
                Coupon.valid_until < now
            ).all()
            
            for coupon in expired_coupons:
                coupon.status = CouponStatus.EXPIRED.value
                coupon.updated_at = now
            
            # 更新过期的用户优惠券状态
            expired_user_coupons = self.db.query(UserCoupon).filter(
                UserCoupon.status == UsageStatus.UNUSED.value,
                UserCoupon.expired_at < now
            ).all()
            
            for user_coupon in expired_user_coupons:
                user_coupon.status = UsageStatus.EXPIRED.value
                user_coupon.updated_at = now
            
            self.db.commit()
            return len(expired_coupons) + len(expired_user_coupons)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"处理过期优惠券失败: {str(e)}")
            raise
    
    async def cleanup_expired_data(self, days: int = 30) -> int:
        """清理过期数据"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 删除过期的使用记录
            deleted_usage = self.db.query(CouponUsage).filter(
                CouponUsage.created_at < cutoff_date,
                CouponUsage.status == UsageStatus.EXPIRED.value
            ).delete()
            
            # 删除过期的用户优惠券记录
            deleted_user_coupons = self.db.query(UserCoupon).filter(
                UserCoupon.created_at < cutoff_date,
                UserCoupon.status == UsageStatus.EXPIRED.value
            ).delete()
            
            self.db.commit()
            return deleted_usage + deleted_user_coupons
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"清理过期数据失败: {str(e)}")
            raise
    
    async def generate_usage_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """生成使用报告"""
        try:
            # 统计使用数据
            usage_stats = self.db.query(CouponUsage).filter(
                CouponUsage.used_at >= start_date,
                CouponUsage.used_at <= end_date,
                CouponUsage.status == UsageStatus.USED.value
            ).all()
            
            total_usage = len(usage_stats)
            total_discount = sum([float(usage.discount_amount) for usage in usage_stats])
            
            # 按优惠券类型统计
            type_stats = {}
            for usage in usage_stats:
                coupon = self.db.query(Coupon).filter(Coupon.id == usage.coupon_id).first()
                if coupon:
                    coupon_type = coupon.coupon_type
                    if coupon_type not in type_stats:
                        type_stats[coupon_type] = {'count': 0, 'discount': 0}
                    type_stats[coupon_type]['count'] += 1
                    type_stats[coupon_type]['discount'] += float(usage.discount_amount)
            
            # 按日期统计
            daily_stats = {}
            for usage in usage_stats:
                date_str = usage.used_at.date().isoformat()
                if date_str not in daily_stats:
                    daily_stats[date_str] = {'count': 0, 'discount': 0}
                daily_stats[date_str]['count'] += 1
                daily_stats[date_str]['discount'] += float(usage.discount_amount)
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'total_usage': total_usage,
                'total_discount': total_discount,
                'type_stats': type_stats,
                'daily_stats': daily_stats
            }
            
        except Exception as e:
            logger.error(f"生成使用报告失败: {str(e)}")
            raise