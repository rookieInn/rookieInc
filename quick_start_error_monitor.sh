#!/bin/bash
# 错误监控系统快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message $BLUE "🚀 错误监控系统快速启动"
echo "=================================="

# 检查Python环境
print_message $YELLOW "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    print_message $RED "Python3 未安装，请先安装Python3"
    exit 1
fi
print_message $GREEN "✅ Python3 已安装"

# 检查依赖
print_message $YELLOW "检查依赖..."
if ! python3 -c "import psutil" 2>/dev/null; then
    print_message $YELLOW "安装psutil依赖..."
    pip3 install psutil --break-system-packages --quiet
fi
print_message $GREEN "✅ 依赖检查完成"

# 运行基本测试
print_message $YELLOW "运行基本功能测试..."
python3 simple_test.py

echo ""
print_message $BLUE "📋 使用说明:"
echo "1. 配置邮件服务器:"
echo "   nano error_monitor_config.json"
echo ""
echo "2. 测试邮件发送:"
echo "   python3 email_notifier.py --test"
echo ""
echo "3. 测试监控功能:"
echo "   python3 error_log_monitor.py --test"
echo ""
echo "4. 启动监控服务:"
echo "   python3 error_log_monitor.py"
echo ""
echo "5. 安装为系统服务:"
echo "   sudo ./error_monitor_service.sh install"
echo "   sudo ./error_monitor_service.sh start"
echo ""

print_message $GREEN "🎉 错误监控系统准备就绪！"
print_message $YELLOW "请根据上述说明配置邮件服务器后开始使用。"