#!/bin/bash

# 多服务Docker部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|logs|status|clean]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs/{wechat,oss,tracking,video,bookmark,nginx}
    mkdir -p data/{wechat,oss,tracking,video,bookmark}
    mkdir -p ssl
    
    log_success "目录创建完成"
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在，从 .env.example 创建..."
        cp .env.example .env
        log_warning "请编辑 .env 文件配置您的环境变量"
    fi
}

# 启动服务
start_services() {
    log_info "启动所有服务..."
    
    check_dependencies
    create_directories
    check_env_file
    
    # 构建并启动服务
    docker-compose up -d --build
    
    log_success "所有服务已启动"
    show_status
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    
    docker-compose down
    
    log_success "所有服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启所有服务..."
    
    docker-compose restart
    
    log_success "所有服务已重启"
    show_status
}

# 查看日志
show_logs() {
    local service=${1:-""}
    
    if [ -n "$service" ]; then
        log_info "显示 $service 服务日志..."
        docker-compose logs -f "$service"
    else
        log_info "显示所有服务日志..."
        docker-compose logs -f
    fi
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    echo ""
    docker-compose ps
    echo ""
    
    log_info "服务访问地址:"
    echo "  📊 OSS监控仪表板: http://oss.localhost"
    echo "  📈 页面埋点API: http://api.localhost"
    echo "  🎬 视频水印服务: http://video.localhost"
    echo "  📊 Grafana监控: http://localhost:3000"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🏠 服务概览: http://localhost"
    echo ""
}

# 清理资源
clean_resources() {
    log_warning "清理Docker资源..."
    
    read -p "确定要清理所有容器、镜像和数据卷吗? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "清理完成"
    else
        log_info "取消清理"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    services=("oss-monitor" "tracking-api" "video-watermark" "wechat-bot")
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务运行异常"
        fi
    done
}

# 更新服务
update_services() {
    log_info "更新服务..."
    
    docker-compose pull
    docker-compose up -d --build
    
    log_success "服务更新完成"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs "$2"
            ;;
        status)
            show_status
            ;;
        health)
            health_check
            ;;
        update)
            update_services
            ;;
        clean)
            clean_resources
            ;;
        *)
            echo "使用方法: $0 {start|stop|restart|logs|status|health|update|clean}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动所有服务"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  logs     - 查看日志 (可选指定服务名)"
            echo "  status   - 查看服务状态"
            echo "  health   - 健康检查"
            echo "  update   - 更新服务"
            echo "  clean    - 清理资源"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"