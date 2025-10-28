-- 创建数据库
CREATE DATABASE IF NOT EXISTS test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE test_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    role_ids JSON COMMENT '角色ID列表，存储为JSON数组，如[1,2,3,4,5]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_email (email),
    INDEX idx_role_ids ((CAST(role_ids AS CHAR(255) ARRAY)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 插入测试数据
INSERT INTO users (name, email, role_ids) VALUES
('张三', 'zhangsan@example.com', JSON_ARRAY(1, 2, 3)),
('李四', 'lisi@example.com', JSON_ARRAY(2, 4, 5)),
('王五', 'wangwu@example.com', JSON_ARRAY(1, 5)),
('赵六', 'zhaoliu@example.com', JSON_ARRAY(3, 6, 7)),
('孙七', 'sunqi@example.com', JSON_ARRAY(1, 2, 3, 4, 5));

-- 验证数据
SELECT 
    id, 
    name, 
    email, 
    role_ids,
    JSON_LENGTH(role_ids) as role_count
FROM users;

-- 测试JSON查询功能
-- 1. 查询包含角色2的所有用户
SELECT 
    id, 
    name, 
    role_ids
FROM users 
WHERE JSON_CONTAINS(role_ids, JSON_QUOTE(2));

-- 2. 查询包含角色1或5的用户
SELECT 
    id, 
    name, 
    role_ids
FROM users 
WHERE JSON_OVERLAPS(role_ids, JSON_ARRAY(1, 5));

-- 3. 查询同时包含角色1和5的用户
SELECT 
    id, 
    name, 
    role_ids
FROM users 
WHERE JSON_CONTAINS(role_ids, JSON_QUOTE(1)) 
  AND JSON_CONTAINS(role_ids, JSON_QUOTE(5));

-- 4. 统计包含角色2的用户数量
SELECT COUNT(*) as user_count
FROM users 
WHERE JSON_CONTAINS(role_ids, JSON_QUOTE(2));