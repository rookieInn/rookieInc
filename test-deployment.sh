#!/bin/bash

# Docker多服务部署测试脚本
# 使用方法: ./test-deployment.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 测试服务健康状态
test_service_health() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    log_info "测试 $service_name 服务健康状态..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$service_name 服务健康检查通过"
            return 0
        else
            log_info "尝试 $attempt/$max_attempts - 等待服务启动..."
            sleep 2
            ((attempt++))
        fi
    done
    
    log_error "$service_name 服务健康检查失败"
    return 1
}

# 测试所有服务
test_all_services() {
    log_info "开始测试所有服务..."
    
    local all_passed=true
    
    # 测试OSS监控服务
    if ! test_service_health "OSS监控" "http://localhost:5001/health"; then
        all_passed=false
    fi
    
    # 测试页面埋点API
    if ! test_service_health "页面埋点API" "http://localhost:5002/api/health"; then
        all_passed=false
    fi
    
    # 测试视频水印服务
    if ! test_service_health "视频水印" "http://localhost:5003/health"; then
        all_passed=false
    fi
    
    # 测试微信群机器人
    if ! test_service_health "微信群机器人" "http://localhost:8000/health"; then
        all_passed=false
    fi
    
    # 测试Prometheus
    if ! test_service_health "Prometheus" "http://localhost:9090/-/healthy"; then
        all_passed=false
    fi
    
    # 测试Grafana
    if ! test_service_health "Grafana" "http://localhost:3000/api/health"; then
        all_passed=false
    fi
    
    if [ "$all_passed" = true ]; then
        log_success "所有服务健康检查通过！"
        return 0
    else
        log_error "部分服务健康检查失败"
        return 1
    fi
}

# 显示服务状态
show_service_status() {
    log_info "服务状态概览:"
    echo ""
    
    # 显示Docker容器状态
    docker-compose ps
    echo ""
    
    # 显示服务访问地址
    log_info "服务访问地址:"
    echo "  📊 OSS监控仪表板: http://oss.localhost (http://localhost:5001)"
    echo "  📈 页面埋点API: http://api.localhost (http://localhost:5002)"
    echo "  🎬 视频水印服务: http://video.localhost (http://localhost:5003)"
    echo "  🤖 微信群机器人: http://localhost:8000"
    echo "  📊 Grafana监控: http://localhost:3000"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  🏠 服务概览: http://localhost"
    echo ""
}

# 测试API功能
test_api_functionality() {
    log_info "测试API功能..."
    
    # 测试页面埋点API
    log_info "测试页面埋点API..."
    response=$(curl -s -X POST http://localhost:5002/api/events \
        -H "Content-Type: application/json" \
        -d '{
            "event_type": "page_view",
            "page_url": "http://test.com",
            "user_id": "test_user",
            "session_id": "test_session",
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
        }' 2>/dev/null || echo "API调用失败")
    
    if echo "$response" | grep -q "success\|event_id"; then
        log_success "页面埋点API功能正常"
    else
        log_warning "页面埋点API功能异常: $response"
    fi
    
    # 测试视频水印服务状态
    log_info "测试视频水印服务..."
    response=$(curl -s http://localhost:5003/api/status 2>/dev/null || echo "API调用失败")
    
    if echo "$response" | grep -q "running"; then
        log_success "视频水印服务功能正常"
    else
        log_warning "视频水印服务功能异常: $response"
    fi
}

# 显示资源使用情况
show_resource_usage() {
    log_info "资源使用情况:"
    echo ""
    
    # 显示Docker容器资源使用
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    
    # 显示磁盘使用
    log_info "磁盘使用情况:"
    df -h | grep -E "(Filesystem|/dev/)"
    echo ""
}

# 清理测试
cleanup_test() {
    log_info "清理测试环境..."
    
    # 停止所有服务
    docker-compose down
    
    # 清理未使用的镜像
    docker image prune -f
    
    log_success "测试环境清理完成"
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "🧪 Docker多服务部署测试"
    echo "========================"
    echo -e "${NC}"
    
    # 检查Docker是否运行
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker未运行，请先启动Docker"
        exit 1
    fi
    
    # 启动服务
    log_info "启动所有服务..."
    docker-compose up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 显示服务状态
    show_service_status
    
    # 测试服务健康状态
    if test_all_services; then
        log_success "✅ 所有服务健康检查通过"
        
        # 测试API功能
        test_api_functionality
        
        # 显示资源使用情况
        show_resource_usage
        
        log_success "🎉 部署测试完成！所有服务运行正常"
    else
        log_error "❌ 部分服务健康检查失败"
        
        # 显示失败的容器日志
        log_info "显示失败的容器日志:"
        docker-compose logs --tail=50
        
        exit 1
    fi
}

# 处理命令行参数
case "${1:-test}" in
    test)
        main
        ;;
    status)
        show_service_status
        ;;
    health)
        test_all_services
        ;;
    api)
        test_api_functionality
        ;;
    resources)
        show_resource_usage
        ;;
    cleanup)
        cleanup_test
        ;;
    *)
        echo "使用方法: $0 {test|status|health|api|resources|cleanup}"
        echo ""
        echo "命令说明:"
        echo "  test     - 完整部署测试 (默认)"
        echo "  status   - 显示服务状态"
        echo "  health   - 健康检查测试"
        echo "  api      - API功能测试"
        echo "  resources - 显示资源使用情况"
        echo "  cleanup  - 清理测试环境"
        exit 1
        ;;
esac