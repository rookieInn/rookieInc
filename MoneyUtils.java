package com.example.util;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.text.NumberFormat;
import java.util.Currency;
import java.util.Locale;

/**
 * 金额处理工具类
 * 
 * 提供BigDecimal的常用操作，确保金额计算的精确性
 * 避免使用double/float进行金额计算导致的精度问题
 */
public class MoneyUtils {
    
    // 默认精度：2位小数
    public static final int DEFAULT_SCALE = 2;
    
    // 默认舍入模式：四舍五入
    public static final RoundingMode DEFAULT_ROUNDING_MODE = RoundingMode.HALF_UP;
    
    /**
     * 创建BigDecimal金额对象
     * 
     * @param value 金额值（字符串形式，避免精度丢失）
     * @return BigDecimal对象
     */
    public static BigDecimal createMoney(String value) {
        if (value == null || value.trim().isEmpty()) {
            return BigDecimal.ZERO;
        }
        return new BigDecimal(value.trim());
    }
    
    /**
     * 创建BigDecimal金额对象
     * 
     * @param value 金额值（double类型，不推荐用于生产环境）
     * @return BigDecimal对象
     */
    public static BigDecimal createMoney(double value) {
        return BigDecimal.valueOf(value);
    }
    
    /**
     * 创建BigDecimal金额对象
     * 
     * @param value 金额值（int类型）
     * @return BigDecimal对象
     */
    public static BigDecimal createMoney(int value) {
        return new BigDecimal(value);
    }
    
    /**
     * 金额相加
     * 
     * @param amount1 金额1
     * @param amount2 金额2
     * @return 相加结果
     */
    public static BigDecimal add(BigDecimal amount1, BigDecimal amount2) {
        if (amount1 == null) amount1 = BigDecimal.ZERO;
        if (amount2 == null) amount2 = BigDecimal.ZERO;
        return amount1.add(amount2);
    }
    
    /**
     * 金额相减
     * 
     * @param amount1 被减数
     * @param amount2 减数
     * @return 相减结果
     */
    public static BigDecimal subtract(BigDecimal amount1, BigDecimal amount2) {
        if (amount1 == null) amount1 = BigDecimal.ZERO;
        if (amount2 == null) amount2 = BigDecimal.ZERO;
        return amount1.subtract(amount2);
    }
    
    /**
     * 金额相乘
     * 
     * @param amount 金额
     * @param multiplier 乘数
     * @return 相乘结果
     */
    public static BigDecimal multiply(BigDecimal amount, BigDecimal multiplier) {
        if (amount == null) amount = BigDecimal.ZERO;
        if (multiplier == null) multiplier = BigDecimal.ZERO;
        return amount.multiply(multiplier);
    }
    
    /**
     * 金额相除
     * 
     * @param amount 被除数
     * @param divisor 除数
     * @return 相除结果
     */
    public static BigDecimal divide(BigDecimal amount, BigDecimal divisor) {
        if (amount == null) amount = BigDecimal.ZERO;
        if (divisor == null || divisor.compareTo(BigDecimal.ZERO) == 0) {
            throw new IllegalArgumentException("除数不能为零");
        }
        return amount.divide(divisor, DEFAULT_SCALE, DEFAULT_ROUNDING_MODE);
    }
    
    /**
     * 金额相除（指定精度）
     * 
     * @param amount 被除数
     * @param divisor 除数
     * @param scale 精度
     * @return 相除结果
     */
    public static BigDecimal divide(BigDecimal amount, BigDecimal divisor, int scale) {
        if (amount == null) amount = BigDecimal.ZERO;
        if (divisor == null || divisor.compareTo(BigDecimal.ZERO) == 0) {
            throw new IllegalArgumentException("除数不能为零");
        }
        return amount.divide(divisor, scale, DEFAULT_ROUNDING_MODE);
    }
    
    /**
     * 格式化金额显示
     * 
     * @param amount 金额
     * @return 格式化后的字符串
     */
    public static String formatMoney(BigDecimal amount) {
        if (amount == null) {
            return "0.00";
        }
        
        NumberFormat formatter = NumberFormat.getCurrencyInstance(Locale.CHINA);
        return formatter.format(amount);
    }
    
    /**
     * 格式化金额显示（指定格式）
     * 
     * @param amount 金额
     * @param pattern 格式模式
     * @return 格式化后的字符串
     */
    public static String formatMoney(BigDecimal amount, String pattern) {
        if (amount == null) {
            return "0.00";
        }
        
        DecimalFormat formatter = new DecimalFormat(pattern);
        return formatter.format(amount);
    }
    
    /**
     * 比较两个金额
     * 
     * @param amount1 金额1
     * @param amount2 金额2
     * @return 比较结果：-1(小于), 0(等于), 1(大于)
     */
    public static int compare(BigDecimal amount1, BigDecimal amount2) {
        if (amount1 == null) amount1 = BigDecimal.ZERO;
        if (amount2 == null) amount2 = BigDecimal.ZERO;
        return amount1.compareTo(amount2);
    }
    
    /**
     * 判断金额是否为零
     * 
     * @param amount 金额
     * @return 是否为零
     */
    public static boolean isZero(BigDecimal amount) {
        return amount == null || amount.compareTo(BigDecimal.ZERO) == 0;
    }
    
    /**
     * 判断金额是否为正数
     * 
     * @param amount 金额
     * @return 是否为正数
     */
    public static boolean isPositive(BigDecimal amount) {
        return amount != null && amount.compareTo(BigDecimal.ZERO) > 0;
    }
    
    /**
     * 判断金额是否为负数
     * 
     * @param amount 金额
     * @return 是否为负数
     */
    public static boolean isNegative(BigDecimal amount) {
        return amount != null && amount.compareTo(BigDecimal.ZERO) < 0;
    }
    
    /**
     * 计算折扣
     * 
     * @param originalPrice 原价
     * @param discountRate 折扣率（0.0-1.0）
     * @return 折扣后价格
     */
    public static BigDecimal calculateDiscount(BigDecimal originalPrice, BigDecimal discountRate) {
        if (originalPrice == null) originalPrice = BigDecimal.ZERO;
        if (discountRate == null) discountRate = BigDecimal.ZERO;
        
        if (discountRate.compareTo(BigDecimal.ZERO) < 0 || 
            discountRate.compareTo(BigDecimal.ONE) > 0) {
            throw new IllegalArgumentException("折扣率必须在0-1之间");
        }
        
        return multiply(originalPrice, discountRate);
    }
    
    /**
     * 计算税费
     * 
     * @param amount 金额
     * @param taxRate 税率（如0.13表示13%）
     * @return 税费
     */
    public static BigDecimal calculateTax(BigDecimal amount, BigDecimal taxRate) {
        if (amount == null) amount = BigDecimal.ZERO;
        if (taxRate == null) taxRate = BigDecimal.ZERO;
        
        return multiply(amount, taxRate);
    }
    
    /**
     * 四舍五入到指定精度
     * 
     * @param amount 金额
     * @param scale 精度
     * @return 四舍五入后的金额
     */
    public static BigDecimal round(BigDecimal amount, int scale) {
        if (amount == null) return BigDecimal.ZERO;
        return amount.setScale(scale, DEFAULT_ROUNDING_MODE);
    }
    
    /**
     * 获取金额的绝对值
     * 
     * @param amount 金额
     * @return 绝对值
     */
    public static BigDecimal abs(BigDecimal amount) {
        if (amount == null) return BigDecimal.ZERO;
        return amount.abs();
    }
}