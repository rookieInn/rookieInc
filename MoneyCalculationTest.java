package com.example.test;

import com.example.util.MoneyUtils;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

import java.math.BigDecimal;

/**
 * 金额计算测试类
 * 
 * 验证BigDecimal金额计算的正确性
 * 对比double和BigDecimal的精度差异
 */
public class MoneyCalculationTest {
    
    @Test
    @DisplayName("测试基本金额运算")
    public void testBasicMoneyOperations() {
        // 测试金额相加
        BigDecimal price1 = MoneyUtils.createMoney("99.99");
        BigDecimal price2 = MoneyUtils.createMoney("199.50");
        BigDecimal total = MoneyUtils.add(price1, price2);
        
        assertEquals(new BigDecimal("299.49"), total);
        assertEquals(0, total.compareTo(new BigDecimal("299.49")));
        
        // 测试金额相减
        BigDecimal difference = MoneyUtils.subtract(price2, price1);
        assertEquals(new BigDecimal("99.51"), difference);
        
        // 测试金额相乘
        BigDecimal taxRate = new BigDecimal("0.13");
        BigDecimal tax = MoneyUtils.multiply(total, taxRate);
        assertEquals(new BigDecimal("38.9337"), tax);
    }
    
    @Test
    @DisplayName("测试精度问题对比")
    public void testPrecisionComparison() {
        // 使用double计算（会有精度问题）
        double doublePrice1 = 0.1;
        double doublePrice2 = 0.2;
        double doubleResult = doublePrice1 + doublePrice2;
        
        // 使用BigDecimal计算（精确）
        BigDecimal bigDecimalPrice1 = new BigDecimal("0.1");
        BigDecimal bigDecimalPrice2 = new BigDecimal("0.2");
        BigDecimal bigDecimalResult = bigDecimalPrice1.add(bigDecimalPrice2);
        
        // 验证double的精度问题
        assertNotEquals(0.3, doubleResult, 0.0001);
        
        // 验证BigDecimal的精确性
        assertEquals(0, bigDecimalResult.compareTo(new BigDecimal("0.3")));
        assertTrue(bigDecimalResult.equals(new BigDecimal("0.3")));
    }
    
    @Test
    @DisplayName("测试金额比较")
    public void testMoneyComparison() {
        BigDecimal amount1 = MoneyUtils.createMoney("100.00");
        BigDecimal amount2 = MoneyUtils.createMoney("99.99");
        BigDecimal amount3 = MoneyUtils.createMoney("100.00");
        
        // 测试大于比较
        assertTrue(MoneyUtils.compare(amount1, amount2) > 0);
        assertTrue(amount1.compareTo(amount2) > 0);
        
        // 测试小于比较
        assertTrue(MoneyUtils.compare(amount2, amount1) < 0);
        assertTrue(amount2.compareTo(amount1) < 0);
        
        // 测试等于比较
        assertEquals(0, MoneyUtils.compare(amount1, amount3));
        assertEquals(0, amount1.compareTo(amount3));
        assertTrue(amount1.equals(amount3));
    }
    
    @Test
    @DisplayName("测试金额格式化")
    public void testMoneyFormatting() {
        BigDecimal amount = MoneyUtils.createMoney("1234.56");
        
        // 测试基本格式化
        String formatted = MoneyUtils.formatMoney(amount);
        assertNotNull(formatted);
        assertTrue(formatted.contains("1234.56"));
        
        // 测试自定义格式化
        String customFormatted = MoneyUtils.formatMoney(amount, "#,##0.00");
        assertEquals("1,234.56", customFormatted);
    }
    
    @Test
    @DisplayName("测试折扣计算")
    public void testDiscountCalculation() {
        BigDecimal originalPrice = MoneyUtils.createMoney("1000.00");
        BigDecimal discountRate = new BigDecimal("0.8"); // 8折
        
        BigDecimal discountPrice = MoneyUtils.calculateDiscount(originalPrice, discountRate);
        assertEquals(new BigDecimal("800.00"), discountPrice);
        
        // 测试5折
        BigDecimal halfDiscount = MoneyUtils.calculateDiscount(originalPrice, new BigDecimal("0.5"));
        assertEquals(new BigDecimal("500.00"), halfDiscount);
    }
    
    @Test
    @DisplayName("测试税费计算")
    public void testTaxCalculation() {
        BigDecimal amount = MoneyUtils.createMoney("1000.00");
        BigDecimal taxRate = new BigDecimal("0.13"); // 13%税率
        
        BigDecimal tax = MoneyUtils.calculateTax(amount, taxRate);
        assertEquals(new BigDecimal("130.00"), tax);
    }
    
