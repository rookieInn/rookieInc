#!/bin/bash

# 短信服务启动脚本

echo "=========================================="
echo "        短信服务系统启动脚本"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖包..."
if ! python3 -c "import requests, flask" 2>/dev/null; then
    echo "📦 安装依赖包..."
    pip3 install requests flask
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败，请手动安装: pip3 install requests flask"
        exit 1
    fi
fi

# 检查配置文件
if [ ! -f "sms_config.json" ]; then
    echo "📝 创建默认配置文件..."
    python3 -c "
from sms_service import SMSManager
sms_manager = SMSManager('sms_config.json')
print('✅ 默认配置文件已创建: sms_config.json')
print('请编辑配置文件，填入您的API密钥')
"
fi

# 显示菜单
echo ""
echo "请选择启动模式:"
echo "1. 启动Web管理界面 (推荐)"
echo "2. 运行测试代码"
echo "3. 运行使用示例"
echo "4. 查看服务状态"
echo "5. 退出"

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "🚀 启动Web管理界面..."
        echo "访问地址: http://localhost:5000"
        echo "按 Ctrl+C 停止服务"
        python3 sms_web_admin.py
        ;;
    2)
        echo "🧪 运行测试代码..."
        python3 sms_test.py
        ;;
    3)
        echo "📚 运行使用示例..."
        python3 sms_example.py
        ;;
    4)
        echo "📊 查看服务状态..."
        python3 -c "
from sms_service import SMSManager
sms_manager = SMSManager('sms_config.json')
status = sms_manager.get_provider_status()
print('服务提供商状态:')
for name, info in status.items():
    print(f'  {name}: {info[\"provider\"]} - {\"启用\" if info[\"enabled\"] else \"禁用\"} - 成功率: {info[\"success_rate\"]:.2%}')
"
        ;;
    5)
        echo "👋 再见!"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，请重新运行脚本"
        exit 1
        ;;
esac