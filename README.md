# 旅游路线规划智能体系统

基于AI技术的个性化旅游路线规划系统，根据用户需求智能生成最优旅游路线。

## 功能特性

### 核心功能
- 🤖 **AI智能规划**: 基于大语言模型的智能路线规划
- 🗺️ **地理信息集成**: 集成景点、酒店、交通等地理信息
- 💰 **预算估算**: 智能计算旅行预算和费用分解
- 🎯 **个性化推荐**: 根据用户偏好和旅行风格定制路线
- 💬 **多轮对话**: 支持上下文理解和历史记忆
- ⚡ **高性能缓存**: Redis缓存优化常见查询

### 性能指标
- ⏱️ **响应时间**: 1分钟内生成初步路线规划
- 🎯 **准确率**: 95%以上的需求匹配准确率
- 🔄 **灵活性**: 10-15分钟内完成路线调整优化
- 👥 **并发支持**: 支持100-200用户同时使用

### 安全特性
- 🛡️ **内容过滤**: 敏感词检测和有害内容拦截
- 🔐 **权限管理**: 区分普通用户和管理员权限
- 📝 **可解释性**: 提供推荐理由和决策解释
- ⚠️ **错误提示**: 智能错误检测和用户友好提示

## 技术架构

### 后端技术栈
- **FastAPI**: 现代、高性能的Web框架
- **SQLAlchemy**: Python SQL工具包和ORM
- **Redis**: 高性能缓存数据库
- **Pydantic**: 数据验证和序列化
- **JWT**: 用户认证和授权

### AI集成
- **大语言模型**: 支持通义千问、文心一言、Kimi等
- **地理信息系统**: 集成地图和位置服务
- **智能优化算法**: 路线优化和个性化推荐

### 前端界面
- **响应式设计**: 支持桌面和移动设备
- **现代化UI**: 基于Tailwind CSS的美观界面
- **交互体验**: 流畅的用户交互和实时反馈

## 快速开始

### 环境要求
- Python 3.8+
- Redis 6.0+
- SQLite 3.x

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd travel-agent
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要的配置
```

4. **初始化数据库**
```bash
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

5. **启动服务**
```bash
python run.py
```

6. **访问应用**
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### Docker部署

```bash
# 构建镜像
docker build -t travel-agent .

# 运行容器
docker run -p 8000:8000 travel-agent
```

## API使用

### 认证
```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "password"}'

# 登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'
```

### 创建路线规划
```bash
curl -X POST "http://localhost:8000/api/v1/plan" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
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

## 配置说明

### 环境变量
```env
# 数据库配置
DATABASE_URL=sqlite:///./travel_agent.db
REDIS_URL=redis://localhost:6379

# AI模型配置
OPENAI_API_KEY=your_openai_api_key
TONGYI_API_KEY=your_tongyi_api_key
WENXIN_API_KEY=your_wenxin_api_key

# 应用配置
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 外部API配置
MAPS_API_KEY=your_maps_api_key
WEATHER_API_KEY=your_weather_api_key
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_ai_agent.py
pytest tests/test_api.py

# 生成测试覆盖率报告
pytest --cov=app --cov-report=html
```

## 项目结构

```
travel-agent/
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   │   ├── auth.py        # 认证接口
│   │   └── routes.py      # 主要业务接口
│   ├── core/              # 核心功能
│   │   ├── ai_agent.py    # AI智能体
│   │   ├── cache.py       # 缓存管理
│   │   ├── config.py      # 配置管理
│   │   ├── content_filter.py # 内容过滤
│   │   ├── database.py    # 数据库配置
│   │   └── security.py    # 安全认证
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   └── travel.py      # 旅游模型
│   ├── schemas/           # 数据模式
│   │   ├── auth.py        # 认证模式
│   │   └── travel.py      # 旅游模式
│   ├── services/          # 服务层
│   │   ├── gis_service.py # 地理信息服务
│   │   └── route_optimizer.py # 路线优化器
│   ├── static/            # 静态文件
│   │   └── index.html     # Web界面
│   └── main.py            # 应用入口
├── tests/                 # 测试文件
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── run.py                # 启动脚本
└── README.md             # 项目说明
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目链接: [https://github.com/your-username/travel-agent](https://github.com/your-username/travel-agent)
- 问题反馈: [Issues](https://github.com/your-username/travel-agent/issues)

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- 🤖 基础AI智能体功能
- 🗺️ 地理信息集成
- 💰 预算估算功能
- 🎯 个性化推荐
- 💬 多轮对话支持
- 🛡️ 内容安全过滤
- 📱 响应式Web界面