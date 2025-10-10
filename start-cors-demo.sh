#!/bin/bash

# Spring Boot CORS Demo 启动脚本

echo "=========================================="
echo "Spring Boot CORS Demo 启动脚本"
echo "=========================================="

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "❌ 错误: 未找到Java环境，请先安装Java 11或更高版本"
    exit 1
fi

# 检查Maven环境
if ! command -v mvn &> /dev/null; then
    echo "❌ 错误: 未找到Maven环境，请先安装Maven"
    exit 1
fi

echo "✅ Java版本:"
java -version

echo ""
echo "✅ Maven版本:"
mvn -version

echo ""
echo "🚀 开始启动Spring Boot CORS Demo..."

# 清理并编译项目
echo "📦 正在编译项目..."
mvn clean compile

if [ $? -ne 0 ]; then
    echo "❌ 编译失败，请检查代码"
    exit 1
fi

echo "✅ 编译成功"

# 启动应用
echo "🌐 正在启动Spring Boot应用..."
echo ""
echo "访问地址:"
echo "  - 应用首页: http://localhost:8080"
echo "  - 测试页面: http://localhost:8080/test.html"
echo "  - API测试: http://localhost:8080/api/test"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""

mvn spring-boot:run