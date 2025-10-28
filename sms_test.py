#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信服务测试代码
"""

import json
import time
from sms_service import SMSManager, SMSProvider, SMSConfig


def test_sms_manager():
    """测试短信管理器"""
    print("=== 短信服务测试 ===")
    
    # 创建短信管理器
    sms_manager = SMSManager("sms_config.json")
    
    # 显示服务提供商状态
    print("\n1. 服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}:")
        print(f"    提供商: {info['provider']}")
        print(f"    启用状态: {info['enabled']}")
        print(f"    优先级: {info['priority']}")
        print(f"    每日限制: {info['daily_limit']}")
        print(f"    今日已发送: {info['daily_sent']}")
        print(f"    总发送量: {info['total_sent']}")
        print(f"    成功率: {info['success_rate']:.2%}")
        print(f"    余额: {info['balance']:.2f}元")
        print()
    
    # 测试发送短信（这里使用测试手机号，实际使用时请替换）
    test_phone = "13800138000"  # 请替换为实际手机号
    test_content = "您的验证码是123456，5分钟内有效。"
    template_params = {"code": "123456"}
    
    print(f"2. 发送测试短信到: {test_phone}")
    print(f"   内容: {test_content}")
    
    # 发送短信
    result = sms_manager.send_sms(
        phone=test_phone,
        content=test_content,
        template_params=template_params
    )
    
    if result.success:
        print(f"   ✅ 短信发送成功!")
        print(f"   消息ID: {result.message_id}")
        print(f"   使用提供商: {result.provider}")
        print(f"   发送时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.send_time))}")
    else:
        print(f"   ❌ 短信发送失败!")
        print(f"   错误代码: {result.error_code}")
        print(f"   错误信息: {result.error_message}")
        print(f"   使用提供商: {result.provider}")
    
    # 再次显示状态（查看统计更新）
    print("\n3. 发送后的服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        if info['total_sent'] > 0:
            print(f"  {name}: 总发送 {info['total_sent']} 条，成功 {info['success_count']} 条")


def test_provider_switching():
    """测试服务提供商切换"""
    print("\n=== 服务提供商切换测试 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 显示当前状态
    print("1. 当前服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")
    
    # 测试禁用主服务提供商
    print("\n2. 禁用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", False)
    
    # 显示切换后状态
    print("3. 切换后的服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")
    
    # 重新启用主服务提供商
    print("\n4. 重新启用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", True)
    
    # 显示最终状态
    print("5. 最终服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")


def test_daily_limit():
    """测试每日限制功能"""
    print("\n=== 每日限制测试 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 模拟达到每日限制
    print("1. 模拟达到每日限制...")
    for name in sms_manager.usage_stats:
        sms_manager.usage_stats[name]["daily_sent"] = 999  # 接近限制
    
    # 尝试发送短信
    print("2. 尝试发送短信...")
    result = sms_manager.send_sms(
        phone="13800138000",
        content="测试每日限制",
        template_params={}
    )
    
    if result.success:
        print("   ✅ 短信发送成功（未达到限制）")
    else:
        print(f"   ❌ 短信发送失败: {result.error_message}")
    
    # 重置每日计数
    print("3. 重置每日计数...")
    for name in sms_manager.usage_stats:
        sms_manager.usage_stats[name]["daily_sent"] = 0
        sms_manager.usage_stats[name]["last_reset_date"] = time.strftime("%Y-%m-%d")
    
    print("   每日计数已重置")


def test_configuration_management():
    """测试配置管理"""
    print("\n=== 配置管理测试 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 添加新的服务提供商配置
    print("1. 添加新的服务提供商配置...")
    new_config = SMSConfig(
        provider=SMSProvider.ALIYUN,
        access_key="NEW_ACCESS_KEY",
        secret_key="NEW_SECRET_KEY",
        sign_name="新签名",
        template_id="SMS_NEW_TEMPLATE",
        enabled=True,
        priority=4,
        daily_limit=500
    )
    
    sms_manager.configs["new_provider"] = new_config
    sms_manager.save_config()
    print("   新配置已添加并保存")
    
    # 显示所有配置
    print("2. 当前所有配置:")
    for name, config in sms_manager.configs.items():
        print(f"  {name}: {config.provider.value} - 优先级: {config.priority}")


def create_demo_config():
    """创建演示配置"""
    print("\n=== 创建演示配置 ===")
    
    demo_config = {
        "providers": {
            "aliyun_demo": {
                "provider": "aliyun",
                "access_key": "LTAI5txxxxxxxxxxxxxxxxx",
                "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "sign_name": "演示签名",
                "template_id": "SMS_123456789",
                "endpoint": "https://dysmsapi.aliyuncs.com",
                "region": "cn-hangzhou",
                "enabled": True,
                "priority": 1,
                "daily_limit": 100,
                "cost_per_sms": 0.045
            },
            "tencent_demo": {
                "provider": "tencent",
                "access_key": "AKIDxxxxxxxxxxxxxxxxxxxx",
                "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
                "sign_name": "演示签名",
                "template_id": "1234567",
                "endpoint": "https://sms.tencentcloudapi.com",
                "region": "ap-beijing",
                "enabled": True,
                "priority": 2,
                "daily_limit": 100,
                "cost_per_sms": 0.045
            }
        },
        "default_provider": "aliyun_demo",
        "fallback_enabled": True,
        "retry_count": 3,
        "retry_delay": 1
    }
    
    with open("sms_demo_config.json", "w", encoding="utf-8") as f:
        json.dump(demo_config, f, ensure_ascii=False, indent=2)
    
    print("   演示配置文件已创建: sms_demo_config.json")
    print("   请将配置中的密钥替换为真实的API密钥")


if __name__ == "__main__":
    try:
        # 运行所有测试
        test_sms_manager()
        test_provider_switching()
        test_daily_limit()
        test_configuration_management()
        create_demo_config()
        
        print("\n=== 所有测试完成 ===")
        print("注意: 由于使用的是测试配置，短信发送可能会失败。")
        print("请将配置文件中的密钥替换为真实的API密钥后再进行实际测试。")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()