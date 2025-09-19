-- 创建短链接表
CREATE TABLE IF NOT EXISTS short_urls (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    short_code VARCHAR(8) NOT NULL UNIQUE COMMENT '短码',
    original_url VARCHAR(2048) NOT NULL COMMENT '原始URL',
    title VARCHAR(255) COMMENT '标题',
    description VARCHAR(500) COMMENT '描述',
    access_count BIGINT NOT NULL DEFAULT 0 COMMENT '访问次数',
    unique_access_count BIGINT NOT NULL DEFAULT 0 COMMENT '唯一访问次数',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
    expires_at DATETIME COMMENT '过期时间',
    password VARCHAR(64) COMMENT '密码',
    ip_address VARCHAR(45) COMMENT '创建者IP地址',
    user_agent VARCHAR(500) COMMENT '创建者用户代理',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_short_code (short_code),
    INDEX idx_original_url (original_url(255)),
    INDEX idx_created_at (created_at),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active),
    INDEX idx_access_count (access_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='短链接表';