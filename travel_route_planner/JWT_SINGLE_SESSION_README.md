# JWT单点登录控制系统

## 功能概述

本系统实现了基于JWT的单点登录控制，确保每个用户账户只能同时在一个终端登录。当用户在新设备/浏览器登录时，会自动使之前的所有登录会话失效。

## 核心特性

### 1. 单点登录控制
- 每个用户只能有一个有效的登录会话
- 新登录会自动挤掉之前的登录
- 使用数据库存储当前有效的session_token

### 2. 安全机制
- JWT token包含session_id和jti（JWT ID）
- 每次登录生成新的session_id
- 服务端验证token与用户当前session_token是否匹配

### 3. 管理功能
- 用户登出功能
- 管理员强制登出其他用户
- 登录时间记录

## 数据库变更

### User表新增字段
```sql
ALTER TABLE users 
ADD COLUMN session_token VARCHAR(500) NULL,
ADD COLUMN last_login_at DATETIME NULL,
ADD INDEX idx_users_session_token (session_token);
```

## API接口

### 1. 用户登录
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=testpass123
```

**响应:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 用户登出
```http
POST /auth/logout
Authorization: Bearer <token>
```

**响应:**
```json
{
  "message": "登出成功"
}
```

### 3. 强制登出（管理员）
```http
POST /auth/force-logout/{user_id}
Authorization: Bearer <admin_token>
```

**响应:**
```json
{
  "message": "用户 username 已被强制登出"
}
```

### 4. 获取当前用户信息
```http
GET /auth/me
Authorization: Bearer <token>
```

## 实现原理

### 1. Token生成
```python
def create_access_token(data: dict, session_id: str = None):
    to_encode = data.copy()
    to_encode.update({
        "session_id": session_id,
        "jti": str(uuid.uuid4()),  # JWT ID
        "iat": datetime.utcnow(),   # 签发时间
        "exp": expire_time          # 过期时间
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 2. Token验证
```python
async def get_current_user(credentials, db):
    token = credentials.credentials
    payload = verify_token(token)
    user = get_user_by_username(payload["sub"])
    
    # 关键：验证token是否为当前有效的session_token
    if user.session_token != token:
        raise HTTPException(401, "登录已失效，请重新登录")
    
    return user
```

### 3. 登录流程
```python
async def login(username, password, db):
    user = authenticate_user(username, password)
    
    # 生成新的session_id和token
    session_id = str(uuid.uuid4())
    access_token = create_access_token(
        data={"sub": user.username}, 
        session_id=session_id
    )
    
    # 更新用户的session_token（使之前的登录失效）
    user.session_token = access_token
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, ...}
```

## 部署步骤

### 1. 数据库迁移
```bash
cd /workspace/travel_route_planner
python migrations/add_session_token_to_user.py
```

### 2. 启动服务
```bash
python main.py
```

### 3. 运行测试
```bash
python test_single_session.py
```

## 测试场景

### 1. 基础单点登录测试
1. 用户A登录，获得token1
2. 使用token1访问受保护资源（成功）
3. 用户A再次登录，获得token2
4. 使用token1访问受保护资源（失败，token已失效）
5. 使用token2访问受保护资源（成功）

### 2. 并发登录测试
1. 同时发起多个登录请求
2. 验证只有一个token有效
3. 其他token应该失效

### 3. 登出测试
1. 用户登录获得token
2. 用户登出
3. 使用token访问受保护资源（失败）

## 安全考虑

### 1. Token安全
- 使用强随机密钥
- 设置合理的过期时间
- 包含JWT ID防止重放攻击

### 2. 会话管理
- 服务端存储当前有效token
- 登出时立即清除session_token
- 支持强制登出功能

### 3. 并发控制
- 数据库事务确保原子性
- 避免竞态条件

## 配置选项

在`config/settings.py`中可以配置：

```python
# JWT配置
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 安全配置
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5分钟
```

## 故障排除

### 1. Token验证失败
- 检查SECRET_KEY是否一致
- 验证token格式是否正确
- 确认session_token是否匹配

### 2. 数据库连接问题
- 检查数据库连接配置
- 确认迁移脚本是否执行成功
- 验证表结构是否正确

### 3. 并发问题
- 检查数据库事务隔离级别
- 确认索引是否创建
- 验证锁机制是否正常

## 扩展功能

### 1. 多设备管理
- 记录登录设备信息
- 支持设备白名单
- 设备管理界面

### 2. 会话监控
- 实时会话状态
- 异常登录检测
- 登录日志记录

### 3. 高级安全
- 地理位置验证
- 设备指纹识别
- 风险评分系统