    @Test
    @DisplayName("测试金额除法")
    public void testMoneyDivision() {
        BigDecimal amount = MoneyUtils.createMoney("100.00");
        BigDecimal divisor = new BigDecimal("3");
        
        BigDecimal result = MoneyUtils.divide(amount, divisor);
        assertEquals(new BigDecimal("33.33"), result);
        
        // 测试指定精度的除法
        BigDecimal preciseResult = MoneyUtils.divide(amount, divisor, 4);
        assertEquals(new BigDecimal("33.3333"), preciseResult);
    }
    
    @Test
    @DisplayName("测试零值处理")
    public void testZeroValueHandling() {
        // 测试空值处理
        assertTrue(MoneyUtils.isZero(null));
        assertTrue(MoneyUtils.isZero(BigDecimal.ZERO));
        assertFalse(MoneyUtils.isZero(MoneyUtils.createMoney("0.01")));
        
        // 测试正负数判断
        assertTrue(MoneyUtils.isPositive(MoneyUtils.createMoney("100.00")));
        assertFalse(MoneyUtils.isPositive(MoneyUtils.createMoney("-100.00")));
        assertFalse(MoneyUtils.isPositive(BigDecimal.ZERO));
        
        assertTrue(MoneyUtils.isNegative(MoneyUtils.createMoney("-100.00")));
        assertFalse(MoneyUtils.isNegative(MoneyUtils.createMoney("100.00")));
        assertFalse(MoneyUtils.isNegative(BigDecimal.ZERO));
    }
    
    @Test
    @DisplayName("测试四舍五入")
    public void testRounding() {
        BigDecimal amount = new BigDecimal("123.456789");
        
        // 测试四舍五入到2位小数
        BigDecimal rounded = MoneyUtils.round(amount, 2);
        assertEquals(new BigDecimal("123.46"), rounded);
        
        // 测试四舍五入到4位小数
        BigDecimal rounded4 = MoneyUtils.round(amount, 4);
        assertEquals(new BigDecimal("123.4568"), rounded4);
    }
    
    @Test
    @DisplayName("测试绝对值")
    public void testAbsoluteValue() {
        BigDecimal positive = MoneyUtils.createMoney("100.00");
        BigDecimal negative = MoneyUtils.createMoney("-100.00");
        
        assertEquals(positive, MoneyUtils.abs(positive));
        assertEquals(positive, MoneyUtils.abs(negative));
    }
    
    @Test
    @DisplayName("测试异常情况")
    public void testExceptionCases() {
        // 测试除零异常
        BigDecimal amount = MoneyUtils.createMoney("100.00");
        BigDecimal zero = BigDecimal.ZERO;
        
        assertThrows(IllegalArgumentException.class, () -> {
            MoneyUtils.divide(amount, zero);
        });
        
        // 测试无效折扣率
        assertThrows(IllegalArgumentException.class, () -> {
            MoneyUtils.calculateDiscount(amount, new BigDecimal("1.5")); // 150%折扣
        });
        
        assertThrows(IllegalArgumentException.class, () -> {
            MoneyUtils.calculateDiscount(amount, new BigDecimal("-0.1")); // -10%折扣
        });
    }
    
    @Test
    @DisplayName("测试复杂业务场景")
    public void testComplexBusinessScenario() {
        // 模拟订单计算
        BigDecimal item1Price = MoneyUtils.createMoney("99.99");
        BigDecimal item2Price = MoneyUtils.createMoney("199.50");
        int quantity1 = 2;
        int quantity2 = 1;
        
        // 计算小计
        BigDecimal subtotal1 = MoneyUtils.multiply(item1Price, new BigDecimal(quantity1));
        BigDecimal subtotal2 = MoneyUtils.multiply(item2Price, new BigDecimal(quantity2));
        BigDecimal totalSubtotal = MoneyUtils.add(subtotal1, subtotal2);
        
        assertEquals(new BigDecimal("399.48"), totalSubtotal);
        
        // 计算折扣（满300减50）
        BigDecimal discount = BigDecimal.ZERO;
        if (MoneyUtils.compare(totalSubtotal, new BigDecimal("300.00")) >= 0) {
            discount = new BigDecimal("50.00");
        }
        assertEquals(new BigDecimal("50.00"), discount);
        
        // 计算税费
        BigDecimal taxableAmount = MoneyUtils.subtract(totalSubtotal, discount);
        BigDecimal taxRate = new BigDecimal("0.13");
        BigDecimal tax = MoneyUtils.multiply(taxableAmount, taxRate);
        assertEquals(new BigDecimal("45.4324"), tax);
        
        // 计算最终金额
        BigDecimal finalAmount = MoneyUtils.add(taxableAmount, tax);
        assertEquals(new BigDecimal("394.9124"), finalAmount);
        
        // 四舍五入到2位小数
        BigDecimal finalAmountRounded = MoneyUtils.round(finalAmount, 2);
        assertEquals(new BigDecimal("394.91"), finalAmountRounded);
    }
}