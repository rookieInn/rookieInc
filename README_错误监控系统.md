# 系统错误监控和邮件通知系统

## 概述

这是一个自动化的系统错误监控解决方案，能够监控指定日志文件中的错误，当错误数量在指定时间窗口内超过预设阈值时，自动发送邮件通知给系统负责人。

## 功能特性

- 🔍 **多文件监控**: 支持监控多个日志文件
- ⚡ **实时检测**: 可配置的检查间隔，实时监控错误
- 📧 **邮件通知**: 支持HTML格式的邮件通知
- 🛡️ **智能过滤**: 可配置的错误模式匹配
- ⏰ **时间窗口**: 支持时间窗口内的错误统计
- 🔄 **防重复通知**: 支持冷却时间和频率限制
- 📊 **系统信息**: 包含系统状态信息
- 🚀 **系统服务**: 支持作为systemd服务运行

## 文件结构

```
/workspace/
├── error_log_monitor.py          # 主监控脚本
├── email_notifier.py             # 邮件发送工具
├── error_monitor_config.json     # 配置文件
├── error-monitor.service         # systemd服务文件
├── error_monitor_service.sh      # 服务管理脚本
├── install_error_monitor.sh      # 安装脚本
└── README_错误监控系统.md        # 使用说明
```

## 快速开始

### 1. 安装系统

```bash
# 使用root权限运行安装脚本
sudo ./install_error_monitor.sh
```

### 2. 配置邮件设置

编辑配置文件 `error_monitor_config.json`:

```json
{
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "from_email": "your_email@gmail.com",
        "to_emails": [
            "admin@yourcompany.com",
            "devops@yourcompany.com"
        ],
        "subject_prefix": "[系统错误监控]"
    }
}
```

### 3. 测试配置

```bash
# 测试邮件发送
./error_monitor_service.sh test-email

# 测试监控功能
./error_monitor_service.sh test-monitor
```

### 4. 启动服务

```bash
# 安装系统服务
./error_monitor_service.sh install

# 启动监控服务
./error_monitor_service.sh start

# 查看服务状态
./error_monitor_service.sh status
```

## 配置说明

### 监控配置

```json
{
    "monitor": {
        "log_file_paths": [           // 要监控的日志文件路径
            "/var/log/syslog",
            "/var/log/messages",
            "./bookmark_sync.log"
        ],
        "error_patterns": [           // 错误匹配模式
            "ERROR",
            "FATAL",
            "CRITICAL",
            "Exception",
            "Traceback"
        ],
        "time_window_minutes": 5,     // 时间窗口（分钟）
        "error_threshold": 10,        // 错误数量阈值
        "check_interval_seconds": 30  // 检查间隔（秒）
    }
}
```

### 邮件配置

```json
{
    "email": {
        "smtp_server": "smtp.gmail.com",    // SMTP服务器
        "smtp_port": 587,                   // SMTP端口
        "username": "your_email@gmail.com", // 发送邮箱
        "password": "your_app_password",    // 邮箱密码或应用密码
        "from_email": "your_email@gmail.com", // 发件人邮箱
        "to_emails": [                      // 收件人列表
            "admin@yourcompany.com"
        ],
        "subject_prefix": "[系统错误监控]"   // 邮件主题前缀
    }
}
```

### 通知配置

```json
{
    "notification": {
        "cooldown_minutes": 30,           // 通知冷却时间（分钟）
        "max_notifications_per_hour": 5,  // 每小时最大通知次数
        "include_error_details": true,    // 是否包含错误详情
        "include_system_info": true       // 是否包含系统信息
    }
}
```

## 使用方法

### 命令行使用

```bash
# 直接运行监控（前台）
python3 error_log_monitor.py --config error_monitor_config.json

# 测试模式（只运行一次检查）
python3 error_log_monitor.py --test

# 发送测试邮件
python3 email_notifier.py --test

# 发送自定义邮件
python3 email_notifier.py --subject "测试邮件" --content "这是测试内容" --to admin@example.com
```

### 服务管理

```bash
# 安装服务
./error_monitor_service.sh install

# 启动服务
./error_monitor_service.sh start

# 停止服务
./error_monitor_service.sh stop

# 重启服务
./error_monitor_service.sh restart

# 查看状态
./error_monitor_service.sh status

# 查看日志
./error_monitor_service.sh logs

# 卸载服务
./error_monitor_service.sh uninstall
```

### systemd服务管理

```bash
# 启动服务
sudo systemctl start error-monitor

# 停止服务
sudo systemctl stop error-monitor

# 重启服务
sudo systemctl restart error-monitor

# 查看状态
sudo systemctl status error-monitor

# 查看日志
sudo journalctl -u error-monitor -f

# 开机自启
sudo systemctl enable error-monitor
```

## 邮件通知示例

当系统检测到错误数量超过阈值时，会发送如下格式的邮件：

**主题**: [系统错误监控] 系统错误数量超过阈值 (总计: 15)

**内容**:
```
系统错误监控报告
================

时间: 2024-01-15 14:30:25

错误统计:
总错误数量: 15
错误阈值: 10
时间窗口: 5 分钟

文件: /var/log/syslog
错误数量: 8

文件: ./bookmark_sync.log
错误数量: 7

系统信息:
====================
系统: Linux 6.12.8+
CPU使用率: 45.2%
内存使用率: 67.8%
磁盘使用率: 23.1%
系统运行时间: 5 days, 12:30:15

请及时检查系统状态并处理相关问题。

此邮件由错误监控系统自动发送。
```

## 日志文件

- `error_monitor.log`: 监控系统运行日志
- `journalctl -u error-monitor`: systemd服务日志

## 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查SMTP服务器配置
   - 确认邮箱密码或应用密码正确
   - 检查网络连接

2. **无法读取日志文件**
   - 检查文件路径是否正确
   - 确认有读取权限
   - 检查文件是否存在

3. **服务启动失败**
   - 检查配置文件格式
   - 查看服务日志: `journalctl -u error-monitor`
   - 确认Python依赖已安装

### 调试模式

```bash
# 查看详细日志
tail -f error_monitor.log

# 测试配置文件
python3 -c "import json; json.load(open('error_monitor_config.json'))"

# 测试邮件连接
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email@gmail.com', 'your_password')
print('邮件服务器连接成功')
"
```

## 安全注意事项

1. **配置文件安全**
   - 确保配置文件权限设置为644
   - 不要将包含密码的配置文件提交到版本控制

2. **邮件安全**
   - 使用应用密码而不是账户密码
   - 考虑使用TLS/SSL加密

3. **系统权限**
   - 监控服务以最小权限运行
   - 定期检查日志文件权限

## 扩展功能

### 自定义错误模式

可以在配置文件中添加自定义的错误匹配模式：

```json
{
    "monitor": {
        "error_patterns": [
            "ERROR",
            "FATAL",
            "CRITICAL",
            "Exception",
            "Traceback",
            "Failed",
            "Error:",
            "error:",
            "failed",
            "timeout",
            "connection refused",
            "permission denied",
            "自定义错误模式"
        ]
    }
}
```

### 添加更多日志文件

```json
{
    "monitor": {
        "log_file_paths": [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/auth.log",
            "/var/log/kern.log",
            "./bookmark_sync.log",
            "./sql_to_docs.log",
            "/path/to/your/app.log"
        ]
    }
}
```

## 许可证

本项目采用MIT许可证。

## 支持

如有问题或建议，请提交Issue或联系系统管理员。