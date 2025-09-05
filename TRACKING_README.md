# 页面埋点统计系统

一个完整的页面埋点解决方案，用于统计用户行为数据并存储到MongoDB。包含前端JavaScript SDK、后端API服务、数据分析和可视化功能。

## 🌟 功能特性

- **前端埋点SDK**: 自动收集用户行为数据（点击、滚动、页面访问等）
- **后端API服务**: RESTful API接收和存储埋点数据
- **MongoDB存储**: 高效存储和查询用户行为数据
- **数据分析**: 用户行为分析、漏斗分析、留存分析
- **可视化报告**: 自动生成图表和统计报告
- **实时统计**: 实时监控用户活跃度
- **批量处理**: 支持批量发送和定时刷新
- **配置灵活**: 支持多种配置选项

## 📁 项目结构

```
├── tracking_models.py          # 数据模型和MongoDB连接
├── tracking_api.py             # Flask API服务
├── tracking_analytics.py       # 数据分析和统计
├── tracking_sdk.js             # 前端JavaScript SDK
├── tracking_example.py         # 使用示例
├── config.ini                  # 配置文件
├── requirements.txt            # Python依赖
└── TRACKING_README.md         # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置MongoDB

编辑 `config.ini` 文件，配置MongoDB连接信息：

```ini
[mongodb]
host = localhost
port = 27017
username = 
password = 
database = tracking
timeout = 30
```

### 3. 启动API服务

```bash
python tracking_api.py
```

API服务将在 `http://localhost:5000` 启动。

### 4. 前端集成

在HTML页面中引入SDK：

```html
<!DOCTYPE html>
<html>
<head>
    <title>我的网站</title>
</head>
<body>
    <!-- 你的页面内容 -->
    
    <!-- 引入埋点SDK -->
    <script src="tracking_sdk.js"></script>
    <script>
        // 初始化埋点
        initTracking({
            apiUrl: 'http://localhost:5000/api',
            userId: 'user_123',  // 可选
            debug: true
        });
    </script>
</body>
</html>
```

## 📊 数据模型

### 用户事件 (UserEvent)

```python
{
    "event_id": "唯一事件ID",
    "user_id": "用户ID",
    "session_id": "会话ID", 
    "event_type": "事件类型",  # page_view, click, scroll, form_submit等
    "page_url": "页面URL",
    "page_title": "页面标题",
    "element_id": "元素ID",
    "element_class": "元素class",
    "element_text": "元素文本",
    "x_position": "鼠标X坐标",
    "y_position": "鼠标Y坐标",
    "scroll_depth": "滚动深度百分比",
    "referrer": "来源页面",
    "user_agent": "用户代理",
    "screen_resolution": "屏幕分辨率",
    "viewport_size": "视口大小",
    "timestamp": "时间戳",
    "custom_data": "自定义数据",
    "duration": "事件持续时间"
}
```

### 页面访问 (PageView)

```python
{
    "page_id": "页面访问ID",
    "user_id": "用户ID",
    "session_id": "会话ID",
    "page_url": "页面URL",
    "page_title": "页面标题",
    "referrer": "来源页面",
    "user_agent": "用户代理",
    "screen_resolution": "屏幕分辨率",
    "viewport_size": "视口大小",
    "load_time": "页面加载时间",
    "timestamp": "访问时间",
    "exit_timestamp": "离开时间",
    "duration": "页面停留时间"
}
```

## 🔧 API接口

### 健康检查

```http
GET /api/health
```

### 发送事件

```http
POST /api/track/event
Content-Type: application/json

{
    "user_id": "user_123",
    "session_id": "session_456",
    "event_type": "click",
    "page_url": "https://example.com/page",
    "page_title": "页面标题",
    "element_id": "button_1",
    "custom_data": {
        "action": "button_click"
    }
}
```

### 发送页面访问

```http
POST /api/track/pageview
Content-Type: application/json

{
    "user_id": "user_123",
    "session_id": "session_456",
    "page_url": "https://example.com/page",
    "page_title": "页面标题",
    "load_time": 1.5
}
```

### 批量发送事件

```http
POST /api/track/batch
Content-Type: application/json

{
    "events": [
        {
            "event_type": "click",
            "page_url": "https://example.com/page1"
        },
        {
            "event_type": "scroll",
            "page_url": "https://example.com/page2"
        }
    ]
}
```

