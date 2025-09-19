# 短链接服务部署指南

## 概述

本文档介绍如何部署短链接服务，包括本地开发环境、Docker容器化部署和生产环境部署。

## 系统要求

### 最低要求
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 100Mbps

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 1Gbps

## 依赖服务

- **Java**: 17+
- **MySQL**: 8.0+
- **Redis**: 6.0+
- **Nginx**: 1.18+ (可选)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd shorturl-service
```

### 2. 使用Docker Compose (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f shorturl-service
```

### 3. 验证部署

```bash
# 健康检查
curl http://localhost:8080/api/health

# 创建短链接
curl -X POST http://localhost:8080/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com"}'
```

## 本地开发环境

### 1. 安装依赖

```bash
# 安装Java 17
sudo apt update
sudo apt install openjdk-17-jdk

# 安装Maven
sudo apt install maven

# 安装MySQL
sudo apt install mysql-server

# 安装Redis
sudo apt install redis-server
```

### 2. 配置数据库

```bash
# 启动MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库
mysql -u root -p
CREATE DATABASE shorturl CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shorturl'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON shorturl.* TO 'shorturl'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 配置Redis

```bash
# 启动Redis
sudo systemctl start redis
sudo systemctl enable redis

# 验证Redis
redis-cli ping
```

### 4. 运行应用

```bash
# 编译项目
mvn clean package

# 运行应用
java -jar target/shorturl-service-1.0.0.jar
```

## Docker部署

### 1. 构建镜像

```bash
# 构建应用镜像
docker build -t shorturl-service:1.0.0 .

# 查看镜像
docker images | grep shorturl
```

### 2. 运行容器

```bash
# 运行MySQL
docker run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=shorturl \
  -e MYSQL_USER=shorturl \
  -e MYSQL_PASSWORD=shorturl \
  -p 3306:3306 \
  mysql:8.0

# 运行Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7-alpine

# 运行应用
docker run -d --name shorturl-service \
  --link mysql:mysql \
  --link redis:redis \
  -e SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/shorturl \
  -e SPRING_DATASOURCE_USERNAME=shorturl \
  -e SPRING_DATASOURCE_PASSWORD=shorturl \
  -e SPRING_DATA_REDIS_HOST=redis \
  -p 8080:8080 \
  shorturl-service:1.0.0
```

## 生产环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git unzip

# 创建应用用户
sudo useradd -m -s /bin/bash shorturl
sudo usermod -aG docker shorturl
```

### 2. 安装Docker和Docker Compose

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 配置SSL证书

```bash
# 使用Let's Encrypt
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/key.pem
sudo chown shorturl:shorturl ./ssl/*
```

### 4. 配置环境变量

```bash
# 创建环境配置文件
cat > .env << EOF
DOMAIN=your-domain.com
MYSQL_ROOT_PASSWORD=your-secure-password
MYSQL_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
GRAFANA_PASSWORD=your-grafana-password
EOF
```

### 5. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 6. 配置Nginx (可选)

```bash
# 安装Nginx
sudo apt install nginx

# 创建配置文件
sudo tee /etc/nginx/sites-available/shorturl << EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/shorturl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 监控和日志

### 1. 访问监控面板

- **Grafana**: http://your-domain.com:3000 (admin/admin)
- **Prometheus**: http://your-domain.com:9090

### 2. 查看日志

```bash
# 应用日志
docker-compose logs -f shorturl-service

# 数据库日志
docker-compose logs -f mysql

# Redis日志
docker-compose logs -f redis

# 所有服务日志
docker-compose logs -f
```

### 3. 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看数据库性能
docker exec -it mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 查看Redis性能
docker exec -it redis redis-cli info stats
```

## 备份和恢复

### 1. 数据库备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份MySQL
docker exec mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD shorturl > $BACKUP_DIR/shorturl.sql

# 备份Redis
docker exec redis redis-cli --rdb $BACKUP_DIR/dump.rdb

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh

# 设置定时备份
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### 2. 数据恢复

```bash
# 恢复MySQL
docker exec -i mysql mysql -u root -p$MYSQL_ROOT_PASSWORD shorturl < backup.sql

# 恢复Redis
docker exec -i redis redis-cli --pipe < dump.rdb
```

## 故障排除

### 1. 常见问题

**问题**: 应用启动失败
```bash
# 检查日志
docker-compose logs shorturl-service

# 检查数据库连接
docker exec -it mysql mysql -u root -p -e "SHOW DATABASES;"

# 检查Redis连接
docker exec -it redis redis-cli ping
```

**问题**: 短链接无法访问
```bash
# 检查应用状态
curl http://localhost:8080/api/health

# 检查数据库数据
docker exec -it mysql mysql -u root -p -e "USE shorturl; SELECT * FROM short_urls LIMIT 5;"
```

**问题**: 性能问题
```bash
# 检查资源使用
docker stats

# 检查数据库性能
docker exec -it mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 检查Redis性能
docker exec -it redis redis-cli info stats
```

### 2. 日志分析

```bash
# 查看错误日志
docker-compose logs shorturl-service | grep ERROR

# 查看访问日志
docker-compose logs shorturl-service | grep "GET /api/s/"

# 实时监控日志
docker-compose logs -f shorturl-service | grep -E "(ERROR|WARN|INFO)"
```

## 安全建议

### 1. 网络安全

- 使用防火墙限制端口访问
- 配置SSL/TLS加密
- 定期更新系统和依赖

### 2. 数据安全

- 使用强密码
- 定期备份数据
- 加密敏感配置

### 3. 应用安全

- 启用访问日志
- 配置速率限制
- 定期安全扫描

## 扩展和优化

### 1. 水平扩展

```yaml
# docker-compose.yml
services:
  shorturl-service:
    deploy:
      replicas: 3
    environment:
      - SPRING_PROFILES_ACTIVE=cluster
```

### 2. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_short_code_active ON short_urls(short_code, is_active);
CREATE INDEX idx_created_at ON short_urls(created_at);

-- 分区表
ALTER TABLE access_logs PARTITION BY RANGE (YEAR(accessed_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026)
);
```

### 3. 缓存优化

```yaml
# application.yml
shorturl:
  cache:
    local:
      max-size: 50000
      ttl: 300s
    redis:
      ttl: 7200s
```

## 更新和维护

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build shorturl-service

# 滚动更新
docker-compose up -d --no-deps shorturl-service
```

### 2. 数据库迁移

```bash
# 运行迁移脚本
docker exec -it mysql mysql -u root -p shorturl < migration.sql
```

### 3. 监控维护

```bash
# 清理旧日志
docker system prune -f

# 清理旧镜像
docker image prune -f

# 重启服务
docker-compose restart
```