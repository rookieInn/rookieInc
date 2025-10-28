# AOP操作日志记录系统

基于切面技术（AOP）的后台管理操作日志记录系统，提供完整的操作审计和监控功能。

## 功能特性

### 🎯 核心功能
- **AOP装饰器**：使用装饰器模式自动记录操作日志
- **多种操作类型**：支持创建、更新、删除、查询、登录、登出等操作
- **灵活存储**：支持文件、SQLite、MongoDB等多种存储方式
- **Web管理界面**：提供直观的日志查看和管理界面
- **统计分析**：提供操作统计、性能分析、错误分析等功能
- **导出功能**：支持JSON、CSV格式的日志导出

### 🔧 技术特性
- **非侵入式**：通过装饰器实现，不影响业务逻辑
- **高性能**：支持批量记录和异步处理
- **可配置**：丰富的配置选项，适应不同场景
- **可扩展**：模块化设计，易于扩展新功能

## 系统架构

```
AOP操作日志系统
├── 核心模块
│   ├── aop_operation_logger.py      # AOP装饰器和日志记录器
│   ├── operation_log_models.py      # 数据模型和数据库管理
│   └── operation_log_service.py     # 业务逻辑服务层
├── Web界面
│   ├── operation_log_web.py         # 操作日志Web管理界面
│   └── enhanced_tracking_api.py     # 增强的API服务
├── 演示系统
│   └── demo_admin_system.py         # 演示后台管理系统
├── 配置文件
│   └── config_operation_log.ini     # 系统配置文件
└── 测试
    └── test_operation_logging.py    # 测试用例
```

## 快速开始

### 1. 安装依赖

```bash
pip install flask flask-cors pymongo sqlite3
```

### 2. 配置系统

复制配置文件并修改设置：

```bash
cp config_operation_log.ini config.ini
```

编辑 `config.ini` 文件，配置数据库连接等参数。

### 3. 基本使用

#### 使用装饰器记录操作日志

```python
from aop_operation_logger import operation_log, log_create, log_update, log_delete, log_read

# 使用通用装饰器
@operation_log(
    operation_type=OperationType.CREATE,
    operation_name="用户创建",
    description="创建新用户"
)
def create_user(username, email):
    # 业务逻辑
    return {"user_id": "001", "username": username}

# 使用便捷装饰器
@log_create("用户创建", "创建新用户")
def create_user(username, email):
    return {"user_id": "001", "username": username}

@log_update("用户更新", "更新用户信息")
def update_user(user_id, **kwargs):
    return {"user_id": user_id, "updated": True}

@log_delete("用户删除", "删除用户")
def delete_user(user_id):
    return {"deleted": True}

@log_read("用户查询", "查询用户信息")
def get_user(user_id):
    return {"user_id": user_id, "username": "test"}
```

#### 手动记录操作日志

```python
from aop_operation_logger import log_operation_manually, OperationType, OperationStatus

# 手动记录操作日志
log_operation_manually(
    operation_type=OperationType.CUSTOM,
    operation_name="自定义操作",
    description="执行自定义业务操作",
    user_id="user_001",
    username="test_user",
    status=OperationStatus.SUCCESS,
    extra_data={"custom_field": "value"}
)
```

### 4. 启动服务

#### 启动操作日志Web管理界面

```bash
python operation_log_web.py --host 0.0.0.0 --port 5001
```

访问：http://localhost:5001/operation-logs/dashboard

#### 启动演示管理系统

```bash
python demo_admin_system.py --host 0.0.0.0 --port 5002
```

访问：http://localhost:5002

演示账号：
- 管理员：admin / admin123
- 普通用户：user1 / user123

#### 启动增强的API服务

```bash
python enhanced_tracking_api.py --host 0.0.0.0 --port 5000
```

## 配置说明

### 操作日志配置

```ini
[operation_log]
# 是否启用操作日志记录
enabled = true

# 存储类型: file, sqlite, mongodb
storage_type = sqlite

# SQLite数据库路径
db_path = data/operation_logs.db

# 日志保留天数
retention_days = 30

# 是否记录请求参数
include_params = true

# 是否记录响应数据
include_response = true

# 是否记录请求信息
include_request_info = true
```

### 数据库配置

```ini
# SQLite配置
[operation_log]
db_type = sqlite
db_path = data/operation_logs.db

# MongoDB配置
[operation_log]
db_type = mongodb
mongodb_host = localhost
mongodb_port = 27017
mongodb_database = operation_logs
mongodb_collection = logs
```

## API接口

### 操作日志管理API

#### 获取操作日志列表

```http
GET /api/operation-logs?page=1&limit=20&operation_type=create&status=success
```

参数：
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `user_id`: 用户ID
- `operation_type`: 操作类型
- `status`: 操作状态
- `start_date`: 开始日期
- `end_date`: 结束日期

#### 获取操作日志统计

```http
GET /api/operation-logs/statistics?days=30
```

