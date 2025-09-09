#!/bin/bash

# Chrome书签同步启动脚本

echo "Chrome书签同步到Edge浏览器"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要Python 3.6或更高版本"
    exit 1
fi

# 检查脚本文件
if [ ! -f "chrome_to_edge_sync.py" ]; then
    echo "错误: 找不到chrome_to_edge_sync.py文件"
    exit 1
fi

# 显示菜单
echo ""
echo "请选择操作："
echo "1) 运行一次同步"
echo "2) 启动定期同步"
echo "3) 运行简化版本"
echo "4) 运行功能测试"
echo "5) 查看配置"
echo "6) 退出"
echo ""

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo "运行一次同步..."
        python3 chrome_to_edge_sync.py --once
        ;;
    2)
        echo "启动定期同步（按Ctrl+C停止）..."
        python3 chrome_to_edge_sync.py
        ;;
    3)
        echo "运行简化版本..."
        python3 bookmark_sync_manual.py
        ;;
    4)
        echo "运行功能测试..."
        python3 test_bookmark_sync.py
        ;;
    5)
        echo "当前配置："
        if [ -f "bookmark_sync_config.json" ]; then
            cat bookmark_sync_config.json
        else
            echo "配置文件不存在"
        fi
        ;;
    6)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac