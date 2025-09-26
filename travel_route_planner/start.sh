#!/bin/bash

# AI旅游路线规划系统启动脚本

echo "正在启动AI旅游路线规划系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查数据库连接
echo "检查数据库连接..."
python -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='password', database='travel_planner')
    print('数据库连接成功')
    conn.close()
except Exception as e:
    print(f'数据库连接失败: {e}')
    print('请确保MySQL服务正在运行，并创建travel_planner数据库')
    exit(1)
"

# 初始化数据库
echo "初始化数据库..."
python -c "
from database.database import init_db
init_db()
print('数据库初始化完成')
"

# 启动应用
echo "启动应用服务器..."
python main.py