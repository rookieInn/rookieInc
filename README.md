# 直播管理后台系统

一个功能完整的直播管理后台系统，支持用户管理、直播房间管理、内容审核、数据统计等功能。

## 功能特性

### 🔐 用户认证与权限管理
- 用户注册/登录
- JWT令牌认证
- 多角色权限控制（超级管理员、管理员、审核员、主播、观众）
- 密码加密存储

### 📺 直播房间管理
- 创建/编辑/删除直播房间
- 直播状态管理（预约、直播中、已结束、已封禁）
- 实时观众数量统计
- 直播数据记录与分析
- 流媒体URL生成

### 👥 用户管理
- 用户列表查看与搜索
- 用户信息编辑
- 用户状态管理（启用/禁用）
- 用户角色分配
- 用户统计数据

### 🚨 内容审核与举报管理
- 举报提交与处理
- 多类型举报支持（垃圾信息、骚扰、不当内容等）
- 审核员分配
- 举报状态跟踪
- 审核统计数据

### 🔔 通知系统
- 实时通知推送
- 通知分类管理
- 批量通知发送
- 通知已读状态管理

### 📊 数据统计与监控
- 实时数据仪表盘
- 用户统计图表
- 直播数据统计
- 举报处理统计
- 系统健康监控

## 技术栈

### 后端
- **Node.js** - 运行时环境
- **Express.js** - Web框架
- **TypeScript** - 类型安全
- **MongoDB** - 主数据库
- **Redis** - 缓存和会话存储
- **Socket.io** - 实时通信
- **JWT** - 身份认证
- **Winston** - 日志管理

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Ant Design** - UI组件库
- **React Router** - 路由管理
- **Zustand** - 状态管理
- **React Query** - 数据获取
- **Socket.io Client** - 实时通信
- **Vite** - 构建工具

## 项目结构

```
live-streaming-admin/
├── src/                    # 后端源码
│   ├── server/            # 服务器入口
│   ├── models/            # 数据模型
│   ├── controllers/       # 控制器
│   ├── services/          # 业务逻辑
│   ├── middleware/        # 中间件
│   ├── routes/            # 路由
│   ├── types/             # 类型定义
│   └── config/            # 配置文件
├── client/                # 前端源码
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── services/      # API服务
│   │   ├── store/         # 状态管理
│   │   └── types/         # 类型定义
│   └── public/            # 静态资源
├── logs/                  # 日志文件
├── uploads/               # 上传文件
└── docs/                  # 文档
```

## 快速开始

### 环境要求
- Node.js >= 16.0.0
- MongoDB >= 4.4
- Redis >= 6.0

### 安装依赖

```bash
# 安装后端依赖
npm install

# 安装前端依赖
cd client
npm install
```

### 环境配置

1. 复制环境变量文件：
```bash
cp .env.example .env
```

2. 修改 `.env` 文件中的配置：
```env
# 服务器配置
PORT=3000
NODE_ENV=development

# 数据库配置
MONGODB_URI=mongodb://localhost:27017/live_streaming_admin
REDIS_URL=redis://localhost:6379

# JWT配置
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_IN=7d

# 其他配置...
```

### 启动服务

#### 开发模式
```bash
# 同时启动前后端服务
npm run dev

# 或者分别启动
npm run dev:server  # 启动后端服务 (端口 3000)
npm run dev:client  # 启动前端服务 (端口 3001)
```

#### 生产模式
```bash
# 构建项目
npm run build

# 启动生产服务
npm start
```

### 访问应用

- 前端应用：http://localhost:3001
- 后端API：http://localhost:3000/api
- 健康检查：http://localhost:3000/health

## API文档

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息
- `POST /api/auth/change-password` - 修改密码

### 用户管理接口
- `GET /api/users` - 获取用户列表
- `GET /api/users/:id` - 获取用户详情
- `PUT /api/users/:id` - 更新用户信息
- `DELETE /api/users/:id` - 删除用户
- `PATCH /api/users/:id/toggle-status` - 切换用户状态

### 直播房间接口
- `GET /api/rooms` - 获取房间列表
- `POST /api/rooms` - 创建房间
- `GET /api/rooms/:id` - 获取房间详情
- `PUT /api/rooms/:id` - 更新房间
- `DELETE /api/rooms/:id` - 删除房间
- `POST /api/rooms/:id/start` - 开始直播
- `POST /api/rooms/:id/end` - 结束直播

### 举报管理接口
- `GET /api/reports` - 获取举报列表
- `POST /api/reports` - 创建举报
- `GET /api/reports/:id` - 获取举报详情
- `POST /api/reports/:id/assign` - 分配审核员
- `POST /api/reports/:id/resolve` - 解决举报
- `POST /api/reports/:id/reject` - 拒绝举报

### 通知接口
- `GET /api/notifications` - 获取通知列表
- `PATCH /api/notifications/:id/read` - 标记已读
- `PATCH /api/notifications/mark-all-read` - 全部标记已读
- `DELETE /api/notifications/:id` - 删除通知

## 部署指南

### Docker部署

1. 创建 `docker-compose.yml`：
```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - mongodb
      - redis
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/live_streaming_admin
      - REDIS_URL=redis://redis:6379

volumes:
  mongodb_data:
```

2. 启动服务：
```bash
docker-compose up -d
```

### 手动部署

1. 安装PM2：
```bash
npm install -g pm2
```

2. 构建项目：
```bash
npm run build
```

3. 启动服务：
```bash
pm2 start dist/server.js --name "live-streaming-admin"
```

## 开发指南

### 代码规范
- 使用TypeScript进行类型检查
- 遵循ESLint规则
- 使用Prettier格式化代码
- 编写单元测试

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/live-streaming-admin/issues)
- 邮箱: admin@livestream.com

---

**注意**: 这是一个演示项目，生产环境使用前请确保进行充分的安全测试和性能优化。