# 🐳 Docker多服务部署指南

本项目使用Docker和Docker Compose实现多个本地服务的统一部署和管理。

## 📋 服务概览

| 服务名称 | 端口 | 描述 | 访问地址 |
|---------|------|------|----------|
| 微信群ChatGPT机器人 | 内部 | 智能聊天机器人 | 内部服务 |
| OSS监控仪表板 | 5001 | 对象存储监控 | http://oss.localhost |
| 页面埋点API | 5002 | 用户行为分析 | http://api.localhost |
| 视频水印服务 | 5003 | 视频处理服务 | http://video.localhost |
| 书签同步服务 | 内部 | 书签数据同步 | 内部服务 |
| Nginx反向代理 | 80/443 | 负载均衡和SSL | http://localhost |
| MySQL数据库 | 3306 | 关系型数据库 | localhost:3306 |
| MongoDB数据库 | 27017 | 文档数据库 | localhost:27017 |
| Redis缓存 | 6379 | 内存缓存 | localhost:6379 |
| Prometheus监控 | 9090 | 指标收集 | http://localhost:9090 |
| Grafana仪表板 | 3000 | 监控可视化 | http://localhost:3000 |

## 🚀 快速开始

### 1. 环境准备

确保系统已安装：
- Docker (版本 20.10+)
- Docker Compose (版本 2.0+)

### 2. 一键部署

```bash
# 克隆项目（如果还没有）
git clone <your-repo-url>
cd <project-directory>

# 一键启动所有服务
./quick-start.sh
```

### 3. 配置环境变量

编辑 `.env` 文件，配置必要的环境变量：

```bash
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here

# 数据库密码
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_PASSWORD=your_app_password
MONGO_ROOT_PASSWORD=your_mongo_password

# 其他配置...
```

## 🛠️ 详细部署步骤

### 1. 手动部署

```bash
# 1. 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件配置您的环境变量

# 2. 创建必要目录
mkdir -p logs/{wechat,oss,tracking,video,bookmark,nginx}
mkdir -p data/{wechat,oss,tracking,video,bookmark}
mkdir -p ssl

# 3. 启动所有服务
docker-compose up -d --build

# 4. 查看服务状态
docker-compose ps
```

### 2. 服务管理

```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs [服务名]

# 健康检查
./deploy.sh health

# 更新服务
./deploy.sh update

# 清理资源
./deploy.sh clean
```

## 🔧 服务配置

### 微信群ChatGPT机器人

- **配置文件**: `bot_config.ini`, `bot_config_advanced.ini`
- **日志目录**: `logs/wechat/`
- **数据目录**: `data/wechat/`
- **依赖**: Redis, MySQL

### OSS监控仪表板

- **配置文件**: `oss_monitor_config.json`
- **端口**: 5001
- **日志目录**: `logs/oss/`
- **数据目录**: `data/oss/`
- **依赖**: MySQL

### 页面埋点API

- **配置文件**: `config.ini`
- **端口**: 5002
- **日志目录**: `logs/tracking/`
- **数据目录**: `data/tracking/`
- **依赖**: MongoDB

### 视频水印服务

- **端口**: 5003
- **日志目录**: `logs/video/`
- **数据目录**: `data/video/`
- **输入目录**: `data/video/input/`
- **输出目录**: `data/video/output/`

### 书签同步服务

- **配置文件**: `bookmark_sync_config.json`
- **日志目录**: `logs/bookmark/`
- **数据目录**: `data/bookmark/`
- **依赖**: MySQL

## 🌐 网络配置

### 本地域名配置

为了使用自定义域名访问服务，需要在 `/etc/hosts` 文件中添加：

```
127.0.0.1 oss.localhost
127.0.0.1 api.localhost
127.0.0.1 video.localhost
```

### Nginx反向代理

Nginx作为反向代理服务器，提供：
- 负载均衡
- SSL终止
- 静态文件缓存
- CORS支持

## 📊 监控和日志

### Prometheus监控

- **访问地址**: http://localhost:9090
- **配置文件**: `docker/prometheus/prometheus.yml`
- **监控指标**: 服务健康状态、性能指标

### Grafana仪表板

- **访问地址**: http://localhost:3000
- **默认账号**: admin/admin
- **数据源**: Prometheus

### 日志管理

各服务日志分别存储在：
- `logs/wechat/` - 微信群机器人日志
- `logs/oss/` - OSS监控日志
- `logs/tracking/` - 埋点API日志
- `logs/video/` - 视频处理日志
- `logs/bookmark/` - 书签同步日志
- `logs/nginx/` - Nginx访问日志

## 🔒 安全配置

### SSL证书

将SSL证书文件放置在 `ssl/` 目录下：
- `ssl/cert.pem` - 证书文件
- `ssl/key.pem` - 私钥文件

### 环境变量安全

- 使用强密码
- 定期轮换API密钥
- 不要将 `.env` 文件提交到版本控制

## 🐛 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs [服务名]
   
   # 检查端口占用
   netstat -tulpn | grep :端口号
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   docker-compose ps mysql mongodb redis
   
   # 查看数据库日志
   docker-compose logs mysql
   ```

3. **Nginx配置错误**
   ```bash
   # 测试Nginx配置
   docker exec nginx-proxy nginx -t
   
   # 重新加载配置
   docker exec nginx-proxy nginx -s reload
   ```

### 性能优化

1. **资源限制**
   在 `docker-compose.yml` 中为服务添加资源限制：
   ```yaml
   services:
     service-name:
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'
   ```

2. **日志轮转**
   配置Docker日志轮转：
   ```yaml
   services:
     service-name:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

## 📚 开发指南

### 添加新服务

1. 创建服务Dockerfile：`docker/新服务.Dockerfile`
2. 在 `docker-compose.yml` 中添加服务配置
3. 更新Nginx配置（如需要）
4. 添加监控配置

### 自定义配置

- 修改 `docker-compose.yml` 调整服务配置
- 更新 `docker/nginx/conf.d/default.conf` 修改路由规则
- 编辑 `docker/prometheus/prometheus.yml` 添加监控目标

## 📞 支持

如有问题，请：
1. 查看日志文件
2. 检查服务状态
3. 参考故障排除部分
4. 提交Issue或联系维护者

---

**注意**: 请确保在生产环境中使用强密码和安全的配置。