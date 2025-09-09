#!/bin/bash

# Let's Encrypt SSL证书自动管理脚本
# 功能：自动申请、续期SSL证书并更新Nginx配置

set -euo pipefail

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/ssl_config.conf"
LOG_FILE="/var/log/ssl_cert_manager.log"
NGINX_CONFIG_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
CERTBOT_DIR="/etc/letsencrypt"
WEBROOT="/var/www/html"

# 默认配置
DOMAIN=""
EMAIL=""
NGINX_SITE_CONFIG=""
CERT_RENEWAL_DAYS=30
DRY_RUN=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "${BLUE}$*${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

log_error() {
    log "ERROR" "${RED}$*${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# 检查依赖
check_dependencies() {
    local deps=("certbot" "nginx" "openssl")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少依赖: ${missing_deps[*]}"
        log_info "请安装缺少的依赖:"
        for dep in "${missing_deps[@]}"; do
            case "$dep" in
                "certbot")
                    echo "  Ubuntu/Debian: sudo apt-get install certbot python3-certbot-nginx"
                    echo "  CentOS/RHEL: sudo yum install certbot python3-certbot-nginx"
                    ;;
                "nginx")
                    echo "  Ubuntu/Debian: sudo apt-get install nginx"
                    echo "  CentOS/RHEL: sudo yum install nginx"
                    ;;
                "openssl")
                    echo "  Ubuntu/Debian: sudo apt-get install openssl"
                    echo "  CentOS/RHEL: sudo yum install openssl"
                    ;;
            esac
        done
        exit 1
    fi
}

# 加载配置文件
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        log_info "请先创建配置文件，参考 ssl_config.conf.example"
        exit 1
    fi
    
    source "$CONFIG_FILE"
    
    # 验证必需配置
    if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
        log_error "配置文件中缺少必需参数: DOMAIN 或 EMAIL"
        exit 1
    fi
    
    if [ -z "$NGINX_SITE_CONFIG" ]; then
        NGINX_SITE_CONFIG="${NGINX_CONFIG_DIR}/${DOMAIN}"
    fi
    
    log_info "加载配置: 域名=$DOMAIN, 邮箱=$EMAIL, Nginx配置=$NGINX_SITE_CONFIG"
}

# 检查证书是否存在
cert_exists() {
    local domain="$1"
    [ -f "${CERTBOT_DIR}/live/${domain}/fullchain.pem" ]
}

# 检查证书有效期
check_cert_expiry() {
    local domain="$1"
    local cert_file="${CERTBOT_DIR}/live/${domain}/fullchain.pem"
    
    if [ ! -f "$cert_file" ]; then
        return 1
    fi
    
    local expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" | cut -d= -f2)
    local expiry_timestamp=$(date -d "$expiry_date" +%s)
    local current_timestamp=$(date +%s)
    local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
    
    echo "$days_until_expiry"
}

# 申请新证书
request_cert() {
    local domain="$1"
    local email="$2"
    
    log_info "申请新证书: $domain"
    
    # 确保webroot目录存在
    sudo mkdir -p "$WEBROOT"
    sudo chown -R www-data:www-data "$WEBROOT" 2>/dev/null || true
    
    local certbot_cmd="sudo certbot certonly --webroot -w $WEBROOT -d $domain --email $email --agree-tos --non-interactive"
    
    if [ "$DRY_RUN" = true ]; then
        certbot_cmd="$certbot_cmd --dry-run"
        log_info "执行试运行模式"
    fi
    
    if eval "$certbot_cmd"; then
        log_success "证书申请成功: $domain"
        return 0
    else
        log_error "证书申请失败: $domain"
        return 1
    fi
}

# 续期证书
renew_cert() {
    local domain="$1"
    
    log_info "续期证书: $domain"
    
    local certbot_cmd="sudo certbot renew --cert-name $domain"
    
    if [ "$DRY_RUN" = true ]; then
        certbot_cmd="$certbot_cmd --dry-run"
        log_info "执行试运行模式"
    fi
    
    if eval "$certbot_cmd"; then
        log_success "证书续期成功: $domain"
        return 0
    else
        log_error "证书续期失败: $domain"
        return 1
    fi
}

