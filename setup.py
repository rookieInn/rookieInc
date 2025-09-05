#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装和设置脚本
"""

import os
import subprocess
import sys

def install_requirements():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def create_config_template():
    """创建配置模板"""
    config_content = """# SQL查询结果推送到腾讯文档配置文件

[database]
# 数据库连接配置
host = localhost
port = 3306
user = root
password = your_password
database = your_database

[tencent_docs]
# 腾讯文档API配置
# 获取方式：https://docs.qq.com/openapi/getAccessToken
access_token = your_access_token
# 腾讯文档文件ID，从文档URL中获取
file_id = your_file_id

[logging]
# 日志级别：DEBUG, INFO, WARNING, ERROR
level = INFO
# 日志文件路径
log_file = sql_to_docs.log
"""
    
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ 配置文件模板已创建: config.ini")
        print("📝 请编辑 config.ini 文件，填入你的数据库和腾讯文档配置")
    else:
        print("ℹ️  配置文件 config.ini 已存在")

def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎉 安装完成！")
    print("="*60)
    print("\n📋 使用步骤：")
    print("1. 编辑 config.ini 文件，配置数据库和腾讯文档信息")
    print("2. 运行快速测试: python quick_start.py")
    print("3. 查看示例代码: python example_usage.py")
    print("4. 自定义你的SQL查询并运行")
    
    print("\n📚 文档：")
    print("- 详细说明: README_sql_to_docs.md")
    print("- 使用示例: example_usage.py")
    print("- 快速启动: quick_start.py")
    
    print("\n🔧 配置说明：")
    print("- 数据库配置: 修改 config.ini 中的 [database] 部分")
    print("- 腾讯文档配置: 修改 config.ini 中的 [tencent_docs] 部分")
    print("- 获取腾讯文档Token: https://docs.qq.com/openapi/getAccessToken")

def main():
    """主函数"""
    print("🚀 SQL查询结果推送到腾讯文档 - 安装脚本")
    print("="*50)
    
    # 安装依赖
    if not install_requirements():
        print("❌ 安装失败，请手动安装依赖包")
        return
    
    # 创建配置模板
    create_config_template()
    
    # 显示使用说明
    show_usage()

if __name__ == "__main__":
    main()