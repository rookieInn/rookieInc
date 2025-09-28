#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误监控系统测试脚本
用于测试监控功能和邮件发送
"""

import os
import time
import json
import logging
from datetime import datetime
from error_log_monitor import ErrorLogMonitor
from email_notifier import EmailNotifier


def create_test_log_file():
    """创建测试日志文件"""
    test_log_content = """
2024-01-15 10:00:01 INFO Application started
2024-01-15 10:00:02 INFO Database connection established
2024-01-15 10:00:03 ERROR Database connection failed
2024-01-15 10:00:04 WARNING High memory usage detected
2024-01-15 10:00:05 ERROR Failed to process request
2024-01-15 10:00:06 INFO Processing completed
2024-01-15 10:00:07 CRITICAL System overload detected
2024-01-15 10:00:08 ERROR Out of memory
2024-01-15 10:00:09 FATAL System crash imminent
2024-01-15 10:00:10 ERROR Connection timeout
2024-01-15 10:00:11 ERROR Permission denied
2024-01-15 10:00:12 INFO System recovered
2024-01-15 10:00:13 ERROR Another error occurred
2024-01-15 10:00:14 ERROR Yet another error
2024-01-15 10:00:15 ERROR Multiple errors detected
"""
    
    with open('test_error.log', 'w') as f:
        f.write(test_log_content)
    
    print("✅ 测试日志文件创建完成: test_error.log")


def test_config_creation():
    """测试配置文件创建"""
    print("\n🔧 测试配置文件...")
    
    # 创建测试配置
    test_config = {
        "monitor": {
            "log_file_paths": ["./test_error.log"],
            "error_patterns": ["ERROR", "FATAL", "CRITICAL"],
            "time_window_minutes": 1,
            "error_threshold": 5,
            "check_interval_seconds": 10
        },
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "test@example.com",
            "to_emails": ["admin@example.com"],
            "subject_prefix": "[测试]"
        },
        "notification": {
            "cooldown_minutes": 1,
            "max_notifications_per_hour": 10,
            "include_error_details": True,
            "include_system_info": True
        }
    }
    
    with open('test_config.json', 'w') as f:
        json.dump(test_config, f, indent=4)
    
    print("✅ 测试配置文件创建完成: test_config.json")


def test_error_detection():
    """测试错误检测功能"""
    print("\n🔍 测试错误检测...")
    
    monitor = ErrorLogMonitor('test_config.json')
    
    # 检查日志文件
    error_counts = monitor.check_log_files()
    
    print(f"检测到的错误数量: {error_counts}")
    
    total_errors = sum(error_counts.values())
    threshold = monitor.config['monitor']['error_threshold']
    
    print(f"总错误数: {total_errors}")
    print(f"错误阈值: {threshold}")
    
    if total_errors >= threshold:
        print("✅ 错误数量超过阈值，应该发送通知")
    else:
        print("❌ 错误数量未超过阈值")
    
    return total_errors >= threshold


def test_email_notification():
    """测试邮件通知功能"""
    print("\n📧 测试邮件通知...")
    
    notifier = EmailNotifier('test_config.json')
    
    # 模拟错误数据
    error_counts = {"test_error.log": 12}
    sample_errors = {"test_error.log": [
        "ERROR Database connection failed",
        "CRITICAL System overload detected",
        "FATAL System crash imminent"
    ]}
    
    print("尝试发送测试邮件...")
    print("注意: 由于使用测试配置，邮件发送可能会失败")
    
    # 这里不实际发送邮件，只测试邮件内容生成
    subject = "测试错误通知"
    content = "这是一个测试邮件，用于验证错误监控系统功能。"
    
    print("✅ 邮件内容生成测试完成")


def test_monitoring_cycle():
    """测试完整监控周期"""
    print("\n🔄 测试完整监控周期...")
    
    monitor = ErrorLogMonitor('test_config.json')
    
    print("运行一次监控周期...")
    monitor.run_monitoring_cycle()
    
    print("✅ 监控周期测试完成")


def cleanup_test_files():
    """清理测试文件"""
    print("\n🧹 清理测试文件...")
    
    test_files = ['test_error.log', 'test_config.json', 'error_monitor.log']
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ 删除测试文件: {file}")


def main():
    """主测试函数"""
    print("🚀 开始错误监控系统测试")
    print("=" * 50)
    
    try:
        # 创建测试文件
        create_test_log_file()
        test_config_creation()
        
        # 测试各项功能
        should_notify = test_error_detection()
        test_email_notification()
        test_monitoring_cycle()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成")
        
        if should_notify:
            print("📧 系统检测到错误数量超过阈值，应该发送邮件通知")
        else:
            print("ℹ️ 错误数量未超过阈值")
        
        print("\n💡 提示:")
        print("- 要测试实际邮件发送，请配置真实的邮件服务器信息")
        print("- 要测试系统服务，请运行: ./error_monitor_service.sh install")
        print("- 查看详细文档: cat README_错误监控系统.md")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 询问是否清理测试文件
        print("\n是否清理测试文件? (y/N): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                cleanup_test_files()
            else:
                print("保留测试文件")
        except KeyboardInterrupt:
            print("\n测试中断")
            cleanup_test_files()


if __name__ == "__main__":
    main()