# 更新Nginx配置
update_nginx_config() {
    local domain="$1"
    local nginx_config="$2"
    local cert_file="${CERTBOT_DIR}/live/${domain}/fullchain.pem"
    local key_file="${CERTBOT_DIR}/live/${domain}/privkey.pem"
    
    if [ ! -f "$cert_file" ] || [ ! -f "$key_file" ]; then
        log_error "证书文件不存在，无法更新Nginx配置"
        return 1
    fi
    
    log_info "更新Nginx配置: $nginx_config"
    
    # 备份原配置
    if [ -f "$nginx_config" ]; then
        sudo cp "$nginx_config" "${nginx_config}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 创建或更新Nginx配置
    sudo tee "$nginx_config" > /dev/null <<EOF
server {
    listen 80;
    server_name $domain;
    
    # 重定向HTTP到HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $domain;
    
    # SSL证书配置
    ssl_certificate $cert_file;
    ssl_certificate_key $key_file;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # 网站根目录
    root $WEBROOT;
    index index.html index.htm index.php;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 安全配置
    location ~ /\. {
        deny all;
    }
}
EOF
    
    # 创建软链接到enabled目录
    local enabled_config="${NGINX_ENABLED_DIR}/$(basename "$nginx_config")"
    if [ ! -L "$enabled_config" ]; then
        sudo ln -sf "$nginx_config" "$enabled_config"
    fi
    
    # 测试Nginx配置
    if sudo nginx -t; then
        log_success "Nginx配置测试通过"
        # 重新加载Nginx
        if sudo systemctl reload nginx; then
            log_success "Nginx重新加载成功"
            return 0
        else
            log_error "Nginx重新加载失败"
            return 1
        fi
    else
        log_error "Nginx配置测试失败"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始SSL证书管理任务"
    
    # 检查依赖
    check_dependencies
    
    # 加载配置
    load_config
    
    # 检查证书是否存在
    if cert_exists "$DOMAIN"; then
        log_info "证书已存在，检查有效期"
        
        local days_until_expiry
        days_until_expiry=$(check_cert_expiry "$DOMAIN")
        
        if [ "$days_until_expiry" -gt "$CERT_RENEWAL_DAYS" ]; then
            log_info "证书有效期还有 $days_until_expiry 天，无需续期"
            # 即使不需要续期，也检查Nginx配置是否需要更新
            update_nginx_config "$DOMAIN" "$NGINX_SITE_CONFIG"
        else
            log_warn "证书将在 $days_until_expiry 天后过期，开始续期"
            if renew_cert "$DOMAIN"; then
                update_nginx_config "$DOMAIN" "$NGINX_SITE_CONFIG"
            else
                log_error "证书续期失败"
                exit 1
            fi
        fi
    else
        log_info "证书不存在，申请新证书"
        if request_cert "$DOMAIN" "$EMAIL"; then
            update_nginx_config "$DOMAIN" "$NGINX_SITE_CONFIG"
        else
            log_error "证书申请失败"
            exit 1
        fi
    fi
    
    log_success "SSL证书管理任务完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
Let's Encrypt SSL证书自动管理脚本

用法: $0 [选项]

选项:
    -h, --help          显示此帮助信息
    -d, --domain DOMAIN 指定域名
    -e, --email EMAIL   指定邮箱地址
    -c, --config FILE   指定配置文件路径
    --dry-run           试运行模式
    --renew             强制续期证书
    --update-nginx      仅更新Nginx配置

示例:
    $0 --domain example.com --email admin@example.com
    $0 --config /path/to/config.conf
    $0 --renew --dry-run

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --renew)
            FORCE_RENEW=true
            shift
            ;;
        --update-nginx)
            UPDATE_NGINX_ONLY=true
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 如果指定了强制续期
if [ "${FORCE_RENEW:-false}" = true ]; then
    load_config
    if renew_cert "$DOMAIN"; then
        update_nginx_config "$DOMAIN" "$NGINX_SITE_CONFIG"
    else
        log_error "强制续期失败"
        exit 1
    fi
    exit 0
fi

# 如果仅更新Nginx配置
if [ "${UPDATE_NGINX_ONLY:-false}" = true ]; then
    load_config
    update_nginx_config "$DOMAIN" "$NGINX_SITE_CONFIG"
    exit 0
fi

# 执行主函数
main