-- 插入测试数据
INSERT INTO sys_user (username, password, email, phone, real_name, age, gender, status, create_time, update_time, deleted, version) VALUES
('admin', 'admin123', 'admin@example.com', '13800138000', '管理员', 30, 1, 1, NOW(), NOW(), 0, 1),
('user1', 'user123', 'user1@example.com', '13800138001', '张三', 25, 1, 1, NOW(), NOW(), 0, 1),
('user2', 'user123', 'user2@example.com', '13800138002', '李四', 28, 2, 1, NOW(), NOW(), 0, 1),
('user3', 'user123', 'user3@example.com', '13800138003', '王五', 32, 1, 0, NOW(), NOW(), 0, 1),
('user4', 'user123', 'user4@example.com', '13800138004', '赵六', 26, 2, 1, NOW(), NOW(), 0, 1),
('test1', 'test123', 'test1@example.com', '13800138005', '测试用户1', 22, 1, 1, NOW(), NOW(), 0, 1),
('test2', 'test123', 'test2@example.com', '13800138006', '测试用户2', 24, 2, 1, NOW(), NOW(), 0, 1),
('demo1', 'demo123', 'demo1@example.com', '13800138007', '演示用户1', 29, 1, 1, NOW(), NOW(), 0, 1),
('demo2', 'demo123', 'demo2@example.com', '13800138008', '演示用户2', 31, 2, 0, NOW(), NOW(), 0, 1),
('guest', 'guest123', 'guest@example.com', '13800138009', '访客用户', 20, 0, 1, NOW(), NOW(), 0, 1);