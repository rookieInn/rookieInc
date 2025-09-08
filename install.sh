#!/bin/bash

# Let's Encrypt SSL证书管理脚本安装程序

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此安装脚本"
        log_info "使用方法: sudo $0"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# 安装依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y certbot python3-certbot-nginx nginx openssl curl wget
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum install -y epel-release
        yum install -y certbot python3-certbot-nginx nginx openssl curl wget
    elif command -v dnf &> /dev/null; then
        # Fedora
        dnf install -y certbot python3-certbot-nginx nginx openssl curl wget
    else
        log_error "不支持的操作系统，请手动安装依赖"
        exit 1
    fi
    
    log_success "依赖安装完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p /var/log
    mkdir -p /var/www/html
    mkdir -p /etc/nginx/sites-available
    mkdir -p /etc/nginx/sites-enabled
    
    # 设置权限
    chown -R www-data:www-data /var/www/html 2>/dev/null || chown -R nginx:nginx /var/www/html 2>/dev/null || true
    
    log_success "目录创建完成"
}

# 安装脚本文件
install_scripts() {
    log_info "安装脚本文件..."
    
    # 复制脚本到系统目录
    cp ssl_cert_manager.sh /usr/local/bin/
    chmod +x /usr/local/bin/ssl_cert_manager.sh
    
    # 复制systemd服务文件
    cp ssl-cert-manager.service /etc/systemd/system/
    cp ssl-cert-manager.timer /etc/systemd/system/
    
    # 复制配置文件模板
    cp ssl_config.conf.example /etc/ssl-cert-manager/
    mkdir -p /etc/ssl-cert-manager
    
    log_success "脚本文件安装完成"
}

# 配置systemd服务
configure_systemd() {
    log_info "配置systemd服务..."
    
    # 重新加载systemd配置
    systemctl daemon-reload
    
    # 启用定时器
    systemctl enable ssl-cert-manager.timer
    
    log_success "systemd服务配置完成"
}

# 创建初始配置
create_initial_config() {
    log_info "创建初始配置..."
    
    if [ ! -f /etc/ssl-cert-manager/ssl_config.conf ]; then
        cp ssl_config.conf.example /etc/ssl-cert-manager/ssl_config.conf
        log_warn "请编辑配置文件: /etc/ssl-cert-manager/ssl_config.conf"
        log_warn "至少需要设置 DOMAIN 和 EMAIL 参数"
    fi
    
    log_success "初始配置创建完成"
}

# 显示使用说明
show_usage() {
    log_success "安装完成！"
    echo
    echo "下一步操作："
    echo "1. 编辑配置文件:"
    echo "   sudo nano /etc/ssl-cert-manager/ssl_config.conf"
    echo
    echo "2. 设置域名和邮箱:"
    echo "   DOMAIN=\"yourdomain.com\""
    echo "   EMAIL=\"admin@yourdomain.com\""
    echo
    echo "3. 测试脚本:"
    echo "   sudo /usr/local/bin/ssl_cert_manager.sh --dry-run"
    echo
    echo "4. 启动定时任务:"
    echo "   sudo systemctl start ssl-cert-manager.timer"
    echo
    echo "5. 检查状态:"
    echo "   sudo systemctl status ssl-cert-manager.timer"
    echo
    echo "更多信息请查看: /usr/local/bin/ssl_cert_manager.sh --help"
}

# 主函数
main() {
    log_info "开始安装Let's Encrypt SSL证书管理脚本"
    
    check_root
    detect_os
    install_dependencies
    create_directories
    install_scripts
    configure_systemd
    create_initial_config
    show_usage
}

# 运行主函数
main