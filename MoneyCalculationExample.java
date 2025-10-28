package com.example.demo;

import com.example.model.Product;
import com.example.util.MoneyUtils;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 金额计算示例类
 * 
 * 演示如何正确使用BigDecimal进行金额计算
 * 避免使用double/float导致的精度问题
 */
public class MoneyCalculationExample {
    
    public static void main(String[] args) {
        System.out.println("=== BigDecimal金额计算示例 ===\n");
        
        // 1. 基本金额操作示例
        basicMoneyOperations();
        
        // 2. 产品价格计算示例
        productPriceCalculation();
        
        // 3. 订单金额计算示例
        orderCalculation();
        
        // 4. 精度问题对比示例
        precisionComparison();
        
        // 5. 实际业务场景示例
        businessScenarioExample();
    }
    
    /**
     * 基本金额操作示例
     */
    private static void basicMoneyOperations() {
        System.out.println("1. 基本金额操作示例:");
        
        // 创建金额对象
        BigDecimal price1 = MoneyUtils.createMoney("99.99");
        BigDecimal price2 = MoneyUtils.createMoney("199.50");
        
        // 金额相加
        BigDecimal total = MoneyUtils.add(price1, price2);
        System.out.println("价格1: " + MoneyUtils.formatMoney(price1));
        System.out.println("价格2: " + MoneyUtils.formatMoney(price2));
        System.out.println("总计: " + MoneyUtils.formatMoney(total));
        
        // 金额相减
        BigDecimal difference = MoneyUtils.subtract(price2, price1);
        System.out.println("差价: " + MoneyUtils.formatMoney(difference));
        
        // 金额相乘（计算税费）
        BigDecimal taxRate = new BigDecimal("0.13"); // 13%税率
        BigDecimal tax = MoneyUtils.multiply(total, taxRate);
        System.out.println("税费(13%): " + MoneyUtils.formatMoney(tax));
        
        System.out.println();
    }
    
    /**
     * 产品价格计算示例
     */
    private static void productPriceCalculation() {
        System.out.println("2. 产品价格计算示例:");
        
        // 创建产品
        Product laptop = new Product("MacBook Pro", "19999.00", "高性能笔记本电脑");
        Product mouse = new Product("Magic Mouse", "599.00", "无线鼠标");
        
        // 计算折扣价格（8折）
        BigDecimal discountRate = new BigDecimal("0.8");
        BigDecimal laptopDiscountPrice = MoneyUtils.calculateDiscount(laptop.getPrice(), discountRate);
        BigDecimal mouseDiscountPrice = MoneyUtils.calculateDiscount(mouse.getPrice(), discountRate);
        
        System.out.println("原价 - " + laptop.getName() + ": " + MoneyUtils.formatMoney(laptop.getPrice()));
        System.out.println("折扣价(8折) - " + laptop.getName() + ": " + MoneyUtils.formatMoney(laptopDiscountPrice));
        System.out.println("原价 - " + mouse.getName() + ": " + MoneyUtils.formatMoney(mouse.getPrice()));
        System.out.println("折扣价(8折) - " + mouse.getName() + ": " + MoneyUtils.formatMoney(mouseDiscountPrice));
        
        // 计算总价
        BigDecimal totalOriginal = MoneyUtils.add(laptop.getPrice(), mouse.getPrice());
        BigDecimal totalDiscount = MoneyUtils.add(laptopDiscountPrice, mouseDiscountPrice);
        BigDecimal totalSavings = MoneyUtils.subtract(totalOriginal, totalDiscount);
        
        System.out.println("原价总计: " + MoneyUtils.formatMoney(totalOriginal));
        System.out.println("折扣价总计: " + MoneyUtils.formatMoney(totalDiscount));
        System.out.println("节省金额: " + MoneyUtils.formatMoney(totalSavings));
        
        System.out.println();
    }
    
