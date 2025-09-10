#!/bin/bash
# OSS存储监控系统安装脚本

set -e

echo "=========================================="
echo "OSS存储监控系统安装脚本"
echo "=========================================="

# 检查Python版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到Python3，请先安装Python3"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "检测到Python版本: $python_version"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        echo "错误: 需要Python 3.7或更高版本"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    echo "正在安装Python依赖..."
    
    # 创建requirements.txt
    cat > requirements_oss_monitor.txt << EOF
oss2==2.18.4
pandas==2.1.4
matplotlib==3.7.2
seaborn==0.12.2
flask==3.0.0
flask-cors==4.0.0
schedule==1.2.0
requests==2.31.0
python-dateutil==2.8.2
tqdm==4.66.1
Pillow==10.1.0
numpy==1.24.3
EOF
    
    # 安装依赖
    pip3 install -r requirements_oss_monitor.txt
    
    echo "Python依赖安装完成"
}

# 创建必要的目录
create_directories() {
    echo "创建必要的目录..."
    
    mkdir -p reports
    mkdir -p logs
    mkdir -p templates
    mkdir -p backups
    
    echo "目录创建完成"
}

# 设置文件权限
set_permissions() {
    echo "设置文件权限..."
    
    chmod +x oss_storage_monitor.py
    chmod +x oss_monitor_dashboard.py
    chmod +x oss_monitor_scheduler.py
    
    echo "文件权限设置完成"
}

# 创建systemd服务
create_systemd_service() {
    echo "创建systemd服务..."
    
    # 获取当前用户
    current_user=$(whoami)
    current_dir=$(pwd)
    
    # 创建服务文件
    sudo tee /etc/systemd/system/oss-monitor.service > /dev/null << EOF
[Unit]
Description=OSS Storage Monitor Scheduler
After=network.target

[Service]
Type=simple
User=$current_user
WorkingDirectory=$current_dir
ExecStart=/usr/bin/python3 $current_dir/oss_monitor_scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    echo "systemd服务创建完成"
    echo "使用以下命令管理服务:"
    echo "  sudo systemctl enable oss-monitor    # 启用服务"
    echo "  sudo systemctl start oss-monitor     # 启动服务"
    echo "  sudo systemctl status oss-monitor    # 查看状态"
    echo "  sudo systemctl stop oss-monitor      # 停止服务"
}

# 创建cron任务
create_cron_jobs() {
    echo "创建cron任务..."
    
    current_dir=$(pwd)
    
    # 创建cron文件
    sudo tee /etc/cron.d/oss-monitor > /dev/null << EOF
# OSS存储监控定时任务
# 每天凌晨2点检查存储
0 2 * * * $current_user /usr/bin/python3 $current_dir/oss_monitor_scheduler.py --run-once check >> $current_dir/logs/cron.log 2>&1

# 每周一上午9点生成报告
0 9 * * 1 $current_user /usr/bin/python3 $current_dir/oss_monitor_scheduler.py --run-once report >> $current_dir/logs/cron.log 2>&1

# 每月1号凌晨3点清理旧数据
0 3 1 * * $current_user /usr/bin/python3 $current_dir/oss_monitor_scheduler.py --run-once cleanup >> $current_dir/logs/cron.log 2>&1
EOF
    
    echo "cron任务创建完成"
    echo "使用以下命令查看cron任务:"
    echo "  sudo crontab -l"
    echo "  cat /etc/cron.d/oss-monitor"
}

