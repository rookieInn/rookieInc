#!/bin/bash
# Maven Wrapper Script for Spring Boot API Timing Application

# 检查是否安装了Maven
if command -v mvn &> /dev/null; then
    echo "使用系统Maven..."
    exec mvn "$@"
else
    echo "未找到Maven，请先安装Maven或使用以下命令："
    echo "  Ubuntu/Debian: sudo apt-get install maven"
    echo "  CentOS/RHEL: sudo yum install maven"
    echo "  macOS: brew install maven"
    echo "  Windows: 下载并安装Maven"
    exit 1
fi