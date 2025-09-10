# OSS存储监控系统 - 完整解决方案

## 系统概述

这是一个完整的阿里云OSS桶每日新增存储监控系统，提供以下核心功能：

- 📊 **每日存储量统计** - 自动监控OSS桶的存储使用情况
- 📈 **存储趋势分析** - 生成详细的存储增长趋势报告
- 🖥️ **Web仪表板** - 提供直观的可视化界面
- ⏰ **定时任务调度** - 支持自动化的监控和报告生成
- 📋 **报告生成** - 自动生成文本和图表报告
- 🗄️ **数据持久化** - 使用SQLite存储历史监控数据
- 🔔 **告警系统** - 支持存储量阈值告警

## 文件结构

```
/workspace/
├── oss_storage_monitor.py      # 主监控程序
├── oss_monitor_dashboard.py    # Web仪表板
├── oss_monitor_scheduler.py    # 定时调度器
├── oss_monitor_config.json     # 配置文件模板
├── test_oss_monitor.py         # 测试脚本
├── demo_oss_monitor.py         # 演示脚本
├── install_oss_monitor.sh      # 安装脚本
├── requirements.txt            # Python依赖
└── OSS_MONITOR_README.md       # 详细使用说明
```

## 快速开始

### 1. 安装系统

```bash
# 运行安装脚本
./install_oss_monitor.sh

# 或者手动安装依赖
pip3 install -r requirements.txt
```

### 2. 配置OSS桶信息

编辑 `oss_monitor_config.json` 文件：

```json
{
    "buckets": [
        {
            "name": "your-bucket-name",
            "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "your-access-key-id",
            "access_key_secret": "your-access-key-secret",
            "description": "主存储桶"
        }
    ]
}
```

### 3. 运行测试

```bash
# 运行功能测试
python3 test_oss_monitor.py

# 运行演示
python3 demo_oss_monitor.py
```

### 4. 启动监控系统

```bash
# 启动完整系统
./start_monitor.sh

# 或者分别启动
python3 oss_monitor_dashboard.py    # Web仪表板
python3 oss_monitor_scheduler.py    # 定时调度器
```

### 5. 访问Web界面

打开浏览器访问: http://localhost:5000

## 主要功能详解

### 1. 存储监控 (`oss_storage_monitor.py`)

**核心功能：**
- 连接OSS桶获取存储信息
- 计算每日新增存储量
- 生成存储趋势报告
- 数据清理和维护

**使用方法：**
```bash
# 检查所有桶
python3 oss_storage_monitor.py --check

# 生成报告
python3 oss_storage_monitor.py --report --days 30

# 清理旧数据
python3 oss_storage_monitor.py --cleanup
```

### 2. Web仪表板 (`oss_monitor_dashboard.py`)

**核心功能：**
- 实时存储状态显示
- 交互式图表展示
- 多桶对比分析
- 一键报告生成

**特性：**
- 响应式设计，支持移动端
- 实时数据更新
- 美观的图表展示
- 直观的操作界面

### 3. 定时调度器 (`oss_monitor_scheduler.py`)

**核心功能：**
- 自动存储检查
- 定期报告生成
- 数据清理任务
- 告警通知

**调度配置：**
```json
{
    "scheduler": {
        "check_interval": "daily",
        "check_time": "02:00",
        "report_interval": "weekly",
        "cleanup_interval": "monthly"
    }
}
```

## 配置说明

### 监控配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `check_interval_hours` | 检查间隔（小时） | 24 |
| `retention_days` | 数据保留天数 | 365 |
| `alert_threshold_gb` | 告警阈值（GB） | 1000 |
| `enable_daily_reports` | 启用每日报告 | true |

### 调度配置

| 参数 | 说明 | 选项 |
|------|------|------|
| `check_interval` | 检查频率 | daily/hourly/weekly |
| `check_time` | 检查时间 | HH:MM格式 |
| `report_interval` | 报告频率 | daily/weekly/monthly |
| `cleanup_interval` | 清理频率 | daily/weekly/monthly |

## 使用场景

### 1. 企业存储监控

- 监控多个OSS桶的存储使用情况
- 生成定期的存储报告
- 设置存储量告警阈值
- 分析存储增长趋势

### 2. 成本控制

