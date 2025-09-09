#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置和运行脚本
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        return False
    print(f"✓ Python版本: {sys.version}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("安装依赖包...")
    
    try:
        # 尝试使用pip安装
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 依赖包安装成功")
            return True
        else:
            print(f"✗ 依赖包安装失败: {result.stderr}")
            print("请手动安装依赖包:")
            print("pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"✗ 安装依赖包时出错: {e}")
        return False


def check_config():
    """检查配置文件"""
    config_file = Path("config.ini")
    
    if not config_file.exists():
        print("✗ 配置文件 config.ini 不存在")
        print("请复制 config_example.ini 为 config.ini 并填入您的配置")
        return False
    
    print("✓ 配置文件存在")
    
    # 检查配置内容
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        
        # 检查是否有占位符
        placeholder_found = False
        for section in config.sections():
            for key, value in config.items(section):
                if 'YOUR_' in value or 'test_' in value:
                    print(f"⚠️  请更新配置: [{section}] {key} = {value}")
                    placeholder_found = True
        
        if not placeholder_found:
            print("✓ 配置文件看起来已正确配置")
            return True
        else:
            print("请更新配置文件中的占位符值")
            return False
            
    except Exception as e:
        print(f"✗ 配置文件解析失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    directories = ["temp", "output"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ 创建目录: {dir_name}")
    
    return True


def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("阿里云OSS到百度云盘迁移工具")
    print("="*60)
    print()
    print("使用步骤:")
    print("1. 确保已正确配置 config.ini 文件")
    print("2. 运行迁移程序:")
    print("   python3 oss_to_baidupan.py")
    print()
    print("配置说明:")
    print("- aliyun_oss: 阿里云OSS访问凭证")
    print("- baidu_pan: 百度云盘访问令牌")
    print("- general: 目标年份和目录设置")
    print()
    print("注意事项:")
    print("⚠️  此操作会永久删除OSS中的原始文件夹")
    print("⚠️  请确保数据已正确备份")
    print("⚠️  建议先在测试环境中验证")
    print()


def main():
    """主函数"""
    print("阿里云OSS到百度云盘迁移工具 - 设置向导")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 创建目录
    create_directories()
    
    # 检查配置文件
    config_ok = check_config()
    
    # 尝试安装依赖
    deps_ok = install_dependencies()
    
    print("\n" + "="*50)
    print("设置状态:")
    print(f"Python版本: {'✓' if check_python_version() else '✗'}")
    print(f"配置文件: {'✓' if config_ok else '✗'}")
    print(f"依赖包: {'✓' if deps_ok else '✗'}")
    
    if config_ok and deps_ok:
        print("\n✓ 所有检查通过！可以开始使用程序")
        show_usage()
        return True
    else:
        print("\n✗ 请解决上述问题后重新运行")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)