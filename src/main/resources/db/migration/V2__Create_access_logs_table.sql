-- 创建访问记录表
CREATE TABLE IF NOT EXISTS access_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    short_url_id BIGINT NOT NULL COMMENT '短链接ID',
    ip_address VARCHAR(45) COMMENT '访问者IP地址',
    user_agent VARCHAR(500) COMMENT '访问者用户代理',
    referer VARCHAR(2048) COMMENT '来源页面',
    country VARCHAR(2) COMMENT '国家代码',
    city VARCHAR(100) COMMENT '城市',
    device_type VARCHAR(20) COMMENT '设备类型',
    browser VARCHAR(50) COMMENT '浏览器',
    os VARCHAR(50) COMMENT '操作系统',
    accessed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
    
    INDEX idx_short_url_id (short_url_id),
    INDEX idx_accessed_at (accessed_at),
    INDEX idx_ip_address (ip_address),
    INDEX idx_user_agent (user_agent(100)),
    INDEX idx_country (country),
    INDEX idx_device_type (device_type),
    INDEX idx_browser (browser),
    INDEX idx_os (os),
    
    FOREIGN KEY (short_url_id) REFERENCES short_urls(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='访问记录表';