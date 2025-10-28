#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信服务演示 - 不依赖外部包的简化版本
"""

import json
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


class SMSProvider(Enum):
    """短信服务提供商枚举"""
    ALIYUN = "aliyun"
    TENCENT = "tencent"
    HUAWEI = "huawei"


@dataclass
class SMSResult:
    """短信发送结果"""
    success: bool
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider: Optional[str] = None
    cost: Optional[float] = None
    send_time: Optional[float] = None


@dataclass
class SMSConfig:
    """短信配置"""
    provider: SMSProvider
    access_key: str
    secret_key: str
    sign_name: str
    template_id: str
    endpoint: Optional[str] = None
    region: Optional[str] = None
    enabled: bool = True
    priority: int = 1
    daily_limit: Optional[int] = None
    cost_per_sms: Optional[float] = None


class MockSMSProvider:
    """模拟短信服务提供商"""
    
    def __init__(self, config: SMSConfig):
        self.config = config
        self.name = config.provider.value
    
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None) -> SMSResult:
        """模拟发送短信"""
        # 模拟发送延迟
        time.sleep(0.1)
        
        # 模拟发送结果
        if self.config.enabled and phone.startswith("138"):
            return SMSResult(
                success=True,
                message_id=f"{self.name}_{int(time.time())}",
                provider=self.name,
                send_time=time.time(),
                cost=self.config.cost_per_sms or 0.045
            )
        else:
            return SMSResult(
                success=False,
                error_code="INVALID_PHONE",
                error_message="无效的手机号码",
                provider=self.name
            )
    
    def get_balance(self) -> float:
        """模拟获取余额"""
        return 100.0
    
    def validate_config(self) -> bool:
        """验证配置"""
        return all([
            self.config.access_key,
            self.config.secret_key,
            self.config.sign_name,
            self.config.template_id
        ])


class SMSManager:
    """短信服务管理器"""
    
    def __init__(self, config_file: str = "sms_demo_config.json"):
        self.config_file = config_file
        self.providers: Dict[str, MockSMSProvider] = {}
        self.configs: Dict[str, SMSConfig] = {}
        self.usage_stats: Dict[str, Dict] = {}
        self.load_configs()
        self.initialize_providers()
    
    def load_configs(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for name, config_dict in config_data.get("providers", {}).items():
                config = SMSConfig(
                    provider=SMSProvider(config_dict["provider"]),
                    access_key=config_dict["access_key"],
                    secret_key=config_dict["secret_key"],
                    sign_name=config_dict["sign_name"],
                    template_id=config_dict["template_id"],
                    endpoint=config_dict.get("endpoint"),
                    region=config_dict.get("region"),
                    enabled=config_dict.get("enabled", True),
                    priority=config_dict.get("priority", 1),
                    daily_limit=config_dict.get("daily_limit"),
                    cost_per_sms=config_dict.get("cost_per_sms")
                )
                self.configs[name] = config
                
        except FileNotFoundError:
            self.create_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "providers": {
                "aliyun_primary": {
                    "provider": "aliyun",
                    "access_key": "LTAI5tDemoKey123456789",
                    "secret_key": "DemoSecretKey123456789",
                    "sign_name": "演示签名",
                    "template_id": "SMS_123456789",
                    "endpoint": "https://dysmsapi.aliyuncs.com",
                    "region": "cn-hangzhou",
                    "enabled": True,
                    "priority": 1,
                    "daily_limit": 1000,
                    "cost_per_sms": 0.045
                },
                "tencent_backup": {
                    "provider": "tencent",
                    "access_key": "AKIDDemoKey123456789",
                    "secret_key": "DemoSecretKey123456789",
                    "sign_name": "演示签名",
                    "template_id": "1234567",
                    "endpoint": "https://sms.tencentcloudapi.com",
                    "region": "ap-beijing",
                    "enabled": True,
                    "priority": 2,
                    "daily_limit": 1000,
                    "cost_per_sms": 0.045
                },
                "huawei_emergency": {
                    "provider": "huawei",
                    "access_key": "HW_DemoKey123456789",
                    "secret_key": "DemoSecretKey123456789",
                    "sign_name": "演示签名",
                    "template_id": "1234567890123456789",
                    "endpoint": "https://rtcsms.cn-north-4.myhuaweicloud.com",
                    "region": "cn-north-4",
                    "enabled": False,
                    "priority": 3,
                    "daily_limit": 500,
                    "cost_per_sms": 0.04
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        print(f"已创建默认配置文件: {self.config_file}")
    
    def initialize_providers(self):
        """初始化短信服务提供商"""
        for name, config in self.configs.items():
            if config.enabled:
                try:
                    provider = MockSMSProvider(config)
                    if provider.validate_config():
                        self.providers[name] = provider
                        self.usage_stats[name] = {
                            "total_sent": 0,
                            "success_count": 0,
                            "error_count": 0,
                            "last_send_time": None,
                            "daily_sent": 0,
                            "last_reset_date": time.strftime("%Y-%m-%d")
                        }
                        print(f"✅ 初始化短信服务提供商: {name} ({config.provider.value})")
                    else:
                        print(f"⚠️  短信服务提供商配置无效: {name}")
                except Exception as e:
                    print(f"❌ 初始化短信服务提供商失败 {name}: {e}")
        
        # 如果没有可用的提供商，重新加载配置
        if not self.providers:
            print("🔄 重新加载配置...")
            self.load_configs()
            for name, config in self.configs.items():
                if config.enabled:
                    try:
                        provider = MockSMSProvider(config)
                        if provider.validate_config():
                            self.providers[name] = provider
                            self.usage_stats[name] = {
                                "total_sent": 0,
                                "success_count": 0,
                                "error_count": 0,
                                "last_send_time": None,
                                "daily_sent": 0,
                                "last_reset_date": time.strftime("%Y-%m-%d")
                            }
                            print(f"✅ 重新初始化短信服务提供商: {name} ({config.provider.value})")
                    except Exception as e:
                        print(f"❌ 重新初始化短信服务提供商失败 {name}: {e}")
    
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None, 
                 provider_name: Optional[str] = None) -> SMSResult:
        """发送短信"""
        if not self.providers:
            return SMSResult(
                success=False,
                error_message="没有可用的短信服务提供商"
            )
        
        # 选择短信服务提供商
        if provider_name and provider_name in self.providers:
            selected_provider = provider_name
        else:
            selected_provider = self._select_provider()
        
        if not selected_provider:
            return SMSResult(
                success=False,
                error_message="没有可用的短信服务提供商"
            )
        
        # 检查每日限制
        if not self._check_daily_limit(selected_provider):
            return SMSResult(
                success=False,
                error_message=f"短信服务提供商 {selected_provider} 已达到每日发送限制"
            )
        
        # 发送短信
        provider = self.providers[selected_provider]
        result = provider.send_sms(phone, content, template_params)
        
        # 更新统计信息
        self._update_stats(selected_provider, result)
        
        # 如果失败且启用了备用服务，尝试其他提供商
        if not result.success and self._should_use_fallback():
            print(f"🔄 主服务 {selected_provider} 发送失败，尝试备用服务")
            for backup_name, backup_provider in self.providers.items():
                if backup_name != selected_provider and self._check_daily_limit(backup_name):
                    backup_result = backup_provider.send_sms(phone, content, template_params)
                    self._update_stats(backup_name, backup_result)
                    if backup_result.success:
                        print(f"✅ 备用服务 {backup_name} 发送成功")
                        return backup_result
        
        return result
    
    def _select_provider(self) -> Optional[str]:
        """选择短信服务提供商"""
        sorted_providers = sorted(
            self.providers.keys(),
            key=lambda x: self.configs[x].priority
        )
        
        for provider_name in sorted_providers:
            if self._check_daily_limit(provider_name):
                return provider_name
        
        return None
    
    def _check_daily_limit(self, provider_name: str) -> bool:
        """检查每日发送限制"""
        config = self.configs.get(provider_name)
        if not config or not config.daily_limit:
            return True
        
        stats = self.usage_stats.get(provider_name, {})
        today = time.strftime("%Y-%m-%d")
        
        if stats.get("last_reset_date") != today:
            stats["daily_sent"] = 0
            stats["last_reset_date"] = today
        
        return stats["daily_sent"] < config.daily_limit
    
    def _should_use_fallback(self) -> bool:
        """是否应该使用备用服务"""
        return True
    
    def _update_stats(self, provider_name: str, result: SMSResult):
        """更新统计信息"""
        if provider_name not in self.usage_stats:
            self.usage_stats[provider_name] = {
                "total_sent": 0,
                "success_count": 0,
                "error_count": 0,
                "last_send_time": None,
                "daily_sent": 0,
                "last_reset_date": time.strftime("%Y-%m-%d")
            }
        
        stats = self.usage_stats[provider_name]
        stats["total_sent"] += 1
        stats["last_send_time"] = time.time()
        
        if result.success:
            stats["success_count"] += 1
            stats["daily_sent"] += 1
        else:
            stats["error_count"] += 1
    
    def get_provider_status(self) -> Dict[str, Dict]:
        """获取所有服务提供商状态"""
        status = {}
        for name, provider in self.providers.items():
            config = self.configs[name]
            stats = self.usage_stats.get(name, {})
            
            status[name] = {
                "provider": config.provider.value,
                "enabled": config.enabled,
                "priority": config.priority,
                "daily_limit": config.daily_limit,
                "daily_sent": stats.get("daily_sent", 0),
                "total_sent": stats.get("total_sent", 0),
                "success_rate": stats.get("success_count", 0) / max(stats.get("total_sent", 1), 1),
                "last_send_time": stats.get("last_send_time"),
                "balance": provider.get_balance()
            }
        
        return status
    
    def switch_provider(self, provider_name: str, enabled: bool):
        """切换服务提供商状态"""
        if provider_name in self.configs:
            self.configs[provider_name].enabled = enabled
            if enabled and provider_name not in self.providers:
                try:
                    provider = MockSMSProvider(self.configs[provider_name])
                    if provider.validate_config():
                        self.providers[provider_name] = provider
                        print(f"✅ 启用短信服务提供商: {provider_name}")
                    else:
                        print(f"⚠️  短信服务提供商配置无效: {provider_name}")
                except Exception as e:
                    print(f"❌ 启用短信服务提供商失败 {provider_name}: {e}")
            elif not enabled and provider_name in self.providers:
                del self.providers[provider_name]
                print(f"🔴 禁用短信服务提供商: {provider_name}")


def demo_basic_usage():
    """基础使用演示"""
    print("=" * 60)
    print("                   短信服务系统演示")
    print("=" * 60)
    
    # 创建短信管理器
    print("\n1. 创建短信管理器...")
    sms_manager = SMSManager("sms_demo_config.json")
    
    # 显示服务提供商状态
    print("\n2. 服务提供商状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"   📱 {name}:")
        print(f"      提供商: {info['provider']}")
        print(f"      状态: {'✅ 启用' if info['enabled'] else '❌ 禁用'}")
        print(f"      优先级: {info['priority']}")
        print(f"      每日限制: {info['daily_limit'] or '无限制'}")
        print(f"      余额: ¥{info['balance']:.2f}")
        print()
    
    # 发送短信演示
    print("3. 发送短信演示:")
    test_phones = ["13800138000", "13800138001", "12345678901"]  # 最后一个无效
    
    for i, phone in enumerate(test_phones, 1):
        print(f"\n   发送第 {i} 条短信到 {phone}...")
        
        result = sms_manager.send_sms(
            phone=phone,
            content="您的验证码是123456，5分钟内有效。",
            template_params={"code": "123456"}
        )
        
        if result.success:
            print(f"   ✅ 发送成功!")
            print(f"      消息ID: {result.message_id}")
            print(f"      使用提供商: {result.provider}")
            print(f"      费用: ¥{result.cost:.3f}")
        else:
            print(f"   ❌ 发送失败: {result.error_message}")
    
    # 显示统计信息
    print("\n4. 发送统计:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        if info['total_sent'] > 0:
            print(f"   📊 {name}:")
            print(f"      总发送: {info['total_sent']} 条")
            print(f"      成功率: {info['success_rate']:.1%}")
            print(f"      今日发送: {info['daily_sent']} 条")
    
    # 服务提供商切换演示
    print("\n5. 服务提供商切换演示:")
    print("   禁用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", False)
    
    print("   再次发送短信...")
    result = sms_manager.send_sms(
        phone="13800138000",
        content="测试备用服务",
        template_params={}
    )
    
    if result.success:
        print(f"   ✅ 备用服务发送成功: {result.provider}")
    else:
        print(f"   ❌ 备用服务也失败: {result.error_message}")
    
    print("\n   重新启用主服务提供商...")
    sms_manager.switch_provider("aliyun_primary", True)
    
    # 最终状态
    print("\n6. 最终状态:")
    status = sms_manager.get_provider_status()
    for name, info in status.items():
        print(f"   {name}: {'✅ 启用' if info['enabled'] else '❌ 禁用'} - 发送 {info['total_sent']} 条")
    
    print("\n" + "=" * 60)
    print("                   演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo_basic_usage()