    /**
     * 订单金额计算示例
     */
    private static void orderCalculation() {
        System.out.println("3. 订单金额计算示例:");
        
        // 模拟订单项
        List<OrderItem> orderItems = new ArrayList<>();
        orderItems.add(new OrderItem("iPhone 15 Pro", 1, new BigDecimal("7999.00")));
        orderItems.add(new OrderItem("AirPods Pro", 2, new BigDecimal("1999.00")));
        orderItems.add(new OrderItem("保护壳", 1, new BigDecimal("299.00")));
        
        // 计算订单总金额
        BigDecimal subtotal = BigDecimal.ZERO;
        for (OrderItem item : orderItems) {
            BigDecimal itemTotal = MoneyUtils.multiply(item.getUnitPrice(), new BigDecimal(item.getQuantity()));
            subtotal = MoneyUtils.add(subtotal, itemTotal);
            System.out.println(item.getName() + " x" + item.getQuantity() + 
                             " = " + MoneyUtils.formatMoney(itemTotal));
        }
        
        // 计算折扣（满10000减500）
        BigDecimal discount = BigDecimal.ZERO;
        if (MoneyUtils.compare(subtotal, new BigDecimal("10000")) >= 0) {
            discount = new BigDecimal("500.00");
        }
        
        // 计算税费
        BigDecimal taxableAmount = MoneyUtils.subtract(subtotal, discount);
        BigDecimal taxRate = new BigDecimal("0.13");
        BigDecimal tax = MoneyUtils.multiply(taxableAmount, taxRate);
        
        // 计算运费
        BigDecimal shippingFee = new BigDecimal("50.00");
        
        // 计算最终金额
        BigDecimal finalAmount = MoneyUtils.add(MoneyUtils.add(taxableAmount, tax), shippingFee);
        
        System.out.println("\n订单明细:");
        System.out.println("商品小计: " + MoneyUtils.formatMoney(subtotal));
        System.out.println("优惠金额: " + MoneyUtils.formatMoney(discount));
        System.out.println("税费(13%): " + MoneyUtils.formatMoney(tax));
        System.out.println("运费: " + MoneyUtils.formatMoney(shippingFee));
        System.out.println("最终金额: " + MoneyUtils.formatMoney(finalAmount));
        
        System.out.println();
    }
    
    /**
     * 精度问题对比示例
     */
    private static void precisionComparison() {
        System.out.println("4. 精度问题对比示例:");
        
        // 使用double计算（不推荐）
        double doublePrice1 = 0.1;
        double doublePrice2 = 0.2;
        double doubleResult = doublePrice1 + doublePrice2;
        
        // 使用BigDecimal计算（推荐）
        BigDecimal bigDecimalPrice1 = new BigDecimal("0.1");
        BigDecimal bigDecimalPrice2 = new BigDecimal("0.2");
        BigDecimal bigDecimalResult = bigDecimalPrice1.add(bigDecimalPrice2);
        
        System.out.println("double计算: 0.1 + 0.2 = " + doubleResult);
        System.out.println("BigDecimal计算: 0.1 + 0.2 = " + bigDecimalResult);
        System.out.println("double结果是否等于0.3: " + (doubleResult == 0.3));
        System.out.println("BigDecimal结果是否等于0.3: " + (bigDecimalResult.compareTo(new BigDecimal("0.3")) == 0));
        
        System.out.println();
    }
    
    /**
     * 实际业务场景示例
     */
    private static void businessScenarioExample() {
        System.out.println("5. 实际业务场景示例:");
        
        // 用户余额操作
        BigDecimal userBalance = MoneyUtils.createMoney("1000.00");
        BigDecimal purchaseAmount = MoneyUtils.createMoney("299.99");
        
        System.out.println("用户余额: " + MoneyUtils.formatMoney(userBalance));
        System.out.println("购买金额: " + MoneyUtils.formatMoney(purchaseAmount));
        
        if (MoneyUtils.compare(userBalance, purchaseAmount) >= 0) {
            BigDecimal newBalance = MoneyUtils.subtract(userBalance, purchaseAmount);
            System.out.println("购买成功！");
            System.out.println("剩余余额: " + MoneyUtils.formatMoney(newBalance));
        } else {
            System.out.println("余额不足，购买失败！");
        }
        
        // 批量商品价格计算
        System.out.println("\n批量商品价格计算:");
        String[] productPrices = {"99.99", "199.50", "299.00", "599.99"};
        BigDecimal totalPrice = BigDecimal.ZERO;
        
        for (String priceStr : productPrices) {
            BigDecimal price = MoneyUtils.createMoney(priceStr);
            totalPrice = MoneyUtils.add(totalPrice, price);
            System.out.println("商品价格: " + MoneyUtils.formatMoney(price));
        }
        
        System.out.println("所有商品总价: " + MoneyUtils.formatMoney(totalPrice));
        
        // 计算平均价格
        BigDecimal averagePrice = MoneyUtils.divide(totalPrice, new BigDecimal(productPrices.length));
        System.out.println("平均价格: " + MoneyUtils.formatMoney(averagePrice));
    }
    
    /**
     * 订单项内部类
     */
    static class OrderItem {
        private String name;
        private int quantity;
        private BigDecimal unitPrice;
        
        public OrderItem(String name, int quantity, BigDecimal unitPrice) {
            this.name = name;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }
        
        public String getName() { return name; }
        public int getQuantity() { return quantity; }
        public BigDecimal getUnitPrice() { return unitPrice; }
    }
}