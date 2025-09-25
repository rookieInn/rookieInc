package com.example.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 产品实体类 - 演示如何正确使用BigDecimal处理金额
 * 
 * 重要说明：
 * 1. 金额字段必须使用BigDecimal类型，不能使用double或float
 * 2. BigDecimal提供精确的十进制运算，避免浮点数精度问题
 * 3. 数据库字段类型应使用DECIMAL，而不是FLOAT或DOUBLE
 */
public class Product {
    
    private Long id;
    private String name;
    private BigDecimal price;  // 使用BigDecimal而不是double
    private String description;
    private LocalDateTime createdAt;
    
    // 默认构造函数
    public Product() {
        this.createdAt = LocalDateTime.now();
    }
    
    // 带参数的构造函数
    public Product(String name, BigDecimal price, String description) {
        this.name = name;
        this.price = price;
        this.description = description;
        this.createdAt = LocalDateTime.now();
    }
    
    // 便捷构造函数，接受String类型的价格
    public Product(String name, String priceStr, String description) {
        this.name = name;
        this.price = new BigDecimal(priceStr);
        this.description = description;
        this.createdAt = LocalDateTime.now();
    }
    
    // Getter和Setter方法
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public BigDecimal getPrice() {
        return price;
    }
    
    public void setPrice(BigDecimal price) {
        this.price = price;
    }
    
    // 便捷方法：设置价格（String类型）
    public void setPrice(String priceStr) {
        this.price = new BigDecimal(priceStr);
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    @Override
    public String toString() {
        return "Product{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", price=" + price +
                ", description='" + description + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}