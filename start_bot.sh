#!/bin/bash
# 微信群ChatGPT机器人启动脚本

echo "🤖 微信群ChatGPT机器人启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查依赖包
echo "📦 检查依赖包..."
if ! python3 -c "import itchat, openai, aiohttp" &> /dev/null; then
    echo "⚠️  依赖包未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
    echo "✅ 依赖包安装完成"
fi

# 检查配置文件
if [ ! -f "bot_config.ini" ] && [ ! -f "bot_config_advanced.ini" ]; then
    echo "⚠️  配置文件不存在，将创建默认配置"
fi

# 选择运行版本
echo ""
echo "请选择要运行的版本："
echo "1) 基础版本 (wechat_chatgpt_bot.py)"
echo "2) 高级版本 (wechat_bot_advanced.py)"
echo "3) 退出"
echo ""

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🚀 启动基础版本..."
        python3 wechat_chatgpt_bot.py
        ;;
    2)
        echo "🚀 启动高级版本..."
        python3 wechat_bot_advanced.py
        ;;
    3)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac