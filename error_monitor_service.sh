#!/bin/bash
# 错误监控服务管理脚本

SERVICE_NAME="error-monitor"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
WORKSPACE_DIR="/workspace"
PYTHON_SCRIPT="${WORKSPACE_DIR}/error_log_monitor.py"
CONFIG_FILE="${WORKSPACE_DIR}/error_monitor_config.json"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查必要文件
check_files() {
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_message $RED "Python脚本不存在: $PYTHON_SCRIPT"
        exit 1
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_message $RED "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
}

# 安装服务
install_service() {
    print_message $YELLOW "安装错误监控服务..."
    
    # 复制服务文件
    cp "${WORKSPACE_DIR}/${SERVICE_NAME}.service" "$SERVICE_FILE"
    
    # 设置权限
    chmod 644 "$SERVICE_FILE"
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启用服务
    systemctl enable "$SERVICE_NAME"
    
    print_message $GREEN "服务安装完成"
}

# 卸载服务
uninstall_service() {
    print_message $YELLOW "卸载错误监控服务..."
    
    # 停止服务
    systemctl stop "$SERVICE_NAME" 2>/dev/null
    
    # 禁用服务
    systemctl disable "$SERVICE_NAME" 2>/dev/null
    
    # 删除服务文件
    rm -f "$SERVICE_FILE"
    
    # 重新加载systemd
    systemctl daemon-reload
    
    print_message $GREEN "服务卸载完成"
}

# 启动服务
start_service() {
    print_message $YELLOW "启动错误监控服务..."
    
    systemctl start "$SERVICE_NAME"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_message $GREEN "服务启动成功"
    else
        print_message $RED "服务启动失败"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# 停止服务
stop_service() {
    print_message $YELLOW "停止错误监控服务..."
    
    systemctl stop "$SERVICE_NAME"
    
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        print_message $GREEN "服务停止成功"
    else
        print_message $RED "服务停止失败"
        exit 1
    fi
}

# 重启服务
restart_service() {
    print_message $YELLOW "重启错误监控服务..."
    
    systemctl restart "$SERVICE_NAME"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_message $GREEN "服务重启成功"
    else
        print_message $RED "服务重启失败"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# 查看服务状态
status_service() {
    print_message $YELLOW "错误监控服务状态:"
    systemctl status "$SERVICE_NAME"
}

# 查看服务日志
logs_service() {
    print_message $YELLOW "错误监控服务日志:"
    journalctl -u "$SERVICE_NAME" -f
}

# 测试邮件发送
test_email() {
    print_message $YELLOW "测试邮件发送..."
    
    cd "$WORKSPACE_DIR"
    python3 email_notifier.py --test
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "测试邮件发送成功"
    else
        print_message $RED "测试邮件发送失败"
    fi
}

# 测试监控功能
test_monitor() {
    print_message $YELLOW "测试监控功能..."
    
    cd "$WORKSPACE_DIR"
    python3 error_log_monitor.py --test
    
    if [ $? -eq 0 ]; then
        print_message $GREEN "监控功能测试完成"
    else
        print_message $RED "监控功能测试失败"
    fi
}

# 显示帮助信息
show_help() {
    echo "错误监控服务管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  install     安装服务"
    echo "  uninstall   卸载服务"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看服务状态"
    echo "  logs        查看服务日志"
    echo "  test-email  测试邮件发送"
    echo "  test-monitor 测试监控功能"
    echo "  help        显示此帮助信息"
}

# 主函数
main() {
    check_root
    check_files
    
    case "${1:-help}" in
        install)
            install_service
            ;;
        uninstall)
            uninstall_service
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        logs)
            logs_service
            ;;
        test-email)
            test_email
            ;;
        test-monitor)
            test_monitor
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_message $RED "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"