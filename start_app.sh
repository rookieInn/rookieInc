#!/bin/bash

# Spring Boot 应用程序启动脚本

echo "=== 启动 Spring Boot API 处理时间计算应用程序 ==="
echo ""

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "错误: 未找到Java环境，请先安装Java 11或更高版本"
    exit 1
fi

# 检查Maven环境
if ! command -v mvn &> /dev/null; then
    echo "错误: 未找到Maven环境，请先安装Maven"
    exit 1
fi

echo "Java版本:"
java -version
echo ""

echo "Maven版本:"
mvn -version
echo ""

# 编译项目
echo "正在编译项目..."
mvn clean compile

if [ $? -ne 0 ]; then
    echo "编译失败，请检查代码"
    exit 1
fi

echo "编译成功！"
echo ""

# 启动应用程序
echo "正在启动应用程序..."
echo "应用程序将在 http://localhost:8080 启动"
echo "按 Ctrl+C 停止应用程序"
echo ""

mvn spring-boot:run