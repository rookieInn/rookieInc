# 系统错误监控和邮件通知系统 - 功能总结

## 🎯 系统概述

我已经为您创建了一个完整的系统错误监控和邮件通知解决方案。当系统在几分钟内错误日志超过设定阈值时，会自动发送邮件给系统负责人。

## 📁 创建的文件

### 核心功能文件
- `error_log_monitor.py` - 主监控脚本，负责监控日志文件并检测错误
- `email_notifier.py` - 邮件发送工具，支持HTML格式邮件
- `error_monitor_config.json` - 配置文件，包含所有监控和邮件设置

### 服务管理文件
- `error-monitor.service` - systemd服务文件
- `error_monitor_service.sh` - 服务管理脚本（安装、启动、停止等）
- `install_error_monitor.sh` - 自动安装脚本

### 测试和文档
- `test_error_monitor.py` - 完整功能测试脚本
- `simple_test.py` - 基本功能测试脚本
- `quick_start_error_monitor.sh` - 快速启动脚本
- `README_错误监控系统.md` - 详细使用说明文档

## ⚙️ 核心功能特性

### 1. 智能错误监控
- **多文件监控**: 支持监控多个日志文件
- **模式匹配**: 可配置的错误关键词匹配
- **时间窗口**: 在指定时间窗口内统计错误数量
- **实时检测**: 可配置的检查间隔

### 2. 邮件通知系统
- **HTML邮件**: 美观的HTML格式邮件通知
- **多收件人**: 支持多个收件人
- **防重复通知**: 冷却时间和频率限制
- **系统信息**: 包含CPU、内存、磁盘使用率等

### 3. 系统服务集成
- **systemd服务**: 可作为系统服务运行
- **开机自启**: 支持系统启动时自动运行
- **服务管理**: 完整的启动、停止、重启功能

## 🔧 配置说明

### 监控配置
```json
{
    "monitor": {
        "log_file_paths": [           // 监控的日志文件
            "/var/log/syslog",
            "/var/log/messages",
            "./bookmark_sync.log"
        ],
        "error_patterns": [           // 错误匹配模式
            "ERROR", "FATAL", "CRITICAL", "Exception"
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
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "to_emails": ["admin@yourcompany.com"]
    }
}
```

## 🚀 快速开始

### 1. 运行快速启动脚本
```bash
./quick_start_error_monitor.sh
```

### 2. 配置邮件服务器
编辑 `error_monitor_config.json` 文件，设置您的邮件服务器信息。

### 3. 测试功能
```bash
# 测试邮件发送
python3 email_notifier.py --test

# 测试监控功能
python3 error_log_monitor.py --test
```

### 4. 启动监控
```bash
# 直接运行
python3 error_log_monitor.py

# 或安装为系统服务
sudo ./error_monitor_service.sh install
sudo ./error_monitor_service.sh start
```

## 📊 监控效果

当系统检测到错误数量超过阈值时，会发送如下格式的邮件：

**邮件主题**: [系统错误监控] 系统错误数量超过阈值 (总计: 15)

**邮件内容**:
- 错误统计信息
- 各文件错误数量
- 系统状态信息（CPU、内存、磁盘使用率）
- 系统运行时间
- 错误示例（如果启用）

## 🛠️ 管理命令

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

### 测试命令
```bash
# 测试邮件发送
./error_monitor_service.sh test-email

# 测试监控功能
./error_monitor_service.sh test-monitor
```

## 📈 监控指标

系统会监控以下指标：
- **错误数量**: 在指定时间窗口内的错误总数
- **文件级别统计**: 每个日志文件的错误数量
- **系统资源**: CPU、内存、磁盘使用率
- **系统运行时间**: 系统启动后的运行时间

## 🔒 安全特性

- **权限控制**: 最小权限原则
- **配置文件保护**: 建议设置适当的文件权限
- **邮件安全**: 支持TLS/SSL加密
- **防重复通知**: 避免邮件轰炸

## 📝 日志记录

- **监控日志**: `error_monitor.log`
- **系统日志**: `journalctl -u error-monitor`
- **错误详情**: 邮件中包含错误示例

## 🎛️ 自定义选项

### 错误模式自定义
可以在配置文件中添加自定义的错误匹配模式：
```json
"error_patterns": [
    "ERROR", "FATAL", "CRITICAL",
    "自定义错误关键词",
    "特定应用错误"
]
```

### 监控文件添加
```json
"log_file_paths": [
    "/var/log/syslog",
    "/path/to/your/app.log",
    "/path/to/another/service.log"
]
```

### 通知频率调整
```json
"notification": {
    "cooldown_minutes": 30,           // 通知冷却时间
    "max_notifications_per_hour": 5,  // 每小时最大通知次数
    "include_error_details": true,    // 包含错误详情
    "include_system_info": true       // 包含系统信息
}
```

## 🎉 总结

这个错误监控系统提供了：

1. **自动化监控**: 无需人工干预，自动检测错误
2. **及时通知**: 错误超过阈值时立即发送邮件
3. **灵活配置**: 可根据需求调整监控参数
4. **系统集成**: 可作为系统服务运行
5. **易于管理**: 提供完整的服务管理工具
6. **详细报告**: 包含系统状态和错误详情

系统已经准备就绪，您只需要配置邮件服务器信息即可开始使用！