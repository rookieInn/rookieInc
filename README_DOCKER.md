# 🐳 Docker多服务部署

本项目使用Docker和Docker Compose实现多个本地服务的统一部署和管理。

## 🚀 快速开始

### 一键部署

```bash
# 快速启动所有服务
./quick-start.sh

# 或者使用部署脚本
./deploy.sh start
```

### 服务概览

| 服务 | 端口 | 访问地址 | 描述 |
|------|------|----------|------|
| OSS监控仪表板 | 5001 | http://oss.localhost | 对象存储监控 |
| 页面埋点API | 5002 | http://api.localhost | 用户行为分析 |
| 视频水印服务 | 5003 | http://video.localhost | 视频处理服务 |
| 微信群机器人 | 8000 | http://localhost:8000 | 智能聊天机器人 |
| Grafana监控 | 3000 | http://localhost:3000 | 监控可视化 |
| Prometheus | 9090 | http://localhost:9090 | 指标收集 |
| 服务概览 | 80 | http://localhost | 统一入口 |

## 📋 管理命令

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

## 🧪 测试部署

```bash
# 完整部署测试
./test-deployment.sh

# 健康检查测试
./test-deployment.sh health

# API功能测试
./test-deployment.sh api

# 查看资源使用
./test-deployment.sh resources
```

## ⚙️ 配置

### 环境变量

复制并编辑环境变量文件：

```bash
cp .env.example .env
# 编辑 .env 文件配置您的环境变量
```

### 本地域名配置

在 `/etc/hosts` 文件中添加：

```
127.0.0.1 oss.localhost
127.0.0.1 api.localhost
127.0.0.1 video.localhost
```

## 📊 监控

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **服务健康检查**: 各服务提供 `/health` 端点

## 🔧 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs [服务名]
   ```

2. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :端口号
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库服务
   docker-compose ps mysql mongodb redis
   ```

### 日志位置

- `logs/wechat/` - 微信群机器人日志
- `logs/oss/` - OSS监控日志
- `logs/tracking/` - 埋点API日志
- `logs/video/` - 视频处理日志
- `logs/bookmark/` - 书签同步日志
- `logs/nginx/` - Nginx访问日志

## 📚 详细文档

- [完整部署指南](DOCKER_DEPLOYMENT.md)
- [服务配置说明](DOCKER_DEPLOYMENT.md#服务配置)
- [监控和日志](DOCKER_DEPLOYMENT.md#监控和日志)
- [故障排除](DOCKER_DEPLOYMENT.md#故障排除)

## 🆘 支持

如有问题，请：
1. 查看日志文件
2. 运行健康检查
3. 参考故障排除部分
4. 提交Issue

---

**注意**: 请确保在生产环境中使用强密码和安全的配置。