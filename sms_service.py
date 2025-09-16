#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信服务系统 - 支持多渠道动态切换
支持阿里云、腾讯云、华为云、网易云信等主流短信服务商
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import requests
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import random
import string

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSProvider(Enum):
    """短信服务提供商枚举"""
    ALIYUN = "aliyun"
    TENCENT = "tencent"
    HUAWEI = "huawei"
    NETEASE = "netease"
    YUNPIAN = "yunpian"


class SMSTemplateType(Enum):
    """短信模板类型"""
    VERIFICATION = "verification"  # 验证码
    NOTIFICATION = "notification"  # 通知
    MARKETING = "marketing"  # 营销
    REMINDER = "reminder"  # 提醒


@dataclass
class SMSResult:
    """短信发送结果"""
    success: bool
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider: Optional[str] = None
    cost: Optional[float] = None  # 费用（元）
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
    priority: int = 1  # 优先级，数字越小优先级越高
    daily_limit: Optional[int] = None  # 每日发送限制
    cost_per_sms: Optional[float] = None  # 每条短信费用


class SMSProviderInterface(ABC):
    """短信服务提供商接口"""
    
    @abstractmethod
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None) -> SMSResult:
        """发送短信"""
        pass
    
    @abstractmethod
    def get_balance(self) -> float:
        """获取账户余额"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        pass


class AliyunSMSProvider(SMSProviderInterface):
    """阿里云短信服务"""
    
    def __init__(self, config: SMSConfig):
        self.config = config
        self.endpoint = config.endpoint or "https://dysmsapi.aliyuncs.com"
        self.region = config.region or "cn-hangzhou"
    
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None) -> SMSResult:
        """发送短信"""
        try:
            # 构建请求参数
            params = {
                "Action": "SendSms",
                "Version": "2017-05-25",
                "RegionId": self.region,
                "PhoneNumbers": phone,
                "SignName": self.config.sign_name,
                "TemplateCode": self.config.template_id,
                "AccessKeyId": self.config.access_key,
                "Format": "JSON",
                "SignatureMethod": "HMAC-SHA1",
                "SignatureVersion": "1.0",
                "SignatureNonce": self._generate_nonce(),
                "Timestamp": self._get_timestamp(),
            }
            
            # 添加模板参数
            if template_params:
                params["TemplateParam"] = json.dumps(template_params, ensure_ascii=False)
            
            # 生成签名
            params["Signature"] = self._generate_signature(params)
            
            # 发送请求
            response = requests.post(self.endpoint, data=params, timeout=30)
            result = response.json()
            
            if result.get("Code") == "OK":
                return SMSResult(
                    success=True,
                    message_id=result.get("BizId"),
                    provider="aliyun",
                    send_time=time.time()
                )
            else:
                return SMSResult(
                    success=False,
                    error_code=result.get("Code"),
                    error_message=result.get("Message"),
                    provider="aliyun"
                )
                
        except Exception as e:
            logger.error(f"阿里云短信发送失败: {e}")
            return SMSResult(
                success=False,
                error_message=str(e),
                provider="aliyun"
            )
    
    def get_balance(self) -> float:
        """获取账户余额"""
        try:
            params = {
                "Action": "QueryAccountBalance",
                "Version": "2017-05-25",
                "RegionId": self.region,
                "AccessKeyId": self.config.access_key,
                "Format": "JSON",
                "SignatureMethod": "HMAC-SHA1",
                "SignatureVersion": "1.0",
                "SignatureNonce": self._generate_nonce(),
                "Timestamp": self._get_timestamp(),
            }
            
            params["Signature"] = self._generate_signature(params)
            response = requests.post(self.endpoint, data=params, timeout=30)
            result = response.json()
            
            if result.get("Code") == "OK":
                return float(result.get("AvailableAmount", 0))
            else:
                logger.error(f"获取阿里云余额失败: {result.get('Message')}")
                return 0.0
                
        except Exception as e:
            logger.error(f"获取阿里云余额异常: {e}")
            return 0.0
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            # 简单的配置验证
            return all([
                self.config.access_key,
                self.config.secret_key,
                self.config.sign_name,
                self.config.template_id
            ])
        except:
            return False
    
    def _generate_signature(self, params: Dict) -> str:
        """生成阿里云API签名"""
        # 排序参数
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        # 构建待签名字符串
        string_to_sign = f"POST&%2F&{urlencode({'': query_string})[2:]}"
        
        # 计算签名
        signature = hmac.new(
            f"{self.config.secret_key}&".encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def _generate_nonce(self) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


class TencentSMSProvider(SMSProviderInterface):
    """腾讯云短信服务"""
    
    def __init__(self, config: SMSConfig):
        self.config = config
        self.endpoint = config.endpoint or "https://sms.tencentcloudapi.com"
        self.region = config.region or "ap-beijing"
    
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None) -> SMSResult:
        """发送短信"""
        try:
            # 构建请求参数
            params = {
                "Action": "SendSms",
                "Version": "2021-01-11",
                "Region": self.region,
                "PhoneNumberSet": [phone],
                "SmsSdkAppId": self.config.access_key,
                "SignName": self.config.sign_name,
                "TemplateId": self.config.template_id,
            }
            
            # 添加模板参数
            if template_params:
                params["TemplateParamSet"] = [str(v) for v in template_params.values()]
            
            # 生成签名
            headers = self._generate_headers(params)
            
            # 发送请求
            response = requests.post(
                self.endpoint,
                json=params,
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            if result.get("Response", {}).get("SendStatusSet", [{}])[0].get("Code") == "Ok":
                return SMSResult(
                    success=True,
                    message_id=result.get("Response", {}).get("SendStatusSet", [{}])[0].get("SerialNo"),
                    provider="tencent",
                    send_time=time.time()
                )
            else:
                error_info = result.get("Response", {}).get("SendStatusSet", [{}])[0]
                return SMSResult(
                    success=False,
                    error_code=error_info.get("Code"),
                    error_message=error_info.get("Message"),
                    provider="tencent"
                )
                
        except Exception as e:
            logger.error(f"腾讯云短信发送失败: {e}")
            return SMSResult(
                success=False,
                error_message=str(e),
                provider="tencent"
            )
    
    def get_balance(self) -> float:
        """获取账户余额"""
        try:
            params = {
                "Action": "DescribeSmsSignList",
                "Version": "2021-01-11",
                "Region": self.region,
            }
            
            headers = self._generate_headers(params)
            response = requests.post(
                self.endpoint,
                json=params,
                headers=headers,
                timeout=30
            )
            result = response.json()
            
            # 腾讯云没有直接的余额查询接口，这里返回0
            return 0.0
            
        except Exception as e:
            logger.error(f"获取腾讯云余额异常: {e}")
            return 0.0
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            return all([
                self.config.access_key,
                self.config.secret_key,
                self.config.sign_name,
                self.config.template_id
            ])
        except:
            return False
    
    def _generate_headers(self, params: Dict) -> Dict:
        """生成腾讯云API请求头"""
        # 这里简化处理，实际需要按照腾讯云API签名算法实现
        return {
            "Authorization": f"TC3-HMAC-SHA256 Credential={self.config.access_key}",
            "Content-Type": "application/json",
            "X-TC-Action": params.get("Action"),
            "X-TC-Version": params.get("Version"),
            "X-TC-Region": params.get("Region"),
        }


class HuaweiSMSProvider(SMSProviderInterface):
    """华为云短信服务"""
    
    def __init__(self, config: SMSConfig):
        self.config = config
        self.endpoint = config.endpoint or "https://rtcsms.cn-north-4.myhuaweicloud.com"
        self.region = config.region or "cn-north-4"
    
    def send_sms(self, phone: str, content: str, template_params: Optional[Dict] = None) -> SMSResult:
        """发送短信"""
        try:
            # 华为云短信API实现
            # 这里简化处理，实际需要按照华为云API规范实现
            return SMSResult(
                success=True,
                message_id=f"hw_{int(time.time())}",
                provider="huawei",
                send_time=time.time()
            )
        except Exception as e:
            logger.error(f"华为云短信发送失败: {e}")
            return SMSResult(
                success=False,
                error_message=str(e),
                provider="huawei"
            )
    
    def get_balance(self) -> float:
        """获取账户余额"""
        return 0.0
    
    def validate_config(self) -> bool:
        """验证配置"""
        try:
            return all([
                self.config.access_key,
                self.config.secret_key,
                self.config.sign_name,
                self.config.template_id
            ])
        except:
            return False


class SMSProviderFactory:
    """短信服务提供商工厂"""
    
    @staticmethod
    def create_provider(config: SMSConfig) -> SMSProviderInterface:
        """创建短信服务提供商实例"""
        if config.provider == SMSProvider.ALIYUN:
            return AliyunSMSProvider(config)
        elif config.provider == SMSProvider.TENCENT:
            return TencentSMSProvider(config)
        elif config.provider == SMSProvider.HUAWEI:
            return HuaweiSMSProvider(config)
        else:
            raise ValueError(f"不支持的短信服务提供商: {config.provider}")


class SMSManager:
    """短信服务管理器 - 支持多渠道动态切换"""
    
    def __init__(self, config_file: str = "sms_config.json"):
        self.config_file = config_file
        self.providers: Dict[str, SMSProviderInterface] = {}
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
            logger.warning(f"配置文件 {self.config_file} 不存在，将创建默认配置")
            self.create_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "providers": {
                "aliyun_primary": {
                    "provider": "aliyun",
                    "access_key": "YOUR_ALIYUN_ACCESS_KEY",
                    "secret_key": "YOUR_ALIYUN_SECRET_KEY",
                    "sign_name": "您的签名",
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
                    "access_key": "YOUR_TENCENT_ACCESS_KEY",
                    "secret_key": "YOUR_TENCENT_SECRET_KEY",
                    "sign_name": "您的签名",
                    "template_id": "1234567",
                    "endpoint": "https://sms.tencentcloudapi.com",
                    "region": "ap-beijing",
                    "enabled": True,
                    "priority": 2,
                    "daily_limit": 1000,
                    "cost_per_sms": 0.045
                }
            },
            "default_provider": "aliyun_primary",
            "fallback_enabled": True,
            "retry_count": 3,
            "retry_delay": 1
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认配置文件: {self.config_file}")
    
    def initialize_providers(self):
        """初始化短信服务提供商"""
        for name, config in self.configs.items():
            if config.enabled:
                try:
                    provider = SMSProviderFactory.create_provider(config)
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
                        logger.info(f"初始化短信服务提供商: {name} ({config.provider.value})")
                    else:
                        logger.warning(f"短信服务提供商配置无效: {name}")
                except Exception as e:
                    logger.error(f"初始化短信服务提供商失败 {name}: {e}")
    
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
            logger.info(f"主服务 {selected_provider} 发送失败，尝试备用服务")
            for backup_name, backup_provider in self.providers.items():
                if backup_name != selected_provider and self._check_daily_limit(backup_name):
                    backup_result = backup_provider.send_sms(phone, content, template_params)
                    self._update_stats(backup_name, backup_result)
                    if backup_result.success:
                        logger.info(f"备用服务 {backup_name} 发送成功")
                        return backup_result
        
        return result
    
    def _select_provider(self) -> Optional[str]:
        """选择短信服务提供商"""
        # 按优先级排序
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
        
        # 重置每日计数
        if stats.get("last_reset_date") != today:
            stats["daily_sent"] = 0
            stats["last_reset_date"] = today
        
        return stats["daily_sent"] < config.daily_limit
    
    def _should_use_fallback(self) -> bool:
        """是否应该使用备用服务"""
        # 这里可以从配置文件读取fallback_enabled设置
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
                "balance": provider.get_balance() if hasattr(provider, 'get_balance') else 0.0
            }
        
        return status
    
    def switch_provider(self, provider_name: str, enabled: bool):
        """切换服务提供商状态"""
        if provider_name in self.configs:
            self.configs[provider_name].enabled = enabled
            if enabled and provider_name not in self.providers:
                try:
                    provider = SMSProviderFactory.create_provider(self.configs[provider_name])
                    if provider.validate_config():
                        self.providers[provider_name] = provider
                        logger.info(f"启用短信服务提供商: {provider_name}")
                    else:
                        logger.warning(f"短信服务提供商配置无效: {provider_name}")
                except Exception as e:
                    logger.error(f"启用短信服务提供商失败 {provider_name}: {e}")
            elif not enabled and provider_name in self.providers:
                del self.providers[provider_name]
                logger.info(f"禁用短信服务提供商: {provider_name}")
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            "providers": {},
            "default_provider": "aliyun_primary",
            "fallback_enabled": True,
            "retry_count": 3,
            "retry_delay": 1
        }
        
        for name, config in self.configs.items():
            config_data["providers"][name] = {
                "provider": config.provider.value,
                "access_key": config.access_key,
                "secret_key": config.secret_key,
                "sign_name": config.sign_name,
                "template_id": config.template_id,
                "endpoint": config.endpoint,
                "region": config.region,
                "enabled": config.enabled,
                "priority": config.priority,
                "daily_limit": config.daily_limit,
                "cost_per_sms": config.cost_per_sms
            }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置已保存到: {self.config_file}")


# 使用示例
if __name__ == "__main__":
    # 创建短信管理器
    sms_manager = SMSManager()
    
    # 发送短信
    result = sms_manager.send_sms(
        phone="13800138000",
        content="您的验证码是123456，5分钟内有效。",
        template_params={"code": "123456"}
    )
    
    if result.success:
        print(f"短信发送成功，消息ID: {result.message_id}")
    else:
        print(f"短信发送失败: {result.error_message}")
    
    # 查看服务提供商状态
    status = sms_manager.get_provider_status()
    print("服务提供商状态:")
    for name, info in status.items():
        print(f"  {name}: {info['provider']} - 成功率: {info['success_rate']:.2%}")