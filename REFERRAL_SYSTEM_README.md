# 分享返佣裂变系统

一个完整的分享返佣裂变流程系统，支持多级返佣、实时追踪、数据分析和可视化看板。

## 🚀 功能特性

### 核心功能
- **用户管理**: 用户注册、邀请码生成、层级关系管理
- **分享链接**: 短链接生成、点击追踪、过期管理
- **返佣计算**: 多级返佣（最多3级）、自动结算、状态管理
- **数据追踪**: 实时统计、行为分析、转化漏斗
- **可视化看板**: 数据图表、实时监控、报表生成

### 技术特性
- **RESTful API**: 完整的API接口设计
- **数据库支持**: SQLite数据库，支持数据持久化
- **实时分析**: 用户行为追踪和转化分析
- **可视化**: 基于Chart.js的数据可视化
- **响应式设计**: 支持多设备访问

## 📁 项目结构

```
referral_system/
├── referral_system.py          # 核心系统类
├── referral_api.py             # Flask API接口
├── tracking_analytics.py       # 追踪分析模块
├── templates/
│   └── dashboard.html          # 数据看板界面
├── referral_system.db          # SQLite数据库
├── requirements.txt            # 依赖包列表
└── REFERRAL_SYSTEM_README.md   # 系统文档
```

## 🛠️ 安装配置

### 环境要求
- Python 3.7+
- SQLite 3
- 现代浏览器（支持ES6）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd referral_system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
# 启动API服务
python referral_api.py

# 运行分析演示
python tracking_analytics.py
```

4. **访问系统**
- 数据看板: http://localhost:5000
- API文档: http://localhost:5000/api/analytics

## 📊 系统架构

### 数据库设计

#### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | TEXT | 用户唯一ID |
| username | TEXT | 用户名 |
| email | TEXT | 邮箱地址 |
| phone | TEXT | 手机号 |
| invite_code | TEXT | 邀请码 |
| referrer_id | TEXT | 推荐人ID |
| level | INTEGER | 用户层级 |
| total_commission | REAL | 总返佣金额 |
| created_at | TIMESTAMP | 创建时间 |
| is_active | BOOLEAN | 是否激活 |

#### 分享链接表 (referral_links)
| 字段 | 类型 | 说明 |
|------|------|------|
| link_id | TEXT | 链接唯一ID |
| user_id | TEXT | 创建用户ID |
| original_url | TEXT | 原始URL |
| short_code | TEXT | 短链接代码 |
| click_count | INTEGER | 点击次数 |
| conversion_count | INTEGER | 转化次数 |
| created_at | TIMESTAMP | 创建时间 |
| expires_at | TIMESTAMP | 过期时间 |

#### 返佣记录表 (commissions)
| 字段 | 类型 | 说明 |
|------|------|------|
| commission_id | TEXT | 返佣唯一ID |
| user_id | TEXT | 被推荐用户ID |
| referrer_id | TEXT | 推荐人ID |
| amount | REAL | 返佣金额 |
| commission_type | TEXT | 返佣类型 |
| order_id | TEXT | 订单ID |
| status | TEXT | 返佣状态 |
| created_at | TIMESTAMP | 创建时间 |

### 返佣规则

| 层级 | 返佣比例 | 说明 |
|------|----------|------|
| 1级 | 10% | 直接推荐 |
| 2级 | 5% | 间接推荐 |
| 3级 | 2% | 三级推荐 |

## 🔌 API接口文档

### 用户管理

#### 用户注册
```http
POST /api/register
Content-Type: application/json

{
    "username": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "referrer_code": "ABC12345"  // 可选
}
```

**响应:**
```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user_id": "uuid",
        "username": "张三",
        "invite_code": "ABC12345",
        "level": 1
    }
}
```

#### 获取用户信息
```http
GET /api/user/{user_id}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "user_info": {
            "username": "张三",
            "total_commission": 100.50,
            "level": 1,
            "created_at": "2024-01-01 12:00:00"
        },
        "link_stats": {
            "total_links": 5,
            "total_clicks": 100,
            "total_conversions": 10
        },
        "commission_stats": {
            "total_commissions": 3,
            "total_amount": 100.50
        }
    }
}
```

### 分享链接管理

#### 创建分享链接
```http
POST /api/link/create
Content-Type: application/json

{
    "user_id": "uuid",
    "original_url": "https://example.com/product/123",
    "expires_days": 30
}
```

**响应:**
```json
{
    "success": true,
    "message": "分享链接创建成功",
    "data": {
        "link_id": "uuid",
        "short_code": "abc123",
        "original_url": "https://example.com/product/123",
        "short_url": "https://your-domain.com/r/abc123",
        "expires_at": "2024-02-01T12:00:00"
    }
}
```

#### 追踪链接点击
```http
GET /api/link/{short_code}/click
```

**响应:**
```json
{
    "success": true,
    "data": {
        "original_url": "https://example.com/product/123",
        "redirect": true
    }
}
```

### 转化处理

#### 处理转化
```http
POST /api/conversion
Content-Type: application/json

