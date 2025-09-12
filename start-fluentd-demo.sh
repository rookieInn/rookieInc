#!/bin/bash

# Java接入Fluentd日志采集演示脚本

echo "=== Java接入Fluentd日志采集演示 ==="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 构建Java应用
echo "1. 构建Java应用..."
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo "错误: Maven构建失败"
    exit 1
fi

# 启动Fluentd和相关服务
echo "2. 启动Fluentd和相关服务..."
docker-compose -f docker-compose-fluentd.yml up -d fluentd

# 等待Fluentd启动
echo "等待Fluentd启动..."
sleep 10

# 运行Java应用
echo "3. 运行Java应用..."
echo "Java应用将运行30秒，生成各种类型的日志..."
echo "日志将同时输出到控制台、文件和Fluentd"
echo ""

java -cp target/classes:target/dependency/* com.example.fluentd.FluentdLoggingExample

echo ""
echo "4. 查看日志文件..."
echo "应用日志文件:"
ls -la logs/

echo ""
echo "5. 查看Fluentd日志..."
echo "Fluentd容器日志:"
docker logs fluentd-server --tail 20

echo ""
echo "=== 演示完成 ==="
echo "您可以："
echo "1. 查看 logs/application.log 文件"
echo "2. 查看Fluentd容器日志: docker logs fluentd-server"
echo "3. 启动Elasticsearch和Kibana进行日志分析:"
echo "   docker-compose -f docker-compose-fluentd.yml up -d elasticsearch kibana"
echo "4. 访问 http://localhost:5601 查看Kibana界面"