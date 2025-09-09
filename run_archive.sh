#!/bin/bash

# OSS文件归档脚本运行脚本

echo "开始运行OSS文件归档脚本..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 运行脚本
echo "运行归档脚本..."
python3 oss_archive_script.py

echo "脚本执行完成，请查看日志文件 oss_archive.log"