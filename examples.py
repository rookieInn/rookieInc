"""
电商订单金额计算系统 - 使用示例

展示各种优惠规则组合的实际应用场景
"""

from decimal import Decimal
from order_calculator import (
    OrderCalculator, Product, User, Coupon, CouponType
)


def example_1_basic_member_discount():
    """示例1：基础会员折扣"""
    print("=" * 60)
    print("示例1：基础会员折扣")
    print("=" * 60)
    
    # 商品
    products = [
        Product("P001", "MacBook Pro", Decimal("12999.00"), 1, True),
        Product("P002", "Magic Mouse", Decimal("599.00"), 1, True),
        Product("P003", "贴膜", Decimal("29.00"), 1, False),  # 不参与优惠
    ]
    
    # 会员用户
    user = User("U001", "VIP会员", True)
    
    # 无优惠券
    coupons = []
    
    # 计算
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


def example_2_coupon_vs_member():
    """示例2：折扣券与会员折扣互斥"""
    print("=" * 60)
    print("示例2：折扣券与会员折扣互斥（选择优惠力度大的）")
    print("=" * 60)
    
    products = [
        Product("P001", "iPhone 15 Pro", Decimal("7999.00"), 1, True),
        Product("P002", "AirPods Pro", Decimal("1999.00"), 1, True),
    ]
    
    # 会员用户
    user = User("U001", "VIP会员", True)
    
    # 9折券（比会员9.5折更优惠）
    coupons = [
        Coupon("C001", "新用户9折券", CouponType.PERCENTAGE_DISCOUNT,
               discount_rate=Decimal("0.90")),
    ]
    
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


def example_3_fixed_discounts_stackable():
    """示例3：满减券可叠加"""
    print("=" * 60)
    print("示例3：满减券可叠加使用")
    print("=" * 60)
    
    products = [
        Product("P001", "游戏本", Decimal("8999.00"), 1, True),
        Product("P002", "机械键盘", Decimal("599.00"), 1, True),
        Product("P003", "鼠标垫", Decimal("39.00"), 1, False),
    ]
    
    user = User("U001", "普通用户", False)
    
    # 多个满减券
    coupons = [
        Coupon("C001", "满500减50", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("500.00"), discount_amount=Decimal("50.00")),
        Coupon("C002", "满1000减150", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("1000.00"), discount_amount=Decimal("150.00")),
        Coupon("C003", "满5000减500", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("5000.00"), discount_amount=Decimal("500.00")),
    ]
    
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


def example_4_complex_scenario():
    """示例4：复杂场景 - 会员+满减券"""
    print("=" * 60)
    print("示例4：复杂场景 - 会员折扣 + 满减券")
    print("=" * 60)
    
    products = [
        Product("P001", "高端相机", Decimal("15999.00"), 1, True),
        Product("P002", "镜头", Decimal("5999.00"), 1, True),
        Product("P003", "存储卡", Decimal("299.00"), 1, False),
        Product("P004", "相机包", Decimal("199.00"), 1, False),
    ]
    
    # 会员用户
    user = User("U001", "摄影爱好者", True)
    
    # 满减券
    coupons = [
        Coupon("C001", "满1000减100", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("1000.00"), discount_amount=Decimal("100.00")),
        Coupon("C002", "满5000减600", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("5000.00"), discount_amount=Decimal("600.00")),
        Coupon("C003", "满10000减1200", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("10000.00"), discount_amount=Decimal("1200.00")),
    ]
    
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


def example_5_discount_coupon_with_fixed():
    """示例5：折扣券 + 满减券"""
    print("=" * 60)
    print("示例5：折扣券 + 满减券组合")
    print("=" * 60)
    
    products = [
        Product("P001", "平板电脑", Decimal("3999.00"), 1, True),
        Product("P002", "触控笔", Decimal("599.00"), 1, True),
        Product("P003", "保护套", Decimal("99.00"), 1, False),
    ]
    
    user = User("U001", "普通用户", False)
    
    # 折扣券 + 满减券
    coupons = [
        Coupon("C001", "8.5折券", CouponType.PERCENTAGE_DISCOUNT,
               discount_rate=Decimal("0.85")),
        Coupon("C002", "满2000减200", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("2000.00"), discount_amount=Decimal("200.00")),
        Coupon("C003", "满3000减400", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("3000.00"), discount_amount=Decimal("400.00")),
    ]
    
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


def example_6_edge_cases():
    """示例6：边界情况测试"""
    print("=" * 60)
    print("示例6：边界情况测试")
    print("=" * 60)
    
    # 情况1：金额不足满足满减券
    print("情况1：金额不足满足满减券")
    products1 = [
        Product("P001", "小商品", Decimal("100.00"), 1, True),
    ]
    
    user = User("U001", "普通用户", False)
    coupons = [
        Coupon("C001", "满500减50", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("500.00"), discount_amount=Decimal("50.00")),
    ]
    
    calculator = OrderCalculator()
    result1 = calculator.calculate_order(products1, user, coupons)
    print(calculator.format_order_summary(result1))
    print()
    
    # 情况2：只有不参与优惠的商品
    print("情况2：只有不参与优惠的商品")
    products2 = [
        Product("P001", "服务费", Decimal("50.00"), 1, False),
        Product("P002", "手续费", Decimal("20.00"), 1, False),
    ]
    
    result2 = calculator.calculate_order(products2, user, coupons)
    print(calculator.format_order_summary(result2))
    print()


def example_7_business_scenarios():
    """示例7：实际业务场景"""
    print("=" * 60)
    print("示例7：实际业务场景 - 双11购物车")
    print("=" * 60)
    
    # 双11购物车
    products = [
        Product("P001", "iPhone 15 Pro Max", Decimal("9999.00"), 1, True),
        Product("P002", "AirPods Pro 2", Decimal("1999.00"), 1, True),
        Product("P003", "MagSafe充电器", Decimal("329.00"), 1, True),
        Product("P004", "手机壳", Decimal("99.00"), 2, False),  # 不参与优惠
        Product("P005", "贴膜", Decimal("29.00"), 3, False),   # 不参与优惠
    ]
    
    # VIP会员
    user = User("U001", "VIP会员", True)
    
    # 双11优惠券
    coupons = [
        Coupon("C001", "双11满减券-满2000减200", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("2000.00"), discount_amount=Decimal("200.00")),
        Coupon("C002", "双11满减券-满5000减600", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("5000.00"), discount_amount=Decimal("600.00")),
        Coupon("C003", "双11满减券-满10000减1500", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("10000.00"), discount_amount=Decimal("1500.00")),
        Coupon("C004", "双11限时8折券", CouponType.PERCENTAGE_DISCOUNT,
               discount_rate=Decimal("0.80")),
    ]
    
    calculator = OrderCalculator()
    result = calculator.calculate_order(products, user, coupons)
    
    print(calculator.format_order_summary(result))
    print()


if __name__ == "__main__":
    print("电商订单金额计算系统 - 使用示例")
    print("=" * 60)
    print()
    
    # 运行所有示例
    example_1_basic_member_discount()
    example_2_coupon_vs_member()
    example_3_fixed_discounts_stackable()
    example_4_complex_scenario()
    example_5_discount_coupon_with_fixed()
    example_6_edge_cases()
    example_7_business_scenarios()
    
    print("=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)