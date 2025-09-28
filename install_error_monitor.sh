#!/bin/bash
# 错误监控系统安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_message $RED "请使用root权限运行此脚本"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_message $RED "无法确定操作系统类型"
        exit 1
    fi
    
    print_message $BLUE "检测到操作系统: $OS $VER"
}

# 安装Python依赖
install_python_deps() {
    print_message $YELLOW "安装Python依赖..."
    
    # 检查Python3是否已安装
    if ! command -v python3 &> /dev/null; then
        print_message $YELLOW "安装Python3..."
        if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
            apt-get update
            apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
            yum install -y python3 python3-pip
        else
            print_message $RED "不支持的操作系统: $OS"
            exit 1
        fi
    fi
    
    # 安装Python包
    pip3 install psutil
    
    print_message $GREEN "Python依赖安装完成"
}

# 创建配置文件
create_config() {
    print_message $YELLOW "创建配置文件..."
    
    # 检查配置文件是否存在
    if [ -f "error_monitor_config.json" ]; then
        print_message $YELLOW "配置文件已存在，是否要覆盖? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_message $BLUE "跳过配置文件创建"
            return
        fi
    fi
    
    # 创建配置文件
    cat > error_monitor_config.json << 'EOF'
{
    "monitor": {
        "log_file_paths": [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/auth.log",
            "/var/log/kern.log",
            "./bookmark_sync.log",
            "./sql_to_docs.log"
        ],
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
            "permission denied"
        ],
        "time_window_minutes": 5,
        "error_threshold": 10,
        "check_interval_seconds": 30
    },
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
    },
    "notification": {
        "cooldown_minutes": 30,
        "max_notifications_per_hour": 5,
        "include_error_details": true,
        "include_system_info": true
    }
}
EOF
    
    print_message $GREEN "配置文件创建完成"
    print_message $YELLOW "请编辑 error_monitor_config.json 文件，配置邮件服务器和收件人信息"
}

# 配置邮件设置
configure_email() {
    print_message $YELLOW "配置邮件设置..."
    
    echo "请输入邮件配置信息:"
    echo ""
    
    # SMTP服务器
    echo -n "SMTP服务器 (默认: smtp.gmail.com): "
    read -r smtp_server
    smtp_server=${smtp_server:-smtp.gmail.com}
    
    # SMTP端口
    echo -n "SMTP端口 (默认: 587): "
    read -r smtp_port
    smtp_port=${smtp_port:-587}
    
    # 发送邮箱
    echo -n "发送邮箱地址: "
    read -r from_email
    
    # 邮箱密码或应用密码
    echo -n "邮箱密码或应用密码: "
    read -s password
    echo ""
    
    # 收件人邮箱
    echo -n "收件人邮箱地址 (多个用空格分隔): "
    read -r to_emails_input
    
    # 转换为数组
    IFS=' ' read -ra to_emails_array <<< "$to_emails_input"
    to_emails_json=$(printf '%s\n' "${to_emails_array[@]}" | jq -R . | jq -s .)
    
    # 更新配置文件
    jq --arg smtp_server "$smtp_server" \
       --arg smtp_port "$smtp_port" \
       --arg from_email "$from_email" \
       --arg password "$password" \
       --argjson to_emails "$to_emails_json" \
       '.email.smtp_server = $smtp_server |
        .email.smtp_port = ($smtp_port | tonumber) |
        .email.username = $from_email |
        .email.password = $password |
        .email.from_email = $from_email |
        .email.to_emails = $to_emails' \
       error_monitor_config.json > error_monitor_config.json.tmp && \
       mv error_monitor_config.json.tmp error_monitor_config.json
    
    print_message $GREEN "邮件配置完成"
}

# 设置文件权限
set_permissions() {
    print_message $YELLOW "设置文件权限..."
    
    chmod +x error_log_monitor.py
    chmod +x email_notifier.py
    chmod +x error_monitor_service.sh
    
    # 设置日志文件权限
    touch error_monitor.log
    chmod 644 error_monitor.log
    
    print_message $GREEN "文件权限设置完成"
}

# 测试安装
test_installation() {
    print_message $YELLOW "测试安装..."
    
    # 测试Python脚本
    if python3 -c "import psutil, smtplib, json" 2>/dev/null; then
        print_message $GREEN "Python依赖检查通过"
    else
        print_message $RED "Python依赖检查失败"
        exit 1
    fi
    
    # 测试配置文件
    if python3 -c "import json; json.load(open('error_monitor_config.json'))" 2>/dev/null; then
        print_message $GREEN "配置文件格式检查通过"
    else
        print_message $RED "配置文件格式检查失败"
        exit 1
    fi
    
    # 测试监控功能
    print_message $YELLOW "测试监控功能..."
    if python3 error_log_monitor.py --test; then
        print_message $GREEN "监控功能测试通过"
    else
        print_message $YELLOW "监控功能测试失败，请检查配置"
    fi
    
    print_message $GREEN "安装测试完成"
}

# 显示使用说明
show_usage() {
    print_message $BLUE "错误监控系统安装完成！"
    echo ""
    print_message $YELLOW "使用说明:"
    echo "1. 编辑配置文件: nano error_monitor_config.json"
    echo "2. 测试邮件发送: ./error_monitor_service.sh test-email"
    echo "3. 测试监控功能: ./error_monitor_service.sh test-monitor"
    echo "4. 安装系统服务: ./error_monitor_service.sh install"
    echo "5. 启动监控服务: ./error_monitor_service.sh start"
    echo "6. 查看服务状态: ./error_monitor_service.sh status"
    echo "7. 查看服务日志: ./error_monitor_service.sh logs"
    echo ""
    print_message $YELLOW "配置文件说明:"
    echo "- monitor.time_window_minutes: 监控时间窗口（分钟）"
    echo "- monitor.error_threshold: 错误数量阈值"
    echo "- monitor.check_interval_seconds: 检查间隔（秒）"
    echo "- email.*: 邮件服务器配置"
    echo "- notification.*: 通知设置"
    echo ""
    print_message $YELLOW "注意事项:"
    echo "- 确保邮件服务器配置正确"
    echo "- 对于Gmail，需要使用应用密码而不是账户密码"
    echo "- 监控的日志文件需要有读取权限"
    echo "- 建议定期检查 error_monitor.log 文件"
}

# 主函数
main() {
    print_message $BLUE "开始安装错误监控系统..."
    
    check_root
    check_system
    install_python_deps
    create_config
    
    # 询问是否配置邮件
    echo ""
    print_message $YELLOW "是否现在配置邮件设置? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        configure_email
    else
        print_message $YELLOW "请稍后手动编辑 error_monitor_config.json 文件"
    fi
    
    set_permissions
    test_installation
    show_usage
    
    print_message $GREEN "安装完成！"
}

# 运行主函数
main "$@"