{
    "user_id": "uuid",
    "order_id": "ORDER_001",
    "amount": 1000.00
}
```

**响应:**
```json
{
    "success": true,
    "message": "转化处理成功",
    "data": {
        "commissions": [
            {
                "commission_id": "uuid",
                "referrer_id": "uuid",
                "amount": 100.00,
                "type": "direct",
                "status": "pending"
            }
        ]
    }
}
```

### 数据分析

#### 获取系统分析
```http
GET /api/analytics
```

**响应:**
```json
{
    "success": true,
    "data": {
        "users": {
            "total": 1000,
            "new_30d": 100
        },
        "links": {
            "total": 500,
            "total_clicks": 5000,
            "total_conversions": 200,
            "conversion_rate": 0.04
        },
        "commissions": {
            "total_amount": 10000.00
        }
    }
}
```

## 📈 使用示例

### 1. 基本使用流程

```python
from referral_system import ReferralSystem

# 初始化系统
system = ReferralSystem()

# 1. 用户注册
user1 = system.register_user("张三", "zhangsan@example.com", "13800138000")
print(f"用户注册成功: {user1.username}, 邀请码: {user1.invite_code}")

# 2. 通过邀请码注册
user2 = system.register_user("李四", "lisi@example.com", "13800138001", user1.invite_code)

# 3. 创建分享链接
link = system.create_referral_link(user1.user_id, "https://example.com/product/123")

# 4. 模拟点击
original_url = system.track_click(link.short_code, "192.168.1.1", "Mozilla/5.0")

# 5. 处理转化
commissions = system.process_conversion(user2.user_id, "ORDER_001", 1000.0)
for comm in commissions:
    print(f"返佣: {comm.referrer_id} -> {comm.amount:.2f}元")
```

### 2. 数据分析示例

```python
from tracking_analytics import TrackingAnalytics

# 初始化分析器
analytics = TrackingAnalytics()

# 生成分析报告
report = analytics.generate_analytics_report(days=30, output_file="report.md")

# 创建可视化图表
analytics.create_visualization_charts(days=30, output_dir="charts")

# 获取实时指标
metrics = analytics.get_real_time_metrics()
print(f"今日注册: {metrics['today_registrations']}人")
print(f"今日转化: {metrics['today_conversions']}次")
```

### 3. Web界面使用

1. 启动API服务: `python referral_api.py`
2. 访问数据看板: http://localhost:5000
3. 在界面中完成用户注册、链接创建、转化处理等操作

## 🔧 配置说明

### 返佣比例配置

在 `referral_system.py` 中修改返佣比例:

```python
self.commission_rates = {
    1: 0.10,  # 一级返佣 10%
    2: 0.05,  # 二级返佣 5%
    3: 0.02   # 三级返佣 2%
}
```

### 数据库配置

系统默认使用SQLite数据库，如需使用其他数据库，请修改连接配置。

### API配置

在 `referral_api.py` 中修改服务配置:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📊 监控指标

### 关键指标
- **用户增长**: 注册用户数、活跃用户数
- **分享效果**: 分享链接数、点击次数、转化次数
- **返佣数据**: 返佣金额、返佣比例、返佣用户数
- **转化率**: 点击转化率、注册转化率、整体转化率

### 实时监控
- 今日注册用户数
- 今日点击量
- 今日转化数
- 今日返佣金额
- 1小时活跃用户数

## 🚀 部署建议

### 生产环境部署

1. **数据库升级**
   - 建议使用PostgreSQL或MySQL替代SQLite
   - 配置数据库连接池
   - 设置定期备份

2. **服务部署**
   - 使用Gunicorn + Nginx部署Flask应用
   - 配置负载均衡
   - 设置监控和日志

3. **缓存优化**
   - 使用Redis缓存热点数据
   - 配置CDN加速静态资源

4. **安全配置**
   - 配置HTTPS
   - 设置API限流
   - 添加用户认证

### 扩展功能

1. **消息通知**
   - 返佣到账通知
   - 转化成功通知
   - 系统状态通知

2. **高级分析**
   - 用户画像分析
   - 预测模型
   - A/B测试支持

3. **移动端支持**
   - 开发移动端APP
   - 微信小程序集成
   - 推送通知

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 微信群讨论

---

**分享返佣裂变系统** - 让分享更有价值！ 🚀