# 创建启动脚本
create_startup_scripts() {
    echo "创建启动脚本..."
    
    # 创建启动监控脚本
    cat > start_monitor.sh << 'EOF'
#!/bin/bash
# 启动OSS存储监控

echo "启动OSS存储监控系统..."

# 检查配置文件
if [ ! -f "oss_monitor_config.json" ]; then
    echo "错误: 配置文件 oss_monitor_config.json 不存在"
    echo "请先配置OSS桶信息"
    exit 1
fi

# 启动Web仪表板
echo "启动Web仪表板..."
python3 oss_monitor_dashboard.py --host 0.0.0.0 --port 5000 &
DASHBOARD_PID=$!

# 启动定时调度器
echo "启动定时调度器..."
python3 oss_monitor_scheduler.py &
SCHEDULER_PID=$!

echo "监控系统已启动"
echo "Web仪表板: http://localhost:5000"
echo "仪表板PID: $DASHBOARD_PID"
echo "调度器PID: $SCHEDULER_PID"

# 保存PID到文件
echo $DASHBOARD_PID > dashboard.pid
echo $SCHEDULER_PID > scheduler.pid

echo "使用 stop_monitor.sh 停止监控系统"
EOF

    # 创建停止监控脚本
    cat > stop_monitor.sh << 'EOF'
#!/bin/bash
# 停止OSS存储监控

echo "停止OSS存储监控系统..."

# 停止Web仪表板
if [ -f "dashboard.pid" ]; then
    DASHBOARD_PID=$(cat dashboard.pid)
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        kill $DASHBOARD_PID
        echo "Web仪表板已停止 (PID: $DASHBOARD_PID)"
    fi
    rm -f dashboard.pid
fi

# 停止定时调度器
if [ -f "scheduler.pid" ]; then
    SCHEDULER_PID=$(cat scheduler.pid)
    if kill -0 $SCHEDULER_PID 2>/dev/null; then
        kill $SCHEDULER_PID
        echo "定时调度器已停止 (PID: $SCHEDULER_PID)"
    fi
    rm -f scheduler.pid
fi

echo "监控系统已停止"
EOF

    # 创建快速检查脚本
    cat > quick_check.sh << 'EOF'
#!/bin/bash
# 快速检查OSS存储

echo "执行快速存储检查..."

python3 oss_storage_monitor.py --check

echo "检查完成，查看日志文件获取详细信息"
EOF

    # 创建报告生成脚本
    cat > generate_report.sh << 'EOF'
#!/bin/bash
# 生成存储报告

echo "生成存储报告..."

# 生成所有桶的报告
python3 oss_storage_monitor.py --report

echo "报告已生成到 reports/ 目录"
EOF

    # 设置脚本权限
    chmod +x start_monitor.sh
    chmod +x stop_monitor.sh
    chmod +x quick_check.sh
    chmod +x generate_report.sh

    echo "启动脚本创建完成"
}

# 创建配置文件模板
create_config_template() {
    echo "创建配置文件模板..."
    
    if [ ! -f "oss_monitor_config.json" ]; then
        echo "配置文件已存在，跳过创建"
        return
    fi
    
    echo "请编辑 oss_monitor_config.json 文件，配置您的OSS桶信息"
    echo "配置文件位置: $(pwd)/oss_monitor_config.json"
}

