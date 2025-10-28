#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信服务使用示例
演示如何使用短信服务系统发送短信、管理渠道等
"""

from sms_service import SMSManager, SMSProvider, SMSConfig
import json
import time


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 1. 创建短信管理器
    sms_manager = SMSManager("sms_config.json")
    
    # 2. 发送验证码短信
    phone = "13800138000"  # 请替换为实际手机号
    verification_code = "123456"
    
    result = sms_manager.send_sms(
        phone=phone,
        content=f"您的验证码是{verification_code}，5分钟内有效。",
        template_params={"code": verification_code}
    )
    
    if result.success:
        print(f"✅ 验证码发送成功!")
        print(f"   消息ID: {result.message_id}")
        print(f"   使用提供商: {result.provider}")
    else:
        print(f"❌ 验证码发送失败: {result.error_message}")
    
    # 3. 查看服务提供商状态
    print("\n服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {info['provider']} - 成功率: {info['success_rate']:.2%}")


def example_provider_management():
    """服务提供商管理示例"""
    print("\n=== 服务提供商管理示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 1. 查看当前状态
    print("当前服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")
    
    # 2. 禁用某个服务提供商
    print("\n禁用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", False)
    
    # 3. 再次查看状态
    print("禁用后的状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")
    
    # 4. 重新启用
    print("\n重新启用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", True)
    
    print("最终状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {'启用' if info['enabled'] else '禁用'}")


def example_custom_provider():
    """自定义服务提供商示例"""
    print("\n=== 自定义服务提供商示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 1. 添加新的服务提供商配置
    new_config = SMSConfig(
        provider=SMSProvider.ALIYUN,
        access_key="YOUR_NEW_ACCESS_KEY",
        secret_key="YOUR_NEW_SECRET_KEY",
        sign_name="新签名",
        template_id="SMS_NEW_TEMPLATE",
        endpoint="https://dysmsapi.aliyuncs.com",
        region="cn-hangzhou",
        enabled=True,
        priority=1,  # 最高优先级
        daily_limit=500,
        cost_per_sms=0.04
    )
    
    # 2. 添加到管理器
    sms_manager.configs["custom_provider"] = new_config
    
    # 3. 保存配置
    sms_manager.save_config()
    print("✅ 自定义服务提供商已添加并保存")
    
    # 4. 重新初始化以加载新配置
    sms_manager.initialize_providers()
    
    # 5. 查看更新后的状态
    print("\n更新后的服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"  {name}: {info['provider']} - 优先级: {info['priority']}")


def example_batch_sending():
    """批量发送示例"""
    print("\n=== 批量发送示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 模拟批量发送
    phones = ["13800138000", "13800138001", "13800138002"]  # 请替换为实际手机号
    message = "系统维护通知：系统将于今晚22:00-24:00进行维护，期间服务可能中断。"
    
    print(f"开始批量发送短信，共 {len(phones)} 条...")
    
    success_count = 0
    failed_count = 0
    
    for i, phone in enumerate(phones, 1):
        print(f"发送第 {i}/{len(phones)} 条到 {phone}...")
        
        result = sms_manager.send_sms(
            phone=phone,
            content=message,
            template_params={}
        )
        
        if result.success:
            success_count += 1
            print(f"  ✅ 成功 - 消息ID: {result.message_id}")
        else:
            failed_count += 1
            print(f"  ❌ 失败 - {result.error_message}")
        
        # 避免发送过快
        time.sleep(1)
    
    print(f"\n批量发送完成:")
    print(f"  成功: {success_count} 条")
    print(f"  失败: {failed_count} 条")
    print(f"  成功率: {success_count / len(phones) * 100:.1f}%")


def example_monitoring():
    """监控和统计示例"""
    print("\n=== 监控和统计示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 1. 获取详细统计信息
    print("详细统计信息:")
    for name, stats in sms_manager.usage_stats.items():
        config = sms_manager.configs.get(name)
        print(f"\n{name} ({config.provider.value if config else 'unknown'}):")
        print(f"  总发送量: {stats.get('total_sent', 0)}")
        print(f"  成功数量: {stats.get('success_count', 0)}")
        print(f"  失败数量: {stats.get('error_count', 0)}")
        print(f"  今日发送: {stats.get('daily_sent', 0)}")
        print(f"  最后发送时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.get('last_send_time', 0))) if stats.get('last_send_time') else '从未发送'}")
        
        if config:
            print(f"  每日限制: {config.daily_limit or '无限制'}")
            print(f"  单条费用: ¥{config.cost_per_sms or 0:.3f}")
    
    # 2. 计算总成本
    total_cost = 0
    for name, stats in sms_manager.usage_stats.items():
        config = sms_manager.configs.get(name)
        if config and config.cost_per_sms:
            total_cost += stats.get('success_count', 0) * config.cost_per_sms
    
    print(f"\n总成本估算: ¥{total_cost:.2f}")


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 1. 发送到无效手机号
    print("测试无效手机号...")
    result = sms_manager.send_sms(
        phone="12345678901",  # 无效手机号
        content="测试消息",
        template_params={}
    )
    
    if not result.success:
        print(f"❌ 预期失败: {result.error_message}")
    
    # 2. 发送空内容
    print("\n测试空内容...")
    result = sms_manager.send_sms(
        phone="13800138000",
        content="",  # 空内容
        template_params={}
    )
    
    if not result.success:
        print(f"❌ 预期失败: {result.error_message}")
    
    # 3. 使用不存在的服务提供商
    print("\n测试不存在的服务提供商...")
    result = sms_manager.send_sms(
        phone="13800138000",
        content="测试消息",
        template_params={},
        provider_name="non_existent_provider"
    )
    
    if not result.success:
        print(f"❌ 预期失败: {result.error_message}")


def example_configuration_management():
    """配置管理示例"""
    print("\n=== 配置管理示例 ===")
    
    sms_manager = SMSManager("sms_config.json")
    
    # 1. 查看当前配置
    print("当前配置:")
    for name, config in sms_manager.configs.items():
        print(f"  {name}:")
        print(f"    提供商: {config.provider.value}")
        print(f"    签名: {config.sign_name}")
        print(f"    模板ID: {config.template_id}")
        print(f"    启用状态: {config.enabled}")
        print(f"    优先级: {config.priority}")
        print(f"    每日限制: {config.daily_limit}")
        print(f"    单条费用: ¥{config.cost_per_sms or 0:.3f}")
        print()
    
    # 2. 修改配置
    print("修改配置...")
    if "aliyun_primary" in sms_manager.configs:
        config = sms_manager.configs["aliyun_primary"]
        config.priority = 2  # 降低优先级
        config.daily_limit = 200  # 修改每日限制
        config.cost_per_sms = 0.05  # 更新费用
        
        # 保存配置
        sms_manager.save_config()
        print("✅ 配置已更新并保存")
    
    # 3. 重新加载配置
    print("重新加载配置...")
    sms_manager.load_configs()
    sms_manager.initialize_providers()
    print("✅ 配置已重新加载")


if __name__ == "__main__":
    print("短信服务使用示例")
    print("=" * 50)
    
    try:
        # 运行所有示例
        example_basic_usage()
        example_provider_management()
        example_custom_provider()
        example_batch_sending()
        example_monitoring()
        example_error_handling()
        example_configuration_management()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成!")
        print("\n注意事项:")
        print("1. 请将配置文件中的API密钥替换为真实的密钥")
        print("2. 请将示例中的手机号替换为实际手机号")
        print("3. 确保网络连接正常，能够访问短信服务API")
        print("4. 建议在生产环境中使用HTTPS和适当的错误处理")
        
    except Exception as e:
        print(f"运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc()