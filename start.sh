#!/bin/bash

# Spring Boot 图形验证码演示启动脚本

echo "🚀 启动 Spring Boot 图形验证码演示..."

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "❌ 错误: 未找到Java环境，请先安装Java 11+"
    exit 1
fi

# 检查Maven环境
if ! command -v mvn &> /dev/null; then
    echo "❌ 错误: 未找到Maven环境，请先安装Maven 3.6+"
    exit 1
fi

# 检查Redis服务
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  警告: 未找到Redis客户端，请确保Redis服务正在运行"
else
    # 测试Redis连接
    if ! redis-cli ping &> /dev/null; then
        echo "⚠️  警告: 无法连接到Redis服务，请确保Redis服务正在运行"
        echo "   启动Redis: sudo systemctl start redis-server"
        echo "   或使用Docker: docker run -d --name redis -p 6379:6379 redis:latest"
    else
        echo "✅ Redis服务连接正常"
    fi
fi

# 编译项目
echo "📦 编译项目..."
mvn clean compile

if [ $? -ne 0 ]; then
    echo "❌ 编译失败"
    exit 1
fi

echo "✅ 编译成功"

# 启动应用
echo "🌟 启动应用..."
echo "   访问地址: http://localhost:8080"
echo "   演示页面: http://localhost:8080/demo"
echo "   API接口: http://localhost:8080/api/captcha/generate"
echo ""
echo "按 Ctrl+C 停止应用"

mvn spring-boot:run