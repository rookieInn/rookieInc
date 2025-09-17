#!/bin/bash

# 快速启动脚本 - 一键部署多服务
# 使用方法: ./quick-start.sh

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "🚀 多服务Docker部署 - 快速启动"
echo "================================"
echo -e "${NC}"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker 未安装，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 创建环境变量文件...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  请编辑 .env 文件配置您的环境变量${NC}"
fi

# 创建必要目录
echo -e "${BLUE}📁 创建必要目录...${NC}"
mkdir -p logs/{wechat,oss,tracking,video,bookmark,nginx}
mkdir -p data/{wechat,oss,tracking,video,bookmark}
mkdir -p ssl

# 启动服务
echo -e "${BLUE}🐳 启动Docker服务...${NC}"
docker-compose up -d --build

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 10

# 显示状态
echo -e "${GREEN}"
echo "✅ 部署完成！"
echo ""
echo "🌐 服务访问地址:"
echo "  📊 OSS监控仪表板: http://oss.localhost"
echo "  📈 页面埋点API: http://api.localhost"  
echo "  🎬 视频水印服务: http://video.localhost"
echo "  📊 Grafana监控: http://localhost:3000"
echo "  📈 Prometheus: http://localhost:9090"
echo "  🏠 服务概览: http://localhost"
echo ""
echo "📋 管理命令:"
echo "  查看状态: ./deploy.sh status"
echo "  查看日志: ./deploy.sh logs"
echo "  停止服务: ./deploy.sh stop"
echo "  重启服务: ./deploy.sh restart"
echo -e "${NC}"

# 显示容器状态
echo -e "${BLUE}📊 当前服务状态:${NC}"
docker-compose ps