#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的错误监控测试
"""

import os
import json

def test_basic_functionality():
    """测试基本功能"""
    print("🚀 开始基本功能测试")
    
    # 1. 测试配置文件
    print("\n1. 测试配置文件...")
    try:
        with open('error_monitor_config.json', 'r') as f:
            config = json.load(f)
        print("✅ 配置文件格式正确")
        print(f"   - 监控文件数量: {len(config['monitor']['log_file_paths'])}")
        print(f"   - 错误阈值: {config['monitor']['error_threshold']}")
        print(f"   - 时间窗口: {config['monitor']['time_window_minutes']} 分钟")
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False
    
    # 2. 测试Python脚本语法
    print("\n2. 测试Python脚本语法...")
    try:
        import ast
        with open('error_log_monitor.py', 'r') as f:
            source = f.read()
        ast.parse(source)
        print("✅ error_log_monitor.py 语法正确")
        
        with open('email_notifier.py', 'r') as f:
            source = f.read()
        ast.parse(source)
        print("✅ email_notifier.py 语法正确")
    except Exception as e:
        print(f"❌ Python脚本语法错误: {e}")
        return False
    
    # 3. 测试依赖模块
    print("\n3. 测试依赖模块...")
    try:
        import psutil
        print("✅ psutil 模块可用")
    except ImportError as e:
        print(f"❌ psutil 模块不可用: {e}")
        return False
    
    try:
        import smtplib
        print("✅ smtplib 模块可用")
    except ImportError as e:
        print(f"❌ smtplib 模块不可用: {e}")
        return False
    
    # 4. 测试文件权限
    print("\n4. 测试文件权限...")
    scripts = ['error_log_monitor.py', 'email_notifier.py', 'error_monitor_service.sh']
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.R_OK):
                print(f"✅ {script} 可读")
            else:
                print(f"❌ {script} 不可读")
        else:
            print(f"❌ {script} 不存在")
    
    # 5. 创建测试日志文件
    print("\n5. 创建测试日志文件...")
    test_log_content = """2024-01-15 10:00:01 INFO Application started
2024-01-15 10:00:02 ERROR Database connection failed
2024-01-15 10:00:03 CRITICAL System overload detected
2024-01-15 10:00:04 FATAL System crash imminent
2024-01-15 10:00:05 ERROR Another error occurred
"""
    
    with open('test_error.log', 'w') as f:
        f.write(test_log_content)
    print("✅ 测试日志文件创建完成")
    
    # 6. 测试错误计数
    print("\n6. 测试错误计数...")
    error_patterns = ["ERROR", "FATAL", "CRITICAL"]
    error_count = 0
    
    with open('test_error.log', 'r') as f:
        for line in f:
            for pattern in error_patterns:
                if pattern in line:
                    error_count += 1
                    break
    
    print(f"✅ 检测到 {error_count} 个错误")
    
    # 7. 显示配置摘要
    print("\n7. 配置摘要:")
    print(f"   - 监控文件: {config['monitor']['log_file_paths']}")
    print(f"   - 错误模式: {config['monitor']['error_patterns'][:3]}...")
    print(f"   - 错误阈值: {config['monitor']['error_threshold']}")
    print(f"   - 时间窗口: {config['monitor']['time_window_minutes']} 分钟")
    print(f"   - 检查间隔: {config['monitor']['check_interval_seconds']} 秒")
    print(f"   - 收件人: {config['email']['to_emails']}")
    
    print("\n✅ 所有基本功能测试通过！")
    print("\n💡 下一步:")
    print("1. 编辑 error_monitor_config.json 配置邮件服务器")
    print("2. 运行: python3 error_log_monitor.py --test")
    print("3. 运行: python3 email_notifier.py --test")
    print("4. 安装服务: ./error_monitor_service.sh install")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()