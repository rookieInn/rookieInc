#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信支付核心模块
支持小程序支付、H5支付、APP支付、JSAPI支付等
"""

import os
import json
import time
import hashlib
import hmac
import base64
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from configparser import ConfigParser
from urllib.parse import urlencode, quote
import uuid
import random
import string

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_pay.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeChatPayCore:
    """微信支付核心类"""
    
    def __init__(self, config_file: str = 'wechat_pay_config.ini'):
        """初始化微信支付"""
        self.config = self._load_config(config_file)
        self.merchant_id = self.config.get('WECHAT_PAY', 'merchant_id')
        self.app_id = self.config.get('WECHAT_PAY', 'app_id')
        self.api_key = self.config.get('WECHAT_PAY', 'api_key')
        self.notify_url = self.config.get('WECHAT_PAY', 'notify_url')
        self.sandbox_mode = self.config.getboolean('WECHAT_PAY_SETTINGS', 'sandbox_mode')
        self.debug_mode = self.config.getboolean('WECHAT_PAY_SETTINGS', 'debug_mode')
        
        # API URLs
        if self.sandbox_mode:
            self.base_url = "https://api.mch.weixin.qq.com/sandboxnew"
            self.api_key = self.config.get('WECHAT_PAY_SETTINGS', 'sandbox_api_key')
        else:
            self.base_url = "https://api.mch.weixin.qq.com"
        
        # 支付相关URL
        self.unified_order_url = f"{self.base_url}/pay/unifiedorder"
        self.order_query_url = f"{self.base_url}/pay/orderquery"
        self.close_order_url = f"{self.base_url}/pay/closeorder"
        self.refund_url = f"{self.base_url}/secapi/pay/refund"
        self.refund_query_url = f"{self.base_url}/pay/refundquery"
        
        logger.info(f"微信支付初始化完成 - 商户号: {self.merchant_id}, 沙箱模式: {self.sandbox_mode}")
    
    def _load_config(self, config_file: str) -> ConfigParser:
        """加载配置文件"""
        config = ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        else:
            logger.error(f"配置文件不存在: {config_file}")
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        return config
    
    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_timestamp(self) -> str:
        """生成时间戳"""
        return str(int(time.time()))
    
    def _generate_out_trade_no(self, prefix: str = "WX") -> str:
        """生成商户订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{timestamp}{random_str}"
    
    def _sign_md5(self, params: Dict[str, Any]) -> str:
        """MD5签名"""
        # 过滤空值并排序
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ''}
        sorted_params = sorted(filtered_params.items())
        
        # 拼接字符串
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={self.api_key}"
        
        # MD5加密并转大写
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
        
        if self.debug_mode:
            logger.debug(f"签名字符串: {sign_str}")
            logger.debug(f"签名结果: {sign}")
        
        return sign
    
    def _sign_hmac_sha256(self, params: Dict[str, Any]) -> str:
        """HMAC-SHA256签名"""
        # 过滤空值并排序
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ''}
        sorted_params = sorted(filtered_params.items())
        
        # 拼接字符串
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # HMAC-SHA256签名
        sign = hmac.new(
            self.api_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()
        
        if self.debug_mode:
            logger.debug(f"HMAC-SHA256签名字符串: {sign_str}")
            logger.debug(f"HMAC-SHA256签名结果: {sign}")
        
        return sign
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """字典转XML"""
        xml_parts = ['<xml>']
        for key, value in data.items():
            xml_parts.append(f'<{key}><![CDATA[{value}]]></{key}>')
        xml_parts.append('</xml>')
        return ''.join(xml_parts)
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, str]:
        """XML转字典"""
        try:
            root = ET.fromstring(xml_str)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except ET.ParseError as e:
            logger.error(f"XML解析失败: {e}")
            return {}
    
    def _make_request(self, url: str, data: Dict[str, Any], use_cert: bool = False) -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            # 转换为XML
            xml_data = self._dict_to_xml(data)
            
            if self.debug_mode:
                logger.debug(f"请求URL: {url}")
                logger.debug(f"请求数据: {xml_data}")
            
            # 发送请求
            if use_cert:
                # 需要证书的请求（如退款）
                cert_path = self.config.get('WECHAT_PAY', 'cert_path')
                key_path = self.config.get('WECHAT_PAY', 'key_path')
                
                if not os.path.exists(cert_path) or not os.path.exists(key_path):
                    raise FileNotFoundError("微信支付证书文件不存在")
                
                response = requests.post(
                    url,
                    data=xml_data.encode('utf-8'),
                    cert=(cert_path, key_path),
                    timeout=30
                )
            else:
                response = requests.post(
                    url,
                    data=xml_data.encode('utf-8'),
                    timeout=30
                )
            
            response.raise_for_status()
            
            # 解析响应
            result = self._xml_to_dict(response.text)
            
            if self.debug_mode:
                logger.debug(f"响应数据: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求失败: {e}")
            return {'return_code': 'FAIL', 'return_msg': str(e)}
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return {'return_code': 'FAIL', 'return_msg': str(e)}
    
    def create_miniprogram_payment(self, 
                                 openid: str,
                                 total_fee: int,
                                 body: str,
                                 out_trade_no: Optional[str] = None,
                                 attach: Optional[str] = None,
                                 time_expire: Optional[int] = None) -> Dict[str, Any]:
        """创建小程序支付订单"""
        try:
            if not out_trade_no:
                out_trade_no = self._generate_out_trade_no()
            
            # 构建支付参数
            params = {
                'appid': self.app_id,
                'mch_id': self.merchant_id,
                'nonce_str': self._generate_nonce_str(),
                'body': body,
                'out_trade_no': out_trade_no,
                'total_fee': total_fee,
                'spbill_create_ip': '127.0.0.1',  # 实际使用时需要获取真实IP
                'notify_url': self.notify_url,
                'trade_type': 'JSAPI',
                'openid': openid
            }
            
            # 添加可选参数
            if attach:
                params['attach'] = attach
            if time_expire:
                params['time_expire'] = time_expire
            
            # 生成签名
            params['sign'] = self._sign_md5(params)
            
            # 发送请求
            result = self._make_request(self.unified_order_url, params)
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                # 生成小程序支付参数
                prepay_id = result['prepay_id']
                miniprogram_params = self._generate_miniprogram_pay_params(prepay_id)
                
                return {
                    'success': True,
                    'out_trade_no': out_trade_no,
                    'prepay_id': prepay_id,
                    'miniprogram_params': miniprogram_params,
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return_msg', '支付订单创建失败'),
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"创建小程序支付订单失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_miniprogram_pay_params(self, prepay_id: str) -> Dict[str, str]:
        """生成小程序支付参数"""
        params = {
            'appId': self.app_id,
            'timeStamp': self._generate_timestamp(),
            'nonceStr': self._generate_nonce_str(),
            'package': f'prepay_id={prepay_id}',
            'signType': 'MD5'
        }
        
        # 生成签名
        params['paySign'] = self._sign_md5(params)
        
        return params
    
    def create_h5_payment(self,
                         total_fee: int,
                         body: str,
                         out_trade_no: Optional[str] = None,
                         attach: Optional[str] = None,
                         time_expire: Optional[int] = None) -> Dict[str, Any]:
        """创建H5支付订单"""
        try:
            if not out_trade_no:
                out_trade_no = self._generate_out_trade_no()
            
            # 构建支付参数
            params = {
                'appid': self.app_id,
                'mch_id': self.merchant_id,
                'nonce_str': self._generate_nonce_str(),
                'body': body,
                'out_trade_no': out_trade_no,
                'total_fee': total_fee,
                'spbill_create_ip': '127.0.0.1',
                'notify_url': self.notify_url,
                'trade_type': 'MWEB'
            }
            
            # 添加可选参数
            if attach:
                params['attach'] = attach
            if time_expire:
                params['time_expire'] = time_expire
            
            # 生成签名
            params['sign'] = self._sign_md5(params)
            
            # 发送请求
            result = self._make_request(self.unified_order_url, params)
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                return {
                    'success': True,
                    'out_trade_no': out_trade_no,
                    'prepay_id': result['prepay_id'],
                    'mweb_url': result.get('mweb_url'),
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return_msg', 'H5支付订单创建失败'),
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"创建H5支付订单失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_order(self, out_trade_no: str) -> Dict[str, Any]:
        """查询订单状态"""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.merchant_id,
                'out_trade_no': out_trade_no,
                'nonce_str': self._generate_nonce_str()
            }
            
            # 生成签名
            params['sign'] = self._sign_md5(params)
            
            # 发送请求
            result = self._make_request(self.order_query_url, params)
            
            if result.get('return_code') == 'SUCCESS':
                return {
                    'success': True,
                    'trade_state': result.get('trade_state'),
                    'trade_state_desc': result.get('trade_state_desc'),
                    'transaction_id': result.get('transaction_id'),
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return_msg', '订单查询失败'),
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close_order(self, out_trade_no: str) -> Dict[str, Any]:
        """关闭订单"""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.merchant_id,
                'out_trade_no': out_trade_no,
                'nonce_str': self._generate_nonce_str()
            }
            
            # 生成签名
            params['sign'] = self._sign_md5(params)
            
            # 发送请求
            result = self._make_request(self.close_order_url, params)
            
            if result.get('return_code') == 'SUCCESS':
                return {
                    'success': True,
                    'result_msg': result.get('result_msg'),
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return_msg', '关闭订单失败'),
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"关闭订单失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund(self,
              out_trade_no: str,
              out_refund_no: str,
              total_fee: int,
              refund_fee: int,
              refund_desc: Optional[str] = None) -> Dict[str, Any]:
        """申请退款"""
        try:
            params = {
                'appid': self.app_id,
                'mch_id': self.merchant_id,
                'nonce_str': self._generate_nonce_str(),
                'out_trade_no': out_trade_no,
                'out_refund_no': out_refund_no,
                'total_fee': total_fee,
                'refund_fee': refund_fee
            }
            
            # 添加可选参数
            if refund_desc:
                params['refund_desc'] = refund_desc
            
            # 生成签名
            params['sign'] = self._sign_md5(params)
            
            # 发送请求（需要证书）
            result = self._make_request(self.refund_url, params, use_cert=True)
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('return_msg', '退款申请失败'),
                    'raw_response': result
                }
                
        except Exception as e:
            logger.error(f"申请退款失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_notify(self, xml_data: str) -> Tuple[bool, Dict[str, str]]:
        """验证支付回调通知"""
        try:
            # 解析XML
            notify_data = self._xml_to_dict(xml_data)
            
            if not notify_data:
                return False, {}
            
            # 提取签名
            sign = notify_data.pop('sign', '')
            
            # 验证签名
            calculated_sign = self._sign_md5(notify_data)
            
            if sign == calculated_sign:
                return True, notify_data
            else:
                logger.warning(f"签名验证失败: 接收签名={sign}, 计算签名={calculated_sign}")
                return False, notify_data
                
        except Exception as e:
            logger.error(f"验证支付回调失败: {e}")
            return False, {}
    
    def verify_refund_notify(self, xml_data: str) -> Tuple[bool, Dict[str, str]]:
        """验证退款回调通知"""
        try:
            # 解析XML
            notify_data = self._xml_to_dict(xml_data)
            
            if not notify_data:
                return False, {}
            
            # 提取签名
            sign = notify_data.pop('sign', '')
            
            # 验证签名
            calculated_sign = self._sign_md5(notify_data)
            
            if sign == calculated_sign:
                return True, notify_data
            else:
                logger.warning(f"退款签名验证失败: 接收签名={sign}, 计算签名={calculated_sign}")
                return False, notify_data
                
        except Exception as e:
            logger.error(f"验证退款回调失败: {e}")
            return False, {}

def main():
    """测试函数"""
    print("微信支付核心模块测试")
    print("=" * 50)
    
    # 创建支付实例
    pay = WeChatPayCore()
    
    # 测试小程序支付
    print("测试小程序支付...")
    result = pay.create_miniprogram_payment(
        openid="test_openid",
        total_fee=1,  # 1分钱
        body="测试商品",
        attach="test_attach"
    )
    
    print(f"支付结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    main()