# 创建使用说明
create_usage_guide() {
    echo "创建使用说明..."
    
    cat > OSS_MONITOR_README.md << 'EOF'
# OSS存储监控系统使用说明

## 系统概述

OSS存储监控系统是一个用于监控阿里云OSS桶存储使用情况的完整解决方案，支持：

- 每日存储量统计
- 存储趋势分析
- Web仪表板可视化
- 定时任务调度
- 报告生成
- 数据清理

## 快速开始

### 1. 配置OSS桶信息

编辑 `oss_monitor_config.json` 文件，填入您的OSS桶信息：

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

### 2. 启动监控系统

```bash
# 启动完整监控系统（Web仪表板 + 定时调度器）
./start_monitor.sh

# 或者分别启动
python3 oss_monitor_dashboard.py    # 启动Web仪表板
python3 oss_monitor_scheduler.py    # 启动定时调度器
```

### 3. 访问Web仪表板

打开浏览器访问: http://localhost:5000

## 主要功能

### 存储检查

```bash
# 手动检查所有桶
python3 oss_storage_monitor.py --check

# 检查特定桶
python3 oss_storage_monitor.py --check --bucket your-bucket-name
```

### 报告生成

```bash
# 生成所有桶的报告
python3 oss_storage_monitor.py --report

# 生成特定桶的报告
python3 oss_storage_monitor.py --report --bucket your-bucket-name --days 30
```

### 数据清理

```bash
# 清理超过保留期的历史数据
python3 oss_storage_monitor.py --cleanup
```

## 定时任务

系统支持两种定时任务方式：

### 1. systemd服务（推荐）

```bash
# 启用服务
sudo systemctl enable oss-monitor

# 启动服务
sudo systemctl start oss-monitor

# 查看状态
sudo systemctl status oss-monitor
```

### 2. cron任务

```bash
# 查看cron任务
cat /etc/cron.d/oss-monitor
```

## 配置说明

### 监控配置

- `check_interval_hours`: 检查间隔（小时）
- `retention_days`: 数据保留天数
- `alert_threshold_gb`: 告警阈值（GB）

### 调度配置

- `check_interval`: 检查频率（daily/hourly/weekly）
- `check_time`: 检查时间
- `report_interval`: 报告生成频率
- `cleanup_interval`: 数据清理频率

## 文件结构

```
.
├── oss_storage_monitor.py      # 主监控程序
├── oss_monitor_dashboard.py    # Web仪表板
├── oss_monitor_scheduler.py    # 定时调度器
├── oss_monitor_config.json     # 配置文件
├── oss_monitor.db             # SQLite数据库
├── reports/                   # 报告输出目录
├── logs/                      # 日志目录
├── templates/                 # Web模板
└── start_monitor.sh          # 启动脚本
```

## 故障排除

### 1. 权限问题

```bash
# 确保脚本有执行权限
chmod +x *.py *.sh
```

### 2. 依赖问题

```bash
# 重新安装依赖
pip3 install -r requirements_oss_monitor.txt
```

### 3. 配置文件问题

```bash
# 检查配置文件格式
python3 -m json.tool oss_monitor_config.json
```

### 4. 数据库问题

```bash
# 删除数据库文件重新创建
rm oss_monitor.db
python3 oss_storage_monitor.py --check
```

## 日志查看

```bash
# 查看监控日志
tail -f oss_monitor.log

# 查看调度器日志
tail -f oss_monitor_scheduler.log

# 查看cron日志
tail -f logs/cron.log
```

## 性能优化

1. 调整检查频率避免API限制
2. 定期清理历史数据
3. 使用SSD存储数据库文件
4. 配置合适的告警阈值

## 安全建议

1. 使用IAM子账号的访问密钥
2. 限制访问密钥权限
3. 定期轮换访问密钥
4. 保护配置文件权限

## 技术支持

如有问题，请检查：

1. 配置文件格式是否正确
2. OSS访问密钥是否有效
3. 网络连接是否正常
4. 日志文件中的错误信息
EOF

    echo "使用说明已创建: OSS_MONITOR_README.md"
}

# 主安装流程
main() {
    echo "开始安装OSS存储监控系统..."
    
    check_python
    install_dependencies
    create_directories
    set_permissions
    create_startup_scripts
    create_config_template
    create_usage_guide
    
    echo ""
    echo "=========================================="
    echo "安装完成！"
    echo "=========================================="
    echo ""
    echo "下一步操作："
    echo "1. 编辑配置文件: oss_monitor_config.json"
    echo "2. 运行快速检查: ./quick_check.sh"
    echo "3. 启动监控系统: ./start_monitor.sh"
    echo "4. 访问Web仪表板: http://localhost:5000"
    echo ""
    echo "详细使用说明请查看: OSS_MONITOR_README.md"
    echo ""
    
    # 询问是否创建系统服务
    read -p "是否创建systemd服务？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_systemd_service
    fi
    
    # 询问是否创建cron任务
    read -p "是否创建cron任务？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_cron_jobs
    fi
    
    echo "安装完成！"
}

# 运行主函数
main "$@"