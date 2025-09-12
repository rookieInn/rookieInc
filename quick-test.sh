#!/bin/bash

# 快速测试脚本

echo "=== Java Fluentd 快速测试 ==="

# 构建项目
echo "构建Java项目..."
mvn clean compile

# 启动Fluentd（使用简化配置）
echo "启动Fluentd..."
docker run -d --name fluentd-test \
  -p 24224:24224 \
  -v $(pwd)/fluentd-simple.conf:/fluentd/etc/fluent.conf \
  fluent/fluentd:v1.16-debian-1

# 等待Fluentd启动
sleep 5

# 运行Java应用
echo "运行Java应用..."
java -cp target/classes:$(mvn dependency:build-classpath -q -Dmdep.outputFile=/dev/stdout) com.example.fluentd.FluentdLoggingExample

# 查看Fluentd日志
echo "查看Fluentd接收到的日志:"
docker logs fluentd-test

# 清理
echo "清理测试容器..."
docker stop fluentd-test
docker rm fluentd-test

echo "测试完成！"