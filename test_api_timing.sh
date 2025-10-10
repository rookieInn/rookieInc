#!/bin/bash

# Spring Boot API 处理时间测试脚本
# 用于测试各种API接口的处理时间计算功能

BASE_URL="http://localhost:8080"

echo "=== Spring Boot API 处理时间测试 ==="
echo "确保应用程序已启动在端口 8080"
echo ""

# 等待应用程序启动
echo "等待应用程序启动..."
sleep 3

# 测试快速响应接口
echo "1. 测试快速响应接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/quick" | head -5
echo ""

# 测试模拟处理时间接口
echo "2. 测试模拟处理时间接口 (延迟1秒)..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/process?delay=1000" | head -5
echo ""

# 测试数据库查询模拟接口
echo "3. 测试数据库查询模拟接口 (10条记录)..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/database?records=10" | head -5
echo ""

# 测试文件处理模拟接口
echo "4. 测试文件处理模拟接口..."
curl -s -X POST -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/file?filename=test.txt&size=2048" | head -5
echo ""

# 测试复杂业务逻辑模拟接口
echo "5. 测试复杂业务逻辑模拟接口 (3个步骤)..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/complex?steps=3" | head -5
echo ""

# 测试健康检查接口（不计算处理时间）
echo "6. 测试健康检查接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/health" | head -5
echo ""

# 测试服务接口（使用AOP注解）
echo "7. 测试快速业务服务接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/service/quick" | head -5
echo ""

echo "8. 测试慢速业务服务接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/service/slow" | head -5
echo ""

echo "9. 测试数据库操作服务接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/service/database?records=15" | head -5
echo ""

echo "10. 测试文件处理服务接口..."
curl -s -X POST -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/service/file?filename=service_test.txt&fileSize=4096" | head -5
echo ""

echo "11. 测试复杂计算服务接口..."
curl -s -w "\n响应时间: %{time_total}s\n状态码: %{http_code}\n" "$BASE_URL/api/service/calculation?iterations=50000" | head -5
echo ""

echo "=== 测试完成 ==="
echo "请查看应用程序日志以查看详细的处理时间信息"
echo "每个响应都包含 X-Processing-Time 响应头"