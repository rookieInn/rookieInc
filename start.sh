#!/bin/bash

# 微信公众号代理服务器启动脚本

set -e

echo "正在启动微信公众号代理服务器..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 检查依赖是否安装
if [ ! -f "requirements.txt" ]; then
    echo "错误: requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "警告: config.yaml 文件不存在，将使用默认配置"
fi

# 创建日志目录
mkdir -p logs

# 设置权限
chmod +x wechat_proxy.py

# 启动服务
echo "正在启动代理服务器..."
python3 wechat_proxy.py