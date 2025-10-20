#!/bin/bash

# 网易云脏字过滤Java SDK 运行示例脚本

echo "=========================================="
echo "网易云脏字过滤 Java SDK 示例"
echo "=========================================="

# 检查Java版本
echo "检查Java环境..."
java -version
if [ $? -ne 0 ]; then
    echo "错误：未找到Java环境，请先安装Java 11或更高版本"
    exit 1
fi

# 检查Maven
echo "检查Maven环境..."
mvn -version
if [ $? -ne 0 ]; then
    echo "错误：未找到Maven环境，请先安装Maven 3.6或更高版本"
    exit 1
fi

# 编译项目
echo "编译项目..."
mvn clean compile
if [ $? -ne 0 ]; then
    echo "错误：项目编译失败"
    exit 1
fi

# 运行测试
echo "运行测试..."
mvn test
if [ $? -ne 0 ]; then
    echo "警告：测试运行失败，但继续执行示例"
fi

# 运行示例
echo "运行示例程序..."
echo "注意：请先配置正确的API密钥"
echo ""

# 检查配置文件
if [ ! -f "src/main/resources/application.properties" ]; then
    echo "创建配置文件..."
    cat > src/main/resources/application.properties << EOF
# 网易云脏字过滤配置
# 请替换为实际的API密钥
netease.profanity.access-key-id=your_access_key_id
netease.profanity.access-key-secret=your_access_key_secret
netease.profanity.endpoint=https://censor.netease.im
netease.profanity.timeout=30000
netease.profanity.connect-timeout=10000
netease.profanity.debug=true
EOF
fi

# 运行示例
mvn exec:java -Dexec.mainClass="com.netease.profanity.filter.example.ProfanityFilterExample" -Dexec.args=""

echo ""
echo "=========================================="
echo "示例运行完成"
echo "=========================================="
echo ""
echo "使用说明："
echo "1. 请先配置正确的API密钥"
echo "2. 修改 src/main/resources/application.properties 文件"
echo "3. 重新运行此脚本"
echo ""
echo "更多信息请查看 README.md 和 使用说明.md"