# 电商优惠券系统

一个完整的电商优惠券管理系统，支持多种优惠券类型、高级验证规则、批量操作和实时统计。

## 功能特性

### 🎫 优惠券类型
- **固定金额减免** - 满X减Y
- **百分比折扣** - 打X折
- **免运费券** - 免费配送
- **买X送Y** - 买指定数量送商品
- **返现券** - 购买后返现

### 🔧 核心功能
- 优惠券创建、编辑、删除
- 用户领取和使用优惠券
- 实时验证和计算折扣
- 使用记录和统计
- 批量操作和模板管理

### 🛡️ 高级验证
- 时间限制（特定时间段、星期、日期）
- 用户限制（等级、注册时间、消费记录）
- 商品限制（必需商品、数量、价格）
- 分类限制（必需分类、数量）
- 金额限制（最低/最高订单金额）
- 频率限制（每日/每周使用次数）
- 组合限制（与其他优惠券的组合使用）

### 📊 管理功能
- 可视化后台管理界面
- 实时统计和报表
- 优惠券模板管理
- 批量创建和分配
- 定时任务和清理

### 🎨 用户界面
- 响应式优惠券展示
- 分类筛选和搜索
- 我的优惠券管理
- 优惠券详情查看

## 项目结构

```
coupon_system/
├── coupon_models.py          # 数据库模型
├── coupon_service.py         # 业务逻辑服务
├── coupon_api.py            # REST API接口
├── coupon_validator.py      # 高级验证逻辑
├── coupon_admin.html        # 管理后台界面
├── coupon_frontend.html     # 用户前端界面
├── requirements.txt         # 依赖包
└── README_coupon_system.md  # 说明文档
```

## 数据库设计

### 核心表结构

1. **coupons** - 优惠券主表
   - 基本信息：代码、名称、描述
   - 优惠规则：类型、折扣值、使用条件
   - 限制条件：数量、用户限制、时间限制
   - 适用范围：商品、分类、排除商品

2. **coupon_usages** - 使用记录表
   - 使用详情：用户、订单、折扣金额
   - 状态管理：使用状态、时间记录

3. **user_coupons** - 用户优惠券表
   - 用户领取的优惠券记录
   - 使用状态和时间管理

4. **coupon_rules** - 优惠券规则表
   - 复杂规则配置
   - 支持JSON格式的灵活配置

5. **coupon_templates** - 优惠券模板表
   - 优惠券模板管理
   - 批量创建支持

## API接口

### 优惠券管理
- `POST /api/coupons` - 创建优惠券
- `GET /api/coupons` - 获取优惠券列表
- `GET /api/coupons/{id}` - 获取优惠券详情
- `PUT /api/coupons/{id}` - 更新优惠券
- `DELETE /api/coupons/{id}` - 删除优惠券

### 优惠券使用
- `POST /api/coupons/validate` - 验证优惠券
- `POST /api/coupons/use` - 使用优惠券
- `POST /api/coupons/claim` - 领取优惠券
- `GET /api/users/{id}/coupons` - 获取用户优惠券
- `GET /api/coupons/available` - 获取可用优惠券

### 统计分析
- `GET /api/coupons/{id}/statistics` - 获取优惠券统计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```python
from coupon_api import init_database
init_database()
```

### 3. 启动服务

```bash
python coupon_api.py
```

### 4. 访问界面

- 管理后台：`http://localhost:5000/coupon_admin.html`
- 用户界面：`http://localhost:5000/coupon_frontend.html`
- API文档：`http://localhost:5000/api/coupons`

## 使用示例

### 创建优惠券

```python
from coupon_service import CouponService, CouponCreateRequest, CouponType
from decimal import Decimal

# 创建满减券
request = CouponCreateRequest(
    name="新用户专享",
    description="新用户首次购买立减20元",
    coupon_type=CouponType.FIXED_AMOUNT,
    discount_value=Decimal('20'),
    min_order_amount=Decimal('100'),
    total_quantity=1000,
    valid_days=30
)

coupon_service = CouponService(db_session)
coupon = coupon_service.create_coupon(request, created_by=1)
```

### 验证和使用优惠券

```python
# 验证优惠券
validation_result = coupon_service.validate_coupon(
    coupon_code="COUPON123456",
    user_id=1,
    order_amount=Decimal('150'),
    product_ids=[1, 2, 3]
)

if validation_result.is_valid:
    # 使用优惠券
    success, message, discount_amount = coupon_service.use_coupon(
        coupon_code="COUPON123456",
        user_id=1,
        order_id="ORDER123",
        order_amount=Decimal('150')
    )
```

### 高级验证规则

```python
from coupon_validator import AdvancedCouponValidator, ValidationContext

validator = AdvancedCouponValidator(db_session)

# 创建验证上下文
context = ValidationContext(
    user_id=1,
    order_amount=Decimal('200'),
    product_ids=[1, 2],
    category_ids=[1],
    order_time=datetime.now(),
    user_level="gold",
    user_total_orders=10,
    user_total_amount=Decimal('1000')
)

# 高级验证
result = await validator.validate_coupon_advanced("COUPON123456", context)
```

## 配置说明

### 环境变量

```bash
# 数据库配置
DATABASE_URL=sqlite:///coupon_system.db

# 应用配置
FLASK_ENV=development
FLASK_DEBUG=True
```

### 数据库配置

支持多种数据库：
- SQLite（开发环境）
- MySQL（生产环境）
- PostgreSQL（生产环境）

## 部署建议

### 生产环境

1. 使用Gunicorn作为WSGI服务器
2. 配置Nginx作为反向代理
3. 使用Redis作为缓存
4. 配置数据库连接池
5. 设置定时任务清理过期数据

### 性能优化

1. 数据库索引优化
2. 查询缓存
3. 分页加载
4. 异步处理
5. CDN加速静态资源

## 扩展功能

### 可扩展的特性

1. **积分系统集成** - 优惠券与积分系统联动
2. **推荐系统** - 基于用户行为的优惠券推荐
3. **A/B测试** - 优惠券效果测试
4. **实时通知** - 优惠券到期提醒
5. **数据分析** - 更详细的统计报表
6. **移动端支持** - 移动应用API
7. **多语言支持** - 国际化
8. **权限管理** - 细粒度权限控制

## 注意事项

1. **并发安全** - 使用数据库事务确保数据一致性
2. **性能监控** - 监控API响应时间和数据库性能
3. **安全防护** - 防止优惠券滥用和恶意攻击
4. **数据备份** - 定期备份重要数据
5. **日志记录** - 记录关键操作日志

## 技术支持

如有问题或建议，请提交Issue或联系开发团队。

---

**版本**: 1.0.0  
**更新时间**: 2024年  
**许可证**: MIT