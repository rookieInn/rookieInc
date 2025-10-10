#!/bin/bash

# CORS测试脚本

echo "=========================================="
echo "Spring Boot CORS 测试脚本"
echo "=========================================="

BASE_URL="http://localhost:8080"

# 检查服务是否运行
echo "🔍 检查服务状态..."
if ! curl -s "$BASE_URL/api/test" > /dev/null; then
    echo "❌ 服务未运行，请先启动Spring Boot应用"
    echo "   运行命令: ./start-cors-demo.sh"
    exit 1
fi

echo "✅ 服务正在运行"

echo ""
echo "🧪 开始CORS测试..."

# 测试1: 基础GET请求
echo "1️⃣ 测试GET请求..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/api/test")
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE:/d')

if [ "$http_code" = "200" ]; then
    echo "✅ GET请求成功 (HTTP $http_code)"
    echo "   响应: $body"
else
    echo "❌ GET请求失败 (HTTP $http_code)"
fi

echo ""

# 测试2: POST请求
echo "2️⃣ 测试POST请求..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"message":"CORS测试","timestamp":"'$(date -Iseconds)'"}' \
    "$BASE_URL/api/test")
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE:/d')

if [ "$http_code" = "200" ]; then
    echo "✅ POST请求成功 (HTTP $http_code)"
    echo "   响应: $body"
else
    echo "❌ POST请求失败 (HTTP $http_code)"
fi

echo ""

# 测试3: 带自定义请求头
echo "3️⃣ 测试带自定义请求头..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Custom-Header: Test-Value" \
    -H "Authorization: Bearer test-token" \
    -d '{"message":"带请求头测试"}' \
    "$BASE_URL/api/test/headers")
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE:/d')

if [ "$http_code" = "200" ]; then
    echo "✅ 带请求头测试成功 (HTTP $http_code)"
    echo "   响应: $body"
else
    echo "❌ 带请求头测试失败 (HTTP $http_code)"
fi

echo ""

# 测试4: OPTIONS预检请求
echo "4️⃣ 测试OPTIONS预检请求..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type,Authorization" \
    "$BASE_URL/api/test")
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
    echo "✅ OPTIONS预检请求成功 (HTTP $http_code)"
else
    echo "❌ OPTIONS预检请求失败 (HTTP $http_code)"
fi

echo ""

# 测试5: 复杂请求
echo "5️⃣ 测试复杂请求..."
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Custom-Header: Complex-Test" \
    -H "Authorization: Bearer complex-token" \
    -H "X-Requested-With: XMLHttpRequest" \
    -d '{"message":"复杂请求测试","data":{"userId":123}}' \
    "$BASE_URL/cors/complex-request")
http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE:/d')

if [ "$http_code" = "200" ]; then
    echo "✅ 复杂请求测试成功 (HTTP $http_code)"
    echo "   响应: $body"
else
    echo "❌ 复杂请求测试失败 (HTTP $http_code)"
fi

echo ""
echo "=========================================="
echo "🎉 CORS测试完成！"
echo "=========================================="
echo ""
echo "💡 提示:"
echo "   - 打开浏览器访问 http://localhost:8080/test.html 进行交互式测试"
echo "   - 查看完整文档: README_CORS.md"
echo ""