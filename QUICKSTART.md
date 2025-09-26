# 快速启动指南

## 🚀 5分钟快速体验

### 方法一：使用Docker（推荐）

1. **启动服务**
```bash
# 启动所有服务（应用 + Redis）
docker-compose up -d

# 查看服务状态
docker-compose ps
```

2. **访问应用**
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs

3. **停止服务**
```bash
docker-compose down
```

### 方法二：本地开发环境

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动Redis**（需要单独安装Redis）
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# 下载并安装Redis for Windows
```

3. **初始化数据**
```bash
python init_data.py
```

4. **启动应用**
```bash
python run.py
```

## 🎯 功能演示

### 1. 访问Web界面
打开浏览器访问 http://localhost:8000

### 2. 创建路线规划
1. 选择目的地（如：北京）
2. 选择旅行日期
3. 设置行程天数（如：3天）
4. 选择预算范围（如：中等）
5. 选择旅行风格（如：独自旅行）
6. 选择兴趣点（如：历史文化、美食）
7. 点击"生成智能路线规划"

### 3. 查看结果
系统将生成包含以下内容的路线规划：
- 📍 每日行程安排
- 💰 预算估算
- 🏨 推荐住宿
- 🚗 交通规划
- 💡 旅行贴士

## 🔧 配置说明

### 环境变量配置
复制 `.env.example` 到 `.env` 并修改配置：

```env
# 数据库配置
DATABASE_URL=sqlite:///./travel_agent.db
REDIS_URL=redis://localhost:6379

# 应用配置
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI模型配置（可选，用于增强功能）
OPENAI_API_KEY=your_openai_api_key
TONGYI_API_KEY=your_tongyi_api_key
WENXIN_API_KEY=your_wenxin_api_key
```

### 演示账号
- 用户名: `demo`
- 密码: `demo123`

## 📱 API使用示例

### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 3. 创建路线规划
```bash
curl -X POST "http://localhost:8000/api/v1/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "destination": "北京",
    "travel_dates": "2024-01-01",
    "duration_days": 3,
    "budget": "中等",
    "travel_style": "独自旅行",
    "interests": ["历史文化", "美食"],
    "group_size": 1
  }'
```

## 🐛 常见问题

### Q: 启动时提示"Redis连接失败"
A: 确保Redis服务正在运行：
```bash
# 检查Redis状态
redis-cli ping
# 应该返回 PONG
```

### Q: 数据库初始化失败
A: 确保有写入权限，或手动创建数据库目录：
```bash
mkdir -p data
```

### Q: 端口8000被占用
A: 修改端口配置：
```bash
# 在 run.py 中修改端口
uvicorn.run("app.main:app", port=8001)
```

### Q: 静态文件无法访问
A: 确保静态文件目录存在：
```bash
mkdir -p app/static
```

## 📊 性能测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行性能测试
pytest tests/test_performance.py -v

# 生成测试报告
pytest --cov=app --cov-report=html
```

### 压力测试
```bash
# 使用Apache Bench进行压力测试
ab -n 1000 -c 10 http://localhost:8000/health

# 使用wrk进行压力测试
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## 🔍 监控和日志

### 查看应用日志
```bash
# Docker方式
docker-compose logs -f app

# 本地方式
tail -f logs/app.log
```

### 健康检查
```bash
curl http://localhost:8000/health
```

### 系统状态
```bash
curl http://localhost:8000/api
```

## 🚀 生产部署

### 使用Docker Compose
```bash
# 生产环境配置
docker-compose -f docker-compose.prod.yml up -d
```

### 使用Nginx反向代理
```bash
# 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/travel-agent
sudo ln -s /etc/nginx/sites-available/travel-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件
2. 检查配置文件
3. 确认依赖服务状态
4. 提交Issue到项目仓库

---

🎉 **恭喜！** 您已成功启动旅游路线规划智能体系统！