参数：
- `days`: 统计天数（默认30）

#### 导出操作日志

```http
POST /api/operation-logs/export
Content-Type: application/json

{
    "days": 30,
    "format": "json"
}
```

#### 清理旧日志

```http
POST /api/operation-logs/cleanup
Content-Type: application/json

{
    "days": 30
}
```

## 装饰器说明

### 操作类型装饰器

| 装饰器 | 操作类型 | 说明 |
|--------|----------|------|
| `@log_create` | CREATE | 记录创建操作 |
| `@log_update` | UPDATE | 记录更新操作 |
| `@log_delete` | DELETE | 记录删除操作 |
| `@log_read` | READ | 记录查询操作 |
| `@log_login` | LOGIN | 记录登录操作 |
| `@log_logout` | LOGOUT | 记录登出操作 |
| `@log_system` | SYSTEM | 记录系统操作 |
| `@log_config` | CONFIG | 记录配置操作 |

### 通用装饰器

```python
@operation_log(
    operation_type=OperationType.CREATE,
    operation_name="操作名称",
    description="操作描述",
    module_name="模块名称",
    include_params=True,
    include_response=True,
    include_request_info=True
)
def your_function():
    # 业务逻辑
    pass
```

## 数据模型

### 操作日志模型

```python
@dataclass
class OperationLog:
    log_id: str                    # 日志ID
    user_id: Optional[str]         # 用户ID
    username: Optional[str]        # 用户名
    operation_type: str            # 操作类型
    operation_name: str            # 操作名称
    module_name: str               # 模块名称
    function_name: str             # 函数名称
    description: str               # 操作描述
    request_method: Optional[str]  # 请求方法
    request_url: Optional[str]     # 请求URL
    request_params: Optional[Dict] # 请求参数
    request_body: Optional[Dict]   # 请求体
    response_data: Optional[Dict]  # 响应数据
    status: str                    # 操作状态
    error_message: Optional[str]   # 错误信息
    ip_address: Optional[str]      # IP地址
    user_agent: Optional[str]      # 用户代理
    execution_time: float          # 执行时间（毫秒）
    timestamp: datetime            # 时间戳
    extra_data: Optional[Dict]     # 额外数据
```

## 性能优化

### 批量记录

```python
# 批量记录操作日志
logs = []
for i in range(100):
    log = OperationLog(...)
    logs.append(log)

# 批量插入
for log in logs:
    operation_log_service.log_operation(log)
```

### 异步记录

```python
# 配置异步记录
[operation_log]
async_logging = true
batch_size = 100
```

### 性能监控

```python
# 启用性能监控
[operation_log]
performance_monitoring = true
slow_query_threshold = 1000  # 慢查询阈值（毫秒）
```

## 测试

### 运行测试用例

```bash
python test_operation_logging.py
```

### 性能测试

测试用例包含性能测试，会测试：
- 大量日志记录性能
- 查询性能
- 统计性能

## 部署建议

### 生产环境配置

1. **数据库选择**：生产环境建议使用MongoDB或PostgreSQL
2. **日志轮转**：配置日志文件轮转，避免文件过大
3. **监控告警**：设置错误率监控和告警
4. **备份策略**：定期备份操作日志数据

### 安全考虑

1. **敏感信息**：避免记录密码等敏感信息
2. **访问控制**：限制操作日志的访问权限
3. **数据加密**：对敏感操作日志进行加密存储

## 扩展开发

### 添加新的操作类型

```python
# 在 aop_operation_logger.py 中添加新的操作类型
class OperationType(Enum):
    # 现有类型...
    CUSTOM_OPERATION = "custom_operation"

# 创建对应的装饰器
def log_custom_operation(operation_name: str, description: str = ""):
    return operation_log(OperationType.CUSTOM_OPERATION, operation_name, description)
```

### 自定义存储后端

```python
# 继承 OperationLogDatabase 类
class CustomOperationLogDatabase(OperationLogDatabase):
    def _init_custom_storage(self):
        # 实现自定义存储逻辑
        pass
    
    def insert_log(self, log_data: Dict[str, Any]) -> bool:
        # 实现自定义插入逻辑
        pass
```

## 常见问题

### Q: 如何避免记录敏感信息？

A: 在装饰器中设置 `include_params=False` 和 `include_response=False`，或者在业务逻辑中过滤敏感字段。

### Q: 如何提高记录性能？

A: 1. 使用批量记录；2. 启用异步记录；3. 选择合适的存储后端；4. 定期清理旧日志。

### Q: 如何自定义日志格式？

A: 继承 `OperationLog` 类并重写 `to_dict` 方法，或者自定义存储后端的序列化逻辑。

### Q: 如何处理高并发场景？

A: 1. 使用消息队列进行异步处理；2. 使用数据库连接池；3. 考虑使用Redis等缓存存储。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的AOP操作日志记录
- 提供Web管理界面
- 支持多种存储后端
- 完整的测试用例