### 获取事件统计

```http
GET /api/stats/events?days=7
```

### 获取页面统计

```http
GET /api/stats/pages?days=7
```

## 📈 数据分析

### 用户行为摘要

```python
from tracking_analytics import TrackingAnalytics
from tracking_models import TrackingDatabase

# 初始化
db = TrackingDatabase()
analytics = TrackingAnalytics(db)

# 获取7天用户行为摘要
summary = analytics.get_user_behavior_summary(days=7)
print(f"总事件数: {summary['overview']['total_events']}")
print(f"活跃用户: {summary['overview']['active_users']}")
```

### 漏斗分析

```python
# 定义漏斗步骤
funnel_steps = ['page_view', 'click', 'form_submit', 'purchase']

# 获取漏斗分析
funnel = analytics.get_funnel_analysis(funnel_steps, days=7)
for step in funnel['funnel_steps']:
    print(f"{step['step']}: {step['users']} 用户 (转化率: {step['conversion_rate']:.1f}%)")
```

### 留存分析

```python
# 获取30天留存分析
retention = analytics.get_retention_analysis(days=30)
for day_data in retention['retention_data']:
    print(f"第{day_data['day']}天留存率: {day_data['retention_rate']:.1f}%")
```

### 生成可视化报告

```python
# 生成7天可视化报告
report_path = analytics.generate_visualization_report(days=7)
print(f"报告已生成: {report_path}")
```

## 🎯 前端SDK使用

### 基本用法

```javascript
// 初始化
initTracking({
    apiUrl: 'http://localhost:5000/api',
    userId: 'user_123',
    debug: true
});

// 手动跟踪事件
getTracking().trackEvent('custom_event', {
    custom_data: { action: 'button_click' }
});

// 跟踪页面访问
getTracking().trackPageView({
    custom_data: { source: 'homepage' }
});
```

### 高级配置

```javascript
initTracking({
    apiUrl: 'http://localhost:5000/api',
    apiKey: 'your_api_key',
    userId: 'user_123',
    sessionId: 'custom_session_id',
    debug: false,
    autoTrack: true,           // 自动跟踪
    batchSize: 20,            // 批量大小
    flushInterval: 10000      // 刷新间隔(毫秒)
});
```

### 手动控制

```javascript
const tracking = getTracking();

// 设置用户ID
tracking.setUserId('new_user_id');

// 获取会话ID
const sessionId = tracking.getSessionId();

// 强制发送所有待发送事件
tracking.forceFlush();

// 获取队列长度
const queueLength = tracking.getQueueLength();
```

## 📊 监控和运维

### 实时监控

```python
# 获取实时统计
realtime = analytics.get_real_time_stats()
print(f"最近1小时事件: {realtime['recent_events_1h']}")
print(f"当前在线用户: {realtime['online_users']}")
```

### 数据导出

```python
# 导出数据到CSV
exported_files = analytics.export_data_to_csv(days=7)
print(f"数据已导出: {exported_files}")
```

### 健康检查

```bash
curl http://localhost:5000/api/health
```

## 🔒 安全配置

### API密钥验证

在 `config.ini` 中设置API密钥：

```ini
[tracking_api]
api_key = your_secret_api_key
```

前端请求时添加密钥：

```javascript
initTracking({
    apiUrl: 'http://localhost:5000/api',
    apiKey: 'your_secret_api_key'
});
```

### CORS配置

```ini
[tracking_api]
enable_cors = true
```

## 🚀 部署建议

### 生产环境配置

1. **MongoDB集群**: 使用MongoDB副本集或分片集群
2. **API负载均衡**: 使用Nginx或HAProxy进行负载均衡
3. **监控告警**: 集成Prometheus + Grafana监控
4. **日志管理**: 使用ELK Stack进行日志分析
5. **数据备份**: 定期备份MongoDB数据

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "tracking_api.py"]
```

## 📝 示例和测试

运行完整示例：

```bash
python tracking_example.py
```

这将演示：
- 模拟用户行为数据
- 数据分析功能
- API使用说明
- 前端集成说明

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交Issue或联系开发团队。