"""
电商订单金额计算系统测试用例

测试各种优惠规则组合的正确性
"""

import unittest
from decimal import Decimal
from order_calculator import (
    OrderCalculator, Product, User, Coupon, CouponType,
    OrderCalculation, DiscountDetail
)


class TestOrderCalculator(unittest.TestCase):
    """订单计算器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = OrderCalculator()
        
        # 测试商品
        self.products = [
            Product("P001", "iPhone 15", Decimal("5999.00"), 1, True),
            Product("P002", "AirPods Pro", Decimal("1999.00"), 1, True),
            Product("P003", "手机壳", Decimal("99.00"), 2, False),  # 不参与优惠
        ]
        
        # 测试用户
        self.member_user = User("U001", "会员用户", True)
        self.non_member_user = User("U002", "非会员用户", False)
        
        # 测试优惠券
        self.fixed_coupons = [
            Coupon("C001", "满200减30", CouponType.FIXED_DISCOUNT,
                   threshold=Decimal("200.00"), discount_amount=Decimal("30.00")),
            Coupon("C002", "满500减80", CouponType.FIXED_DISCOUNT,
                   threshold=Decimal("500.00"), discount_amount=Decimal("80.00")),
            Coupon("C003", "满1000减200", CouponType.FIXED_DISCOUNT,
                   threshold=Decimal("1000.00"), discount_amount=Decimal("200.00")),
        ]
        
        self.percentage_coupons = [
            Coupon("C004", "9折券", CouponType.PERCENTAGE_DISCOUNT,
                   discount_rate=Decimal("0.90")),
            Coupon("C005", "8.5折券", CouponType.PERCENTAGE_DISCOUNT,
                   discount_rate=Decimal("0.85")),
        ]
    
    def test_basic_calculation_no_discounts(self):
        """测试基础计算，无优惠"""
        result = self.calculator.calculate_order(
            self.products, self.non_member_user, []
        )
        
        # 验证基础金额
        self.assertEqual(result.subtotal, Decimal("8196.00"))  # 5999 + 1999 + 198
        self.assertEqual(result.discountable_amount, Decimal("7998.00"))  # 5999 + 1999
        self.assertEqual(result.non_discountable_amount, Decimal("198.00"))  # 99 * 2
        self.assertEqual(result.total_discount, Decimal("0.00"))
        self.assertEqual(result.final_amount, Decimal("8196.00"))
    
    def test_member_discount_only(self):
        """测试仅会员折扣"""
        result = self.calculator.calculate_order(
            self.products, self.member_user, []
        )
        
        # 验证会员折扣
        expected_member_discount = Decimal("7998.00") * Decimal("0.05")  # 5%折扣
        self.assertEqual(result.member_discount, expected_member_discount)
        self.assertEqual(result.coupon_discount, Decimal("0.00"))
        self.assertEqual(len(result.fixed_discounts), 0)
        self.assertEqual(result.total_discount, expected_member_discount)
    
    def test_percentage_coupon_only(self):
        """测试仅折扣券"""
        result = self.calculator.calculate_order(
            self.products, self.non_member_user, [self.percentage_coupons[0]]  # 9折券
        )
        
        # 验证折扣券
        expected_coupon_discount = Decimal("7998.00") * Decimal("0.10")  # 10%折扣
        self.assertEqual(result.member_discount, Decimal("0.00"))
        self.assertEqual(result.coupon_discount, expected_coupon_discount)
        self.assertEqual(len(result.fixed_discounts), 0)
        self.assertEqual(result.total_discount, expected_coupon_discount)
    
    def test_member_vs_coupon_discount(self):
        """测试会员折扣与折扣券互斥，选择优惠力度大的"""
        # 会员折扣：5%，折扣券：10%
        result = self.calculator.calculate_order(
            self.products, self.member_user, [self.percentage_coupons[0]]  # 9折券
        )
        
        # 应该选择折扣券（10% > 5%）
        expected_coupon_discount = Decimal("7998.00") * Decimal("0.10")
        self.assertEqual(result.member_discount, Decimal("0.00"))
        self.assertEqual(result.coupon_discount, expected_coupon_discount)
        
        # 会员折扣：5%，折扣券：15%
        result2 = self.calculator.calculate_order(
            self.products, self.member_user, [self.percentage_coupons[1]]  # 8.5折券
        )
        
        # 应该选择折扣券（15% > 5%）
        expected_coupon_discount2 = Decimal("7998.00") * Decimal("0.15")
        self.assertEqual(result2.member_discount, Decimal("0.00"))
        self.assertEqual(result2.coupon_discount, expected_coupon_discount2)
    
    def test_fixed_discounts_stackable(self):
        """测试满减券可叠加"""
        result = self.calculator.calculate_order(
            self.products, self.non_member_user, self.fixed_coupons
        )
        
        # 验证满减券叠加
        # 可优惠金额：7998，满足所有满减券条件
        # 满200减30 + 满500减80 + 满1000减200 = 310
        expected_fixed_discount = Decimal("30.00") + Decimal("80.00") + Decimal("200.00")
        self.assertEqual(len(result.fixed_discounts), 3)
        self.assertEqual(result.total_discount, expected_fixed_discount)
    
    def test_fixed_discounts_threshold_order(self):
        """测试满减券按门槛从低到高判断"""
        # 创建不满足所有条件的商品
        small_products = [
            Product("P001", "小商品", Decimal("300.00"), 1, True),  # 总价300
        ]
        
        result = self.calculator.calculate_order(
            small_products, self.non_member_user, self.fixed_coupons
        )
        
        # 只应该满足满200减30的条件
        self.assertEqual(len(result.fixed_discounts), 1)
        self.assertEqual(result.fixed_discounts[0].amount, Decimal("30.00"))
        self.assertEqual(result.total_discount, Decimal("30.00"))
    
    def test_complex_scenario(self):
        """测试复杂场景：会员+满减券"""
        result = self.calculator.calculate_order(
            self.products, self.member_user, self.fixed_coupons
        )
        
        # 验证会员折扣
        expected_member_discount = Decimal("7998.00") * Decimal("0.05")
        self.assertEqual(result.member_discount, expected_member_discount)
        
        # 验证满减券（在会员折扣后的金额上应用）
        processed_amount = Decimal("7998.00") - expected_member_discount
        # 应该满足所有满减券条件
        expected_fixed_discount = Decimal("30.00") + Decimal("80.00") + Decimal("200.00")
        self.assertEqual(len(result.fixed_discounts), 3)
        
        # 验证总优惠
        expected_total_discount = expected_member_discount + expected_fixed_discount
        self.assertEqual(result.total_discount, expected_total_discount)
    
    def test_discount_coupon_vs_member_with_fixed(self):
        """测试折扣券与会员折扣互斥，同时有满减券"""
        result = self.calculator.calculate_order(
            self.products, self.member_user, 
            [self.percentage_coupons[0]] + self.fixed_coupons  # 9折券 + 满减券
        )
        
        # 应该选择折扣券而不是会员折扣
        expected_coupon_discount = Decimal("7998.00") * Decimal("0.10")
        self.assertEqual(result.member_discount, Decimal("0.00"))
        self.assertEqual(result.coupon_discount, expected_coupon_discount)
        
        # 满减券仍然应该应用
        self.assertEqual(len(result.fixed_discounts), 3)
    
    def test_non_discountable_products(self):
        """测试不参与优惠的商品不受影响"""
        result = self.calculator.calculate_order(
            self.products, self.member_user, self.fixed_coupons
        )
        
        # 不可优惠金额应该保持不变
        self.assertEqual(result.non_discountable_amount, Decimal("198.00"))
        
        # 最终金额应该包含不可优惠金额
        expected_final = (result.subtotal - result.total_discount)
        self.assertEqual(result.final_amount, expected_final)
    
    def test_edge_case_zero_amount(self):
        """测试边界情况：金额为0"""
        empty_products = []
        result = self.calculator.calculate_order(
            empty_products, self.member_user, self.fixed_coupons
        )
        
        self.assertEqual(result.subtotal, Decimal("0.00"))
        self.assertEqual(result.final_amount, Decimal("0.00"))
        self.assertEqual(result.total_discount, Decimal("0.00"))
    
    def test_edge_case_insufficient_amount(self):
        """测试边界情况：金额不足满足任何满减券"""
        small_products = [
            Product("P001", "小商品", Decimal("50.00"), 1, True),  # 总价50
        ]
        
        result = self.calculator.calculate_order(
            small_products, self.non_member_user, self.fixed_coupons
        )
        
        # 不应该有任何满减券
        self.assertEqual(len(result.fixed_discounts), 0)
        self.assertEqual(result.total_discount, Decimal("0.00"))


def run_performance_test():
    """性能测试"""
    import time
    
    calculator = OrderCalculator()
    
    # 创建大量商品
    products = []
    for i in range(1000):
        products.append(Product(f"P{i:04d}", f"商品{i}", Decimal("100.00"), 1, True))
    
    user = User("U001", "测试用户", True)
    coupons = [
        Coupon("C001", "满100减10", CouponType.FIXED_DISCOUNT,
               threshold=Decimal("100.00"), discount_amount=Decimal("10.00")),
    ]
    
    start_time = time.time()
    result = calculator.calculate_order(products, user, coupons)
    end_time = time.time()
    
    print(f"性能测试：1000个商品计算耗时 {end_time - start_time:.4f} 秒")
    print(f"最终金额：¥{result.final_amount:.2f}")


if __name__ == "__main__":
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*50)
    print("运行性能测试...")
    run_performance_test()