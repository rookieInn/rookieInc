package com.example.entity;

import javax.persistence.*;
import javax.validation.constraints.DecimalMin;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 产品JPA实体类
 * 
 * 使用JPA注解映射到数据库表
 * 所有金额字段都使用BigDecimal类型
 */
@Entity
@Table(name = "products")
public class ProductEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "产品名称不能为空")
    @Column(name = "name", nullable = false, length = 100)
    private String name;
    
    @NotNull(message = "产品价格不能为空")
    @DecimalMin(value = "0.0", inclusive = false, message = "产品价格必须大于0")
    @Column(name = "price", nullable = false, precision = 10, scale = 2)
    private BigDecimal price;
    
    @DecimalMin(value = "0.0", inclusive = true, message = "产品成本不能为负数")
    @Column(name = "cost", precision = 10, scale = 2)
    private BigDecimal cost = BigDecimal.ZERO;
    
    @DecimalMin(value = "0.0", inclusive = true, message = "折扣价格不能为负数")
    @Column(name = "discount_price", precision = 10, scale = 2)
    private BigDecimal discountPrice;
    
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;
    
    @Column(name = "stock_quantity")
    private Integer stockQuantity = 0;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private ProductStatus status = ProductStatus.ACTIVE;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // 默认构造函数
    public ProductEntity() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    // 带参数的构造函数
    public ProductEntity(String name, BigDecimal price, String description) {
        this();
        this.name = name;
        this.price = price;
        this.description = description;
    }
    
    // 便捷构造函数，接受String类型的价格
    public ProductEntity(String name, String priceStr, String description) {
        this();
        this.name = name;
        this.price = new BigDecimal(priceStr);
        this.description = description;
    }
    
    // JPA生命周期回调
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
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
    
    public BigDecimal getCost() {
        return cost;
    }
    
    public void setCost(BigDecimal cost) {
        this.cost = cost;
    }
    
    public BigDecimal getDiscountPrice() {
        return discountPrice;
    }
    
    public void setDiscountPrice(BigDecimal discountPrice) {
        this.discountPrice = discountPrice;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public Integer getStockQuantity() {
        return stockQuantity;
    }
    
    public void setStockQuantity(Integer stockQuantity) {
        this.stockQuantity = stockQuantity;
    }
    
    public ProductStatus getStatus() {
        return status;
    }
    
    public void setStatus(ProductStatus status) {
        this.status = status;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    // 业务方法
    /**
     * 获取实际销售价格（如果有折扣价格则返回折扣价格，否则返回原价）
     */
    public BigDecimal getActualPrice() {
        return discountPrice != null ? discountPrice : price;
    }
    
    /**
     * 计算利润率
     */
    public BigDecimal getProfitMargin() {
        if (cost == null || cost.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        return getActualPrice().subtract(cost);
    }
    
    /**
     * 计算利润率百分比
     */
    public BigDecimal getProfitRate() {
        if (cost == null || cost.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        BigDecimal profit = getProfitMargin();
        return profit.divide(getActualPrice(), 4, BigDecimal.ROUND_HALF_UP)
                    .multiply(new BigDecimal("100"));
    }
    
    /**
     * 检查是否有库存
     */
    public boolean isInStock() {
        return stockQuantity != null && stockQuantity > 0;
    }
    
    /**
     * 检查是否在售
     */
    public boolean isActive() {
        return status == ProductStatus.ACTIVE;
    }
    
    @Override
    public String toString() {
        return "ProductEntity{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", price=" + price +
                ", cost=" + cost +
                ", discountPrice=" + discountPrice +
                ", description='" + description + '\'' +
                ", stockQuantity=" + stockQuantity +
                ", status=" + status +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
    
    /**
     * 产品状态枚举
     */
    public enum ProductStatus {
        ACTIVE("在售"),
        INACTIVE("下架"),
        DISCONTINUED("停产");
        
        private final String description;
        
        ProductStatus(String description) {
            this.description = description;
        }
        
        public String getDescription() {
            return description;
        }
    }
}