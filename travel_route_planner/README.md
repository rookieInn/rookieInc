# AI旅游路线规划系统

基于AI技术的智能旅游路线规划系统，为用户提供个性化的旅游路线规划和AI助手服务。

## 功能特性

### 核心功能
- **智能路线规划**: 基于用户偏好、预算、时间等因素生成个性化旅游路线
- **AI助手对话**: 支持多轮对话，提供旅游咨询和建议
- **地图可视化**: 集成地图显示，直观展示路线和景点位置
- **费用预算**: 自动计算门票、餐饮、交通、住宿等费用
- **路线优化**: 根据用户反馈实时优化路线规划

### 技术特性
- **多AI模型支持**: 集成通义千问、文心一言、OpenAI等主流AI模型
- **智能缓存**: Redis缓存机制，提升响应速度
- **实时数据**: 集成景点数据库、交通信息等实时数据
- **安全认证**: JWT令牌认证，确保用户数据安全
- **响应式设计**: 支持PC和移动端访问

## 系统架构

```
travel_route_planner/
├── backend/                 # 后端核心模块
│   ├── ai_models.py        # AI模型集成
│   ├── route_planner.py    # 路线规划算法
│   ├── cache_manager.py    # 缓存管理
│   ├── auth.py            # 认证安全
│   ├── api_routes.py      # API路由
│   └── schemas.py         # 数据模型
├── frontend/               # 前端界面
│   ├── index.html         # 主页面
│   └── static/            # 静态资源
│       ├── css/style.css  # 样式文件
│       └── js/app.js      # JavaScript逻辑
├── database/              # 数据库相关
│   ├── models.py          # 数据模型
│   ├── database.py        # 数据库连接
│   └── migrations/        # 数据库迁移
├── config/                # 配置文件
│   └── settings.py        # 系统配置
├── main.py               # 主应用程序
├── requirements.txt      # 依赖包列表
└── start.sh             # 启动脚本
```

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- Node.js 14+ (可选，用于前端开发)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd travel_route_planner
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

4. **初始化数据库**
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE travel_planner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 初始化表结构
python -c "from database.database import init_db; init_db()"
```

5. **启动服务**
```bash
# 使用启动脚本
./start.sh

# 或直接运行
python main.py
```

6. **访问系统**
- 打开浏览器访问: http://localhost:8000
- API文档: http://localhost:8000/docs

## 配置说明

### 环境变量配置

在 `.env` 文件中配置以下参数：

```env
# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/travel_planner
REDIS_URL=redis://localhost:6379/0

# AI模型配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here
QIANFAN_AK=your_qianfan_ak_here
QIANFAN_SK=your_qianfan_sk_here
OPENAI_API_KEY=your_openai_api_key_here

# 地图服务
MAPBOX_TOKEN=your_mapbox_token_here
BAIDU_MAP_AK=your_baidu_map_ak_here

# 安全配置
SECRET_KEY=your-secret-key-change-this-in-production
```

### AI模型配置

系统支持多种AI模型，按优先级选择：

1. **通义千问** (推荐)
   - 获取API Key: https://dashscope.aliyun.com/
   - 配置 `DASHSCOPE_API_KEY`

2. **文心一言**
   - 获取AK/SK: https://cloud.baidu.com/
   - 配置 `QIANFAN_AK` 和 `QIANFAN_SK`

3. **OpenAI** (备用)
   - 获取API Key: https://platform.openai.com/
   - 配置 `OPENAI_API_KEY`

## API接口

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 路线规划接口
- `POST /api/v1/route/plan` - 创建路线规划
- `POST /api/v1/route/optimize` - 优化路线
- `GET /api/v1/scenic-spots` - 获取景点列表

### 对话接口
- `POST /api/v1/chat` - 与AI对话
- `GET /api/v1/chat/history/{session_id}` - 获取对话历史

### 用户管理接口
- `GET /api/v1/plans` - 获取用户计划列表
- `GET /api/v1/plans/{plan_id}` - 获取计划详情
- `DELETE /api/v1/plans/{plan_id}` - 删除计划

## 使用指南

### 1. 用户注册和登录
- 访问系统首页，点击"注册"按钮
- 填写用户名、邮箱和密码完成注册
- 使用注册信息登录系统

### 2. 创建旅游路线
- 点击"路线规划"进入规划页面
- 填写目的地、时间、预算等信息
- 点击"生成路线"获取AI规划的路线
- 查看地图视图或列表视图

### 3. 与AI助手对话
- 点击"AI助手"进入对话页面
- 输入问题或需求，AI将提供专业建议
- 支持多轮对话，AI会记住上下文

### 4. 管理旅游计划
- 在"我的计划"页面查看所有计划
- 点击"查看详情"查看具体规划
- 可以删除不需要的计划

## 性能指标

根据需求规格说明书，系统达到以下性能指标：

- **响应时间**: 1分钟内提供初步路线规划
- **准确率**: 路线规划准确率达到95%以上
- **灵活性**: 10-15分钟内完成路线调整优化
- **并发处理**: 支持100-200用户同时访问
- **缓存命中率**: 常见目的地缓存命中率>80%

## 安全特性

- **用户认证**: JWT令牌认证机制
- **权限管理**: 区分普通用户和管理员权限
- **输入验证**: 严格的输入数据验证和清理
- **内容过滤**: 敏感词检测和有害内容拦截
- **安全日志**: 记录安全事件和异常操作

## 部署说明

### Docker部署

```bash
# 构建镜像
docker build -t travel-planner .

# 运行容器
docker run -d -p 8000:8000 --name travel-planner travel-planner
```

### 生产环境部署

1. **配置生产环境变量**
2. **使用Gunicorn运行**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
3. **配置Nginx反向代理**
4. **配置SSL证书**
5. **设置监控和日志**

## 开发指南

### 项目结构说明

- `backend/`: 后端核心业务逻辑
- `frontend/`: 前端用户界面
- `database/`: 数据库模型和迁移
- `config/`: 系统配置文件
- `utils/`: 工具函数和辅助模块

### 开发环境设置

1. **安装开发依赖**
```bash
pip install -r requirements-dev.txt
```

2. **运行测试**
```bash
pytest tests/
```

3. **代码格式化**
```bash
black .
isort .
```

4. **类型检查**
```bash
mypy .
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库连接配置
   - 确认数据库用户权限

2. **AI模型调用失败**
   - 检查API Key配置
   - 验证网络连接
   - 查看API调用限制

3. **缓存服务异常**
   - 检查Redis服务状态
   - 验证Redis连接配置
   - 查看内存使用情况

4. **前端页面无法访问**
   - 检查静态文件路径
   - 验证CORS配置
   - 查看浏览器控制台错误

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目地址: [GitHub Repository URL]

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基础路线规划功能
- 集成AI模型和对话功能
- 完成用户认证和权限管理
- 添加地图可视化和费用计算