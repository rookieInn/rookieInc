#!/bin/bash
# 分账程序快速启动脚本

echo "分账程序快速启动"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "split_bill_app.py" ]; then
    echo "错误: 请在包含split_bill_app.py的目录中运行此脚本"
    exit 1
fi

# 安装依赖（如果需要）
echo "检查依赖包..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install --break-system-packages -r requirements_split_bill.txt
    if [ $? -ne 0 ]; then
        echo "依赖包安装失败，请手动安装："
        echo "pip3 install --break-system-packages -r requirements_split_bill.txt"
        exit 1
    fi
fi

# 初始化演示数据（如果数据库不存在）
if [ ! -f "split_bills.db" ]; then
    echo "初始化演示数据..."
    python3 demo_split_bill.py
fi

# 启动程序
echo "启动分账程序..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止程序"
echo "=================="

python3 split_bill_app.py