#!/bin/bash
# 直播间管理系统快速启动脚本

echo "直播间管理系统启动脚本"
echo "========================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖包..."
python3 -c "import flask, flask_sqlalchemy, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖包..."
    python3 -m pip install -r requirements.txt --break-system-packages --user
fi

# 初始化数据库
echo "初始化数据库..."
python3 -c "from app import init_db; init_db(); print('数据库初始化完成')"

# 启动系统
echo "启动直播间管理系统..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止系统"
echo ""

python3 run.py --init-db --port 5000