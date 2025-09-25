-- 更新后的数据库脚本 - 使用DECIMAL类型处理金额
-- 作者: AI Assistant
-- 说明: 将原有的FLOAT/DOUBLE类型改为DECIMAL类型，确保金额计算的精确性

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce_db;

-- 用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    balance DECIMAL(15,2) DEFAULT 0.00 COMMENT '用户余额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 产品表
CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL COMMENT '产品价格',
    cost DECIMAL(10,2) DEFAULT 0.00 COMMENT '产品成本',
    discount_price DECIMAL(10,2) COMMENT '折扣价格',
    description TEXT,
    stock_quantity INT DEFAULT 0 COMMENT '库存数量',
    status ENUM('ACTIVE', 'INACTIVE', 'DISCONTINUED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL COMMENT '订单总金额',
    discount_amount DECIMAL(12,2) DEFAULT 0.00 COMMENT '折扣金额',
    tax_amount DECIMAL(12,2) DEFAULT 0.00 COMMENT '税费',
    shipping_fee DECIMAL(10,2) DEFAULT 0.00 COMMENT '运费',
    final_amount DECIMAL(12,2) NOT NULL COMMENT '最终支付金额',
    status ENUM('PENDING', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED') DEFAULT 'PENDING',
    payment_method VARCHAR(50),
    payment_status ENUM('UNPAID', 'PAID', 'REFUNDED') DEFAULT 'UNPAID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_order_number (order_number),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单明细表
CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
    total_price DECIMAL(12,2) NOT NULL COMMENT '小计金额',
    discount_rate DECIMAL(5,4) DEFAULT 0.0000 COMMENT '折扣率',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '折扣金额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 支付记录表
CREATE TABLE payments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    payment_number VARCHAR(32) NOT NULL UNIQUE COMMENT '支付单号',
    amount DECIMAL(12,2) NOT NULL COMMENT '支付金额',
    payment_method VARCHAR(50) NOT NULL,
    payment_status ENUM('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    transaction_id VARCHAR(100) COMMENT '第三方交易ID',
    paid_at TIMESTAMP NULL COMMENT '支付时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_payment_number (payment_number),
    INDEX idx_payment_status (payment_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 退款记录表
CREATE TABLE refunds (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    refund_number VARCHAR(32) NOT NULL UNIQUE COMMENT '退款单号',
    refund_amount DECIMAL(12,2) NOT NULL COMMENT '退款金额',
    refund_reason VARCHAR(500),
    refund_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED') DEFAULT 'PENDING',
    processed_at TIMESTAMP NULL COMMENT '处理时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_refund_number (refund_number),
    INDEX idx_refund_status (refund_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入示例数据
INSERT INTO users (username, email, phone, balance) VALUES 
    ('john_doe', 'john@example.com', '13800138001', 1000.50),
    ('jane_smith', 'jane@example.com', '13800138002', 2500.00),
    ('bob_wilson', 'bob@example.com', '13800138003', 0.00);

INSERT INTO products (name, price, cost, discount_price, description, stock_quantity) VALUES 
    ('MacBook Pro 16"', 19999.00, 15000.00, 18999.00, 'Apple MacBook Pro 16英寸笔记本电脑', 10),
    ('iPhone 15 Pro', 7999.00, 6000.00, 7599.00, 'Apple iPhone 15 Pro 256GB', 50),
    ('AirPods Pro', 1999.00, 1200.00, 1799.00, 'Apple AirPods Pro 2代', 100),
    ('Magic Mouse', 599.00, 300.00, NULL, 'Apple Magic Mouse 无线鼠标', 200);

-- 创建视图：产品利润分析
CREATE VIEW product_profit_analysis AS
SELECT 
    p.id,
    p.name,
    p.price,
    p.cost,
    p.discount_price,
    CASE 
        WHEN p.discount_price IS NOT NULL THEN p.discount_price - p.cost
        ELSE p.price - p.cost
    END AS profit_margin,
    ROUND(
        CASE 
            WHEN p.discount_price IS NOT NULL THEN (p.discount_price - p.cost) / p.discount_price * 100
            ELSE (p.price - p.cost) / p.price * 100
        END, 2
    ) AS profit_rate_percent
FROM products p
WHERE p.status = 'ACTIVE';

-- 创建存储过程：计算订单总金额
DELIMITER //
CREATE PROCEDURE CalculateOrderTotal(IN order_id BIGINT)
BEGIN
    DECLARE total DECIMAL(12,2) DEFAULT 0.00;
    DECLARE discount DECIMAL(12,2) DEFAULT 0.00;
    DECLARE tax DECIMAL(12,2) DEFAULT 0.00;
    DECLARE final_total DECIMAL(12,2) DEFAULT 0.00;
    
    -- 计算商品总金额
    SELECT COALESCE(SUM(total_price), 0.00) INTO total
    FROM order_items 
    WHERE order_id = order_id;
    
    -- 计算折扣金额
    SELECT COALESCE(SUM(discount_amount), 0.00) INTO discount
    FROM order_items 
    WHERE order_id = order_id;
    
    -- 计算税费（假设13%）
    SET tax = (total - discount) * 0.13;
    
    -- 计算最终金额
    SET final_total = total - discount + tax;
    
    -- 更新订单金额
    UPDATE orders 
    SET 
        total_amount = total,
        discount_amount = discount,
        tax_amount = tax,
        final_amount = final_total
    WHERE id = order_id;
    
    -- 返回计算结果
    SELECT 
        total AS subtotal,
        discount AS discount_amount,
        tax AS tax_amount,
        final_total AS final_amount;
END //
DELIMITER ;

-- 创建触发器：自动计算订单项总价
DELIMITER //
CREATE TRIGGER tr_order_items_calculate_total
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    -- 计算小计金额
    SET NEW.total_price = NEW.unit_price * NEW.quantity;
    
    -- 如果有折扣率，计算折扣金额
    IF NEW.discount_rate > 0 THEN
        SET NEW.discount_amount = NEW.total_price * NEW.discount_rate;
        SET NEW.total_price = NEW.total_price - NEW.discount_amount;
    END IF;
END //
DELIMITER ;

-- 创建索引优化查询性能
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_orders_created_status ON orders(created_at, status);
CREATE INDEX idx_products_price_status ON products(price, status);
CREATE INDEX idx_payments_status_created ON payments(payment_status, created_at);

-- 添加约束确保数据完整性
ALTER TABLE products ADD CONSTRAINT chk_price_positive CHECK (price >= 0);
ALTER TABLE products ADD CONSTRAINT chk_cost_positive CHECK (cost >= 0);
ALTER TABLE orders ADD CONSTRAINT chk_total_amount_positive CHECK (total_amount >= 0);
ALTER TABLE orders ADD CONSTRAINT chk_final_amount_positive CHECK (final_amount >= 0);
ALTER TABLE order_items ADD CONSTRAINT chk_quantity_positive CHECK (quantity > 0);
ALTER TABLE order_items ADD CONSTRAINT chk_unit_price_positive CHECK (unit_price >= 0);
ALTER TABLE payments ADD CONSTRAINT chk_payment_amount_positive CHECK (amount > 0);
ALTER TABLE refunds ADD CONSTRAINT chk_refund_amount_positive CHECK (refund_amount > 0);