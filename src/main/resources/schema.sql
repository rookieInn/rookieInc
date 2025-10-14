-- 创建用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    real_name VARCHAR(50) COMMENT '真实姓名',
    age INT COMMENT '年龄',
    gender INT DEFAULT 0 COMMENT '性别：0-未知，1-男，2-女',
    status INT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted INT DEFAULT 0 COMMENT '逻辑删除：0-未删除，1-已删除',
    version INT DEFAULT 1 COMMENT '版本号（乐观锁）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建索引
CREATE INDEX idx_username ON sys_user(username);
CREATE INDEX idx_email ON sys_user(email);
CREATE INDEX idx_phone ON sys_user(phone);
CREATE INDEX idx_status ON sys_user(status);
CREATE INDEX idx_create_time ON sys_user(create_time);
CREATE INDEX idx_deleted ON sys_user(deleted);