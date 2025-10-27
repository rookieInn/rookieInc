#!/bin/bash
# 微信支付模块安装脚本

echo "🚀 开始安装微信支付模块..."
echo "=" * 50

# 检查Python版本
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 安装依赖包
echo "安装Python依赖包..."
pip3 install -r wechat_pay_requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖包安装失败"
    exit 1
fi

# 创建必要的目录
echo "创建必要目录..."
mkdir -p cert
mkdir -p logs

# 设置权限
echo "设置文件权限..."
chmod +x wechat_pay_api.py
chmod +x wechat_pay_core.py
chmod +x wechat_pay_example.py

# 检查配置文件
echo "检查配置文件..."
if [ ! -f "wechat_pay_config.ini" ]; then
    echo "⚠️  配置文件不存在，请先配置 wechat_pay_config.ini"
    echo "📝 参考 wechat_pay_config.ini 中的示例配置"
fi

# 检查证书文件
echo "检查证书文件..."
if [ ! -f "cert/apiclient_cert.pem" ] || [ ! -f "cert/apiclient_key.pem" ]; then
    echo "⚠️  证书文件不存在，请将微信支付证书文件放在 cert/ 目录下"
    echo "📁 需要的文件："
    echo "   - cert/apiclient_cert.pem"
    echo "   - cert/apiclient_key.pem"
fi

echo ""
echo "✅ 微信支付模块安装完成！"
echo "=" * 50
echo "📖 使用说明："
echo "1. 配置 wechat_pay_config.ini 文件"
echo "2. 将微信支付证书文件放在 cert/ 目录下"
echo "3. 启动API服务: python3 wechat_pay_api.py"
echo "4. 访问 http://localhost:5000 查看API文档"
echo "5. 运行示例: python3 wechat_pay_example.py"
echo "=" * 50