"""
电商订单金额计算与优惠规则应用系统

实现多种优惠规则的优先级和互斥关系处理：
- 会员折扣（9.5折，与折扣券互斥）
- 折扣券（与会员折扣互斥，取优惠力度大的）
- 满减券（可叠加，按门槛从低到高判断）
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP


class CouponType(Enum):
    """优惠券类型"""
    FIXED_DISCOUNT = "fixed_discount"  # 满减券
    PERCENTAGE_DISCOUNT = "percentage_discount"  # 折扣券


@dataclass
class Product:
    """商品信息"""
    id: str
    name: str
    price: Decimal  # 单价
    quantity: int
    eligible_for_discount: bool  # 是否参与优惠


@dataclass
class User:
    """用户信息"""
    id: str
    name: str
    is_member: bool  # 是否会员


@dataclass
class Coupon:
    """优惠券信息"""
    id: str
    name: str
    coupon_type: CouponType
    threshold: Optional[Decimal] = None  # 满减券门槛金额
    discount_amount: Optional[Decimal] = None  # 满减券减额
    discount_rate: Optional[Decimal] = None  # 折扣券折扣率
    is_mutually_exclusive: bool = True  # 是否与其他优惠券互斥


@dataclass
class OrderItem:
    """订单商品项"""
    product: Product
    subtotal: Decimal  # 小计金额
    discount_applied: Decimal  # 已应用折扣金额


@dataclass
class DiscountDetail:
    """优惠明细"""
    type: str  # 优惠类型：member_discount, coupon_discount, fixed_discount
    name: str  # 优惠名称
    amount: Decimal  # 优惠金额
    description: str  # 优惠描述


@dataclass
class OrderCalculation:
    """订单计算结果"""
    items: List[OrderItem]
    subtotal: Decimal  # 商品总价
    discountable_amount: Decimal  # 可优惠金额
    non_discountable_amount: Decimal  # 不可优惠金额
    member_discount: Decimal  # 会员折扣金额
    coupon_discount: Decimal  # 折扣券折扣金额
    fixed_discounts: List[DiscountDetail]  # 满减券优惠明细
    total_discount: Decimal  # 总优惠金额
    final_amount: Decimal  # 最终实付金额
    discount_details: List[DiscountDetail]  # 所有优惠明细


class OrderCalculator:
    """订单金额计算器"""
    
    def __init__(self):
        self.member_discount_rate = Decimal('0.95')  # 会员9.5折
    
    def calculate_order(self, 
                       products: List[Product], 
                       user: User, 
                       coupons: List[Coupon]) -> OrderCalculation:
        """
        计算订单金额
        
        Args:
            products: 商品列表
            user: 用户信息
            coupons: 优惠券列表
            
        Returns:
            OrderCalculation: 订单计算结果
        """
        # 1. 计算商品总价和分类
        items = []
        subtotal = Decimal('0')
        discountable_amount = Decimal('0')
        non_discountable_amount = Decimal('0')
        
        for product in products:
            item_subtotal = product.price * product.quantity
            items.append(OrderItem(
                product=product,
                subtotal=item_subtotal,
                discount_applied=Decimal('0')
            ))
            
            subtotal += item_subtotal
            
            if product.eligible_for_discount:
                discountable_amount += item_subtotal
            else:
                non_discountable_amount += item_subtotal
        
        # 2. 应用会员折扣或折扣券（互斥）
        member_discount = Decimal('0')
        coupon_discount = Decimal('0')
        discount_details = []
        
        if user.is_member:
            # 计算会员折扣
            member_discount = discountable_amount * (Decimal('1') - self.member_discount_rate)
            discount_details.append(DiscountDetail(
                type="member_discount",
                name="会员折扣",
                amount=member_discount,
                description=f"会员专享9.5折优惠，优惠金额：¥{member_discount:.2f}"
            ))
        
        # 查找折扣券（与会员折扣互斥）
        discount_coupon = None
        for coupon in coupons:
            if (coupon.coupon_type == CouponType.PERCENTAGE_DISCOUNT and 
                coupon.discount_rate is not None):
                discount_coupon = coupon
                break
        
        # 比较会员折扣和折扣券，选择优惠力度大的
        if discount_coupon and discount_coupon.discount_rate is not None:
            coupon_discount_amount = discountable_amount * (Decimal('1') - discount_coupon.discount_rate)
            
            if coupon_discount_amount > member_discount:
                # 使用折扣券，清除会员折扣
                member_discount = Decimal('0')
                coupon_discount = coupon_discount_amount
                discount_details = [DiscountDetail(
                    type="coupon_discount",
                    name=discount_coupon.name,
                    amount=coupon_discount,
                    description=f"折扣券{discount_coupon.discount_rate * 100:.1f}折优惠，优惠金额：¥{coupon_discount:.2f}"
                )]
        
        # 3. 应用满减券（可叠加）
        fixed_discounts = []
        total_fixed_discount = Decimal('0')
        
        # 按门槛从低到高排序满减券
        fixed_coupons = [c for c in coupons if c.coupon_type == CouponType.FIXED_DISCOUNT]
        fixed_coupons.sort(key=lambda x: x.threshold or Decimal('0'))
        
        # 计算经过会员/折扣券处理后的金额
        processed_amount = discountable_amount - member_discount - coupon_discount
        
        for coupon in fixed_coupons:
            if (coupon.threshold is not None and 
                coupon.discount_amount is not None and
                processed_amount >= coupon.threshold):
                
                fixed_discounts.append(DiscountDetail(
                    type="fixed_discount",
                    name=coupon.name,
                    amount=coupon.discount_amount,
                    description=f"满{coupon.threshold:.2f}减{coupon.discount_amount:.2f}，优惠金额：¥{coupon.discount_amount:.2f}"
                ))
                total_fixed_discount += coupon.discount_amount
                processed_amount -= coupon.discount_amount
        
        # 4. 计算最终金额
        total_discount = member_discount + coupon_discount + total_fixed_discount
        final_amount = subtotal - total_discount
        
        # 5. 更新商品项的折扣信息
        if discountable_amount > 0:
            discount_ratio = total_discount / discountable_amount
            for item in items:
                if item.product.eligible_for_discount:
                    item.discount_applied = item.subtotal * discount_ratio
        
        # 6. 合并所有优惠明细
        all_discount_details = discount_details + fixed_discounts
        
        return OrderCalculation(
            items=items,
            subtotal=subtotal,
            discountable_amount=discountable_amount,
            non_discountable_amount=non_discountable_amount,
            member_discount=member_discount,
            coupon_discount=coupon_discount,
            fixed_discounts=fixed_discounts,
            total_discount=total_discount,
            final_amount=final_amount,
            discount_details=all_discount_details
        )
    
    def format_order_summary(self, calculation: OrderCalculation) -> str:
        """格式化订单摘要"""
        summary = []
        summary.append("=" * 50)
        summary.append("订单明细")
        summary.append("=" * 50)
        
        # 商品明细
        for item in calculation.items:
            summary.append(f"商品：{item.product.name}")
            summary.append(f"  单价：¥{item.product.price:.2f} × {item.product.quantity}")
            summary.append(f"  小计：¥{item.subtotal:.2f}")
            if item.discount_applied > 0:
                summary.append(f"  优惠：-¥{item.discount_applied:.2f}")
            summary.append("")
        
        # 金额汇总
        summary.append("金额汇总：")
        summary.append(f"  商品总价：¥{calculation.subtotal:.2f}")
        summary.append(f"  可优惠金额：¥{calculation.discountable_amount:.2f}")
        summary.append(f"  不可优惠金额：¥{calculation.non_discountable_amount:.2f}")
        summary.append("")
        
        # 优惠明细
        if calculation.discount_details:
            summary.append("优惠明细：")
            for detail in calculation.discount_details:
                summary.append(f"  {detail.description}")
            summary.append("")
        
        summary.append(f"总优惠金额：¥{calculation.total_discount:.2f}")
        summary.append(f"最终实付金额：¥{calculation.final_amount:.2f}")
        summary.append("=" * 50)
        
        return "\n".join(summary)


# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    products = [
        Product("P001", "iPhone 15", Decimal("5999.00"), 1, True),
        Product("P002", "AirPods Pro", Decimal("1999.00"), 1, True),
        Product("P003", "手机壳", Decimal("99.00"), 2, False),  # 不参与优惠
    ]
    
    user = User("U001", "张三", True)  # 会员用户
    
    coupons = [
        Coupon("C001", "新用户满减券", CouponType.FIXED_DISCOUNT, 
               threshold=Decimal("200.00"), discount_amount=Decimal("30.00")),
        Coupon("C002", "满500减80券", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("500.00"), discount_amount=Decimal("80.00")),
        Coupon("C003", "9折优惠券", CouponType.PERCENTAGE_DISCOUNT,
               discount_rate=Decimal("0.90")),
    ]
    
    # 计算订单
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    # 输出结果
    print(calculator.format_order_summary(result))