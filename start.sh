#!/bin/bash

# 直播管理后台系统启动脚本

echo "🚀 启动直播管理后台系统..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

# 检查MongoDB是否运行
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB 未运行，请先启动 MongoDB"
    echo "   启动命令: sudo systemctl start mongod 或 mongod"
fi

# 检查Redis是否运行
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis 未运行，请先启动 Redis"
    echo "   启动命令: sudo systemctl start redis 或 redis-server"
fi

# 安装依赖
echo "📦 安装依赖..."
npm install

# 安装前端依赖
echo "📦 安装前端依赖..."
cd client
npm install
cd ..

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p logs uploads

# 启动服务
echo "🎯 启动服务..."
echo "   后端服务: http://localhost:3000"
echo "   前端服务: http://localhost:3001"
echo "   健康检查: http://localhost:3000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev