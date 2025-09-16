"""
电商优惠券系统 - 数据库模型
支持多种优惠券类型：满减券、折扣券、免运费券等
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Decimal as SQLDecimal, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON

Base = declarative_base()


class CouponType(Enum):
    """优惠券类型枚举"""
    FIXED_AMOUNT = "fixed_amount"  # 固定金额减免
    PERCENTAGE = "percentage"      # 百分比折扣
    FREE_SHIPPING = "free_shipping"  # 免运费
    BUY_X_GET_Y = "buy_x_get_y"   # 买X送Y
    CASHBACK = "cashback"          # 返现


class CouponStatus(Enum):
    """优惠券状态枚举"""
    DRAFT = "draft"           # 草稿
    ACTIVE = "active"         # 激活
    PAUSED = "paused"         # 暂停
    EXPIRED = "expired"       # 过期
    DELETED = "deleted"       # 删除


class UsageStatus(Enum):
    """使用状态枚举"""
    UNUSED = "unused"         # 未使用
    USED = "used"            # 已使用
    EXPIRED = "expired"      # 已过期
    CANCELLED = "cancelled"   # 已取消


class Coupon(Base):
    """优惠券主表"""
    __tablename__ = 'coupons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="优惠券代码")
    name = Column(String(100), nullable=False, comment="优惠券名称")
    description = Column(Text, comment="优惠券描述")
    
    # 优惠券类型和规则
    coupon_type = Column(String(20), nullable=False, comment="优惠券类型")
    discount_value = Column(SQLDecimal(10, 2), comment="折扣值（金额或百分比）")
    min_order_amount = Column(SQLDecimal(10, 2), default=0, comment="最低订单金额")
    max_discount_amount = Column(SQLDecimal(10, 2), comment="最大折扣金额")
    
    # 使用限制
    total_quantity = Column(Integer, default=0, comment="总发行数量，0表示无限制")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    per_user_limit = Column(Integer, default=1, comment="每用户限用次数")
    
    # 时间限制
    valid_from = Column(DateTime, nullable=False, comment="有效期开始时间")
    valid_until = Column(DateTime, nullable=False, comment="有效期结束时间")
    
    # 适用范围
    applicable_products = Column(JSON, comment="适用商品ID列表")
    applicable_categories = Column(JSON, comment="适用分类ID列表")
    excluded_products = Column(JSON, comment="排除商品ID列表")
    
    # 状态和元数据
    status = Column(String(20), default=CouponStatus.DRAFT.value, comment="优惠券状态")
    is_public = Column(Boolean, default=True, comment="是否公开")
    priority = Column(Integer, default=0, comment="优先级，数字越大优先级越高")
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    created_by = Column(Integer, comment="创建人ID")
    
    # 关联关系
    usages = relationship("CouponUsage", back_populates="coupon")
    
    # 索引
    __table_args__ = (
        Index('idx_coupon_code', 'code'),
        Index('idx_coupon_status', 'status'),
        Index('idx_coupon_valid_time', 'valid_from', 'valid_until'),
        Index('idx_coupon_type', 'coupon_type'),
    )


class CouponUsage(Base):
    """优惠券使用记录表"""
    __tablename__ = 'coupon_usages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False, comment="优惠券ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    order_id = Column(String(50), comment="订单ID")
    
    # 使用详情
    discount_amount = Column(SQLDecimal(10, 2), nullable=False, comment="实际折扣金额")
    order_amount = Column(SQLDecimal(10, 2), nullable=False, comment="订单金额")
    final_amount = Column(SQLDecimal(10, 2), nullable=False, comment="最终支付金额")
    
    # 状态和时间
    status = Column(String(20), default=UsageStatus.UNUSED.value, comment="使用状态")
    used_at = Column(DateTime, comment="使用时间")
    expired_at = Column(DateTime, comment="过期时间")
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    coupon = relationship("Coupon", back_populates="usages")
    
    # 索引
    __table_args__ = (
        Index('idx_usage_user', 'user_id'),
        Index('idx_usage_coupon', 'coupon_id'),
        Index('idx_usage_order', 'order_id'),
        Index('idx_usage_status', 'status'),
    )


class CouponTemplate(Base):
    """优惠券模板表"""
    __tablename__ = 'coupon_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, comment="模板描述")
    
    # 模板配置
    template_config = Column(JSON, nullable=False, comment="模板配置JSON")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    created_by = Column(Integer, comment="创建人ID")


class UserCoupon(Base):
    """用户优惠券表（用户领取的优惠券）"""
    __tablename__ = 'user_coupons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False, comment="优惠券ID")
    
    # 状态和时间
    status = Column(String(20), default=UsageStatus.UNUSED.value, comment="使用状态")
    received_at = Column(DateTime, default=datetime.utcnow, comment="领取时间")
    used_at = Column(DateTime, comment="使用时间")
    expired_at = Column(DateTime, comment="过期时间")
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    coupon = relationship("Coupon")
    
    # 索引
    __table_args__ = (
        Index('idx_user_coupon_user', 'user_id'),
        Index('idx_user_coupon_coupon', 'coupon_id'),
        Index('idx_user_coupon_status', 'status'),
        Index('idx_user_coupon_expired', 'expired_at'),
    )


class CouponRule(Base):
    """优惠券规则表（复杂规则配置）"""
    __tablename__ = 'coupon_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=False, comment="优惠券ID")
    rule_type = Column(String(50), nullable=False, comment="规则类型")
    rule_config = Column(JSON, nullable=False, comment="规则配置")
    priority = Column(Integer, default=0, comment="规则优先级")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    coupon = relationship("Coupon")
    
    # 索引
    __table_args__ = (
        Index('idx_rule_coupon', 'coupon_id'),
        Index('idx_rule_type', 'rule_type'),
        Index('idx_rule_priority', 'priority'),
    )