- 跟踪存储成本变化
- 识别存储增长异常
- 优化存储策略
- 预算规划支持

### 3. 运维管理

- 自动化监控任务
- 历史数据追踪
- 故障预警
- 性能分析

## 高级功能

### 1. 多桶监控

支持同时监控多个OSS桶，每个桶可以有不同的配置：

```json
{
    "buckets": [
        {
            "name": "production-bucket",
            "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
            "access_key_id": "prod-key",
            "access_key_secret": "prod-secret",
            "description": "生产环境存储桶"
        },
        {
            "name": "backup-bucket",
            "endpoint": "https://oss-cn-beijing.aliyuncs.com",
            "access_key_id": "backup-key",
            "access_key_secret": "backup-secret",
            "description": "备份存储桶"
        }
    ]
}
```

### 2. 自定义报告

支持生成多种格式的报告：

- 文本报告（.txt）
- 图表报告（.png）
- 按桶分类报告
- 时间范围自定义

### 3. 告警系统

- 存储量阈值告警
- 增长异常检测
- Webhook通知支持
- 自定义告警规则

### 4. 数据导出

- SQLite数据库存储
- 支持数据查询和分析
- 历史数据备份
- 数据清理策略

## 部署选项

### 1. 单机部署

```bash
# 直接运行
python3 oss_monitor_dashboard.py
python3 oss_monitor_scheduler.py
```

### 2. 系统服务部署

```bash
# 创建systemd服务
sudo ./install_oss_monitor.sh

# 启用服务
sudo systemctl enable oss-monitor
sudo systemctl start oss-monitor
```

### 3. Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "oss_monitor_dashboard.py"]
```

## 监控指标

### 1. 存储指标

- 总存储量（GB）
- 对象数量
- 每日新增存储量
- 存储增长率

### 2. 趋势指标

- 存储量趋势
- 增长速率
- 峰值检测
- 异常分析

### 3. 成本指标

- 存储成本估算
- 增长成本预测
- 优化建议

## 故障排除

### 1. 常见问题

**问题：无法连接OSS**
- 检查访问密钥是否正确
- 确认网络连接正常
- 验证桶权限设置

**问题：数据库错误**
- 检查文件权限
- 确认磁盘空间充足
- 验证数据库文件完整性

**问题：图表生成失败**
- 安装matplotlib依赖
- 检查字体配置
- 确认数据完整性

### 2. 日志查看

```bash
# 查看监控日志
tail -f oss_monitor.log

# 查看调度器日志
tail -f oss_monitor_scheduler.log

# 查看系统日志
journalctl -u oss-monitor
```

### 3. 性能优化

- 调整检查频率
- 优化数据库查询
- 使用SSD存储
- 配置合适的保留期

## 安全建议

### 1. 访问控制

- 使用IAM子账号
- 限制访问权限
- 定期轮换密钥
- 监控访问日志

### 2. 数据保护

- 加密敏感配置
- 备份重要数据
- 限制文件权限
- 网络安全隔离

### 3. 监控安全

- 设置访问日志
- 监控异常活动
- 定期安全审计
- 及时更新依赖

## 扩展功能

### 1. 通知集成

- 钉钉机器人
- 企业微信
- 邮件通知
- 短信告警

### 2. 数据集成

- 导出到Excel
- 集成到Grafana
- 推送到InfluxDB
- 对接监控平台

### 3. 高级分析

- 机器学习预测
- 异常检测算法
- 成本优化建议
- 容量规划

## 总结

这个OSS存储监控系统提供了完整的存储监控解决方案，具有以下优势：

✅ **功能完整** - 涵盖监控、分析、报告、告警等全流程
✅ **易于使用** - 提供Web界面和命令行工具
✅ **高度可配置** - 支持多种配置选项和自定义
✅ **扩展性强** - 模块化设计，易于扩展新功能
✅ **生产就绪** - 包含完整的错误处理和日志记录
✅ **文档完善** - 提供详细的使用说明和示例

通过这个系统，您可以：
- 实时监控OSS存储使用情况
- 分析存储增长趋势
- 生成专业的监控报告
- 设置智能告警机制
- 优化存储成本和管理效率

立即开始使用，让您的OSS存储管理更加智能和高效！