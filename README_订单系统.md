# 订单自动关闭系统

一个完整的订单管理系统，支持订单创建、状态管理、30分钟自动关闭、通知等功能。

## 功能特性

- ✅ **订单管理**: 创建、查询、更新、删除订单
- ✅ **自动过期**: 订单创建后30分钟自动关闭
- ✅ **状态管理**: 支持多种订单状态（待处理、已确认、处理中、已完成、已取消、已过期）
- ✅ **通知系统**: 支持邮件和Webhook通知
- ✅ **RESTful API**: 完整的API接口
- ✅ **数据持久化**: SQLite数据库存储
- ✅ **日志记录**: 完整的操作日志
- ✅ **统计分析**: 订单统计和分析功能

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_order.txt
```

### 2. 运行示例

```bash
# 运行基础示例
python order_example.py

# 运行完整测试
python test_order_system.py
```

### 3. 启动服务

```bash
# 启动API服务器
python start_order_system.py api

# 启动订单管理器
python start_order_system.py manager

# 同时启动API服务器和订单管理器
python start_order_system.py all
```

## 核心组件

### 1. 订单数据模型 (`order_models.py`)

- `Order`: 订单类，包含订单的所有信息
- `OrderStatus`: 订单状态枚举
- `OrderManager`: 订单管理器，负责数据库操作和自动过期检查

### 2. API接口 (`order_api.py`)

提供完整的RESTful API接口：

- `POST /api/orders` - 创建订单
- `GET /api/orders/<order_id>` - 获取订单详情
- `PUT /api/orders/<order_id>/status` - 更新订单状态
- `GET /api/orders/user/<user_id>` - 获取用户订单
- `GET /api/orders/statistics` - 获取订单统计
- `POST /api/orders/<order_id>/cancel` - 取消订单
- `POST /api/orders/<order_id>/confirm` - 确认订单

### 3. 通知系统 (`order_notifications.py`)

- 邮件通知
- Webhook通知
- 多种通知模板
- 状态变更自动通知

## 使用示例

### 创建订单

```python
from order_models import OrderManager

# 创建订单管理器
order_manager = OrderManager()

# 创建订单
order = order_manager.create_order(
    user_id="user_001",
    amount=99.99,
    items=[
        {"name": "商品A", "price": 49.99, "quantity": 1},
        {"name": "商品B", "price": 50.00, "quantity": 1}
    ],
    customer_info={
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000"
    },
    expiry_minutes=30  # 30分钟后自动关闭
)
```

### 使用API

```python
import requests

# 创建订单
order_data = {
    "user_id": "user_001",
    "amount": 199.99,
    "items": [{"name": "商品", "price": 199.99, "quantity": 1}],
    "customer_info": {"name": "张三", "email": "zhangsan@example.com"}
}

response = requests.post("http://localhost:5000/api/orders", json=order_data)
order = response.json()["order"]
print(f"订单创建成功: {order['order_id']}")
```

### 配置通知

```python
from order_notifications import NotificationConfig, OrderNotificationService

# 配置通知
config = NotificationConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",
    from_email="your-email@gmail.com",
    webhook_url="https://your-webhook-url.com/notifications"
)

# 创建带通知的订单服务
notification_service = OrderNotificationService(order_manager, config)
```

## 订单状态

| 状态 | 描述 |
|------|------|
| `pending` | 待处理 |
| `confirmed` | 已确认 |
| `processing` | 处理中 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |
| `expired` | 已过期（30分钟自动关闭） |

## 自动过期机制

- 订单创建后30分钟自动检查过期
- 每30秒检查一次过期订单
- 自动将过期订单状态更新为 `expired`
- 支持自定义过期时间

## 数据库结构

### orders 表
- `order_id`: 订单ID（主键）
- `user_id`: 用户ID
- `amount`: 订单金额
- `status`: 订单状态
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `expires_at`: 过期时间
- `items`: 订单商品（JSON）
- `customer_info`: 客户信息（JSON）

### order_logs 表
- `id`: 日志ID（主键）
- `order_id`: 订单ID
- `action`: 操作类型
- `old_status`: 原状态
- `new_status`: 新状态
- `message`: 操作说明
- `created_at`: 创建时间

## 配置说明

创建 `order_config.json` 配置文件：

```json
{
  "database": {
    "path": "orders.db"
  },
  "notifications": {
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_username": "your-email@gmail.com",
      "smtp_password": "your-app-password",
      "from_email": "your-email@gmail.com"
    },
    "webhook": {
      "url": "https://your-webhook-url.com/order-notifications"
    }
  },
  "api": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "order": {
    "default_expiry_minutes": 30,
    "expiry_check_interval": 30
  }
}
```

## 测试

运行测试套件：

```bash
python test_order_system.py
```

测试包括：
- 订单创建和查询
- 状态更新
- 自动过期
- API接口
- 通知系统
- 完整工作流程

## 部署

### 开发环境

```bash
python start_order_system.py all
```

### 生产环境

```bash
# 使用 gunicorn 部署API
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 order_api:app

# 后台运行订单管理器
nohup python -c "from order_models import OrderManager; OrderManager()" &
```

## 监控和日志

- 所有操作都有详细日志记录
- 支持订单统计和分析
- 健康检查接口：`GET /api/health`

## 扩展功能

- 支持多种支付方式
- 订单退款处理
- 库存管理
- 优惠券系统
- 订单导出
- 数据分析报表

## 注意事项

1. 确保数据库文件有写入权限
2. 配置正确的邮件服务器信息
3. 生产环境建议使用PostgreSQL或MySQL
4. 定期备份数据库
5. 监控系统资源使用情况

## 许可证

MIT License