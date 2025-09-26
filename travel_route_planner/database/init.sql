-- AI旅游路线规划系统数据库初始化脚本

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS travel_planner 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE travel_planner;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- 创建景点表
CREATE TABLE IF NOT EXISTS scenic_spots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    category VARCHAR(50),
    opening_hours VARCHAR(200),
    ticket_price DECIMAL(10, 2),
    rating DECIMAL(3, 2) DEFAULT 0.0,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_location (location)
);

-- 创建旅游计划表
CREATE TABLE IF NOT EXISTS travel_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    budget DECIMAL(10, 2),
    travel_type VARCHAR(50),
    preferences JSON,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_destination (destination),
    INDEX idx_status (status)
);

-- 创建计划景点关联表
CREATE TABLE IF NOT EXISTS plan_spots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    spot_id INT NOT NULL,
    visit_date DATETIME NOT NULL,
    visit_order INT NOT NULL,
    duration_hours DECIMAL(4, 2) DEFAULT 2.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (spot_id) REFERENCES scenic_spots(id) ON DELETE CASCADE,
    INDEX idx_plan_id (plan_id),
    INDEX idx_spot_id (spot_id)
);

-- 创建对话记录表
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    plan_id INT,
    session_id VARCHAR(100) NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES travel_plans(id) ON DELETE SET NULL,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- 创建系统缓存表
CREATE TABLE IF NOT EXISTS system_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    cache_type VARCHAR(50) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
);

-- 插入示例数据

-- 插入示例用户
INSERT INTO users (username, email, hashed_password, is_active, is_admin) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/7.8.2.', TRUE, TRUE),
('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/7.8.2.', TRUE, FALSE);

-- 插入示例景点数据
INSERT INTO scenic_spots (name, description, location, latitude, longitude, category, opening_hours, ticket_price, rating) VALUES
('天安门广场', '世界最大的城市广场，位于北京市中心', '北京市东城区', 39.9042, 116.4074, '人文景观', '05:00-22:00', 0.00, 4.8),
('故宫博物院', '明清两代皇家宫殿，现为世界文化遗产', '北京市东城区', 39.9163, 116.3972, '人文景观', '08:30-17:00', 60.00, 4.7),
('颐和园', '中国古典园林之首，皇家园林博物馆', '北京市海淀区', 39.9999, 116.2755, '人文景观', '06:30-18:00', 30.00, 4.6),
('八达岭长城', '万里长城最著名的一段，世界文化遗产', '北京市延庆区', 40.3589, 116.0144, '人文景观', '06:30-19:00', 40.00, 4.5),
('天坛公园', '明清皇帝祭天的场所，世界文化遗产', '北京市东城区', 39.8823, 116.4066, '人文景观', '06:00-22:00', 15.00, 4.4),
('北海公园', '中国现存最古老、最完整、最具综合性的皇家园林', '北京市西城区', 39.9289, 116.3883, '人文景观', '06:30-21:00', 10.00, 4.3),
('什刹海', '北京内城唯一一处具有开阔水面的开放型景区', '北京市西城区', 39.9388, 116.3883, '人文景观', '全天开放', 0.00, 4.2),
('南锣鼓巷', '北京最古老的街区之一，最具北京风情的街巷', '北京市东城区', 39.9388, 116.4044, '人文景观', '全天开放', 0.00, 4.1);

-- 插入示例旅游计划
INSERT INTO travel_plans (user_id, title, destination, start_date, end_date, budget, travel_type, preferences) VALUES
(2, '北京三日游', '北京', '2024-02-01 09:00:00', '2024-02-03 18:00:00', 1000.00, '休闲游', '{"categories": ["人文景观"], "min_rating": 4.0}'),
(2, '北京深度游', '北京', '2024-02-10 08:00:00', '2024-02-15 20:00:00', 2000.00, '文化游', '{"categories": ["人文景观", "自然风光"], "special_requirements": ["无障碍设施"]}');

-- 插入示例计划景点关联
INSERT INTO plan_spots (plan_id, spot_id, visit_date, visit_order, duration_hours, notes) VALUES
(1, 1, '2024-02-01 09:00:00', 1, 2.0, '上午游览天安门广场'),
(1, 2, '2024-02-01 11:00:00', 2, 3.0, '下午参观故宫博物院'),
(1, 3, '2024-02-02 09:00:00', 3, 4.0, '全天游览颐和园'),
(1, 4, '2024-02-03 08:00:00', 4, 6.0, '登长城，注意保暖');

-- 创建视图：用户计划统计
CREATE VIEW user_plan_stats AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(tp.id) as total_plans,
    COUNT(CASE WHEN tp.status = 'active' THEN 1 END) as active_plans,
    COUNT(CASE WHEN tp.status = 'completed' THEN 1 END) as completed_plans,
    AVG(tp.budget) as avg_budget
FROM users u
LEFT JOIN travel_plans tp ON u.id = tp.user_id
GROUP BY u.id, u.username;

-- 创建视图：景点统计
CREATE VIEW scenic_spot_stats AS
SELECT 
    category,
    COUNT(*) as spot_count,
    AVG(rating) as avg_rating,
    AVG(ticket_price) as avg_price,
    MIN(ticket_price) as min_price,
    MAX(ticket_price) as max_price
FROM scenic_spots
WHERE is_active = TRUE
GROUP BY category;

-- 创建存储过程：清理过期缓存
DELIMITER //
CREATE PROCEDURE CleanExpiredCache()
BEGIN
    DELETE FROM system_cache WHERE expires_at < NOW();
    SELECT ROW_COUNT() as deleted_count;
END //
DELIMITER ;

-- 创建事件：定期清理过期缓存（每天凌晨2点执行）
CREATE EVENT IF NOT EXISTS clean_cache_event
ON SCHEDULE EVERY 1 DAY
STARTS '2024-01-01 02:00:00'
DO
  CALL CleanExpiredCache();

-- 启用事件调度器
SET GLOBAL event_scheduler = ON;

-- 创建索引优化查询性能
CREATE INDEX idx_travel_plans_user_date ON travel_plans(user_id, start_date, end_date);
CREATE INDEX idx_conversations_user_session ON conversations(user_id, session_id, created_at);
CREATE INDEX idx_scenic_spots_rating ON scenic_spots(rating DESC);
CREATE INDEX idx_scenic_spots_price ON scenic_spots(ticket_price);

-- 设置字符集和排序规则
ALTER DATABASE travel_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as message;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as scenic_spot_count FROM scenic_spots;
SELECT COUNT(*) as travel_plan_count FROM travel_plans;