#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
支付宝转账给个人用户示例 - Python版本

使用前请确保：
1. 已安装支付宝SDK：pip install alipay-sdk-python
2. 已配置应用ID、私钥、公钥等参数
3. 已开通转账功能
"""

from alipay import AliPay
from alipay.utils import AliPayConfig
import json
import time
import uuid

class AlipayTransferExample:
    
    def __init__(self, app_id, private_key, alipay_public_key, is_sandbox=False):
        """
        初始化支付宝客户端
        
        Args:
            app_id: 应用ID
            private_key: 应用私钥
            alipay_public_key: 支付宝公钥
            is_sandbox: 是否使用沙箱环境
        """
        self.app_id = app_id
        self.private_key = private_key
        self.alipay_public_key = alipay_public_key
        self.is_sandbox = is_sandbox
        
        # 创建支付宝客户端
        self.alipay = AliPay(
            appid=app_id,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=private_key,
            alipay_public_key_string=alipay_public_key,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=is_sandbox,  # 默认False
            config=AliPayConfig(timeout=15)  # 默认 15s
        )
    
    def transfer_to_account(self, out_biz_no, payee_account, payee_type, amount, 
                          payer_show_name=None, payee_real_name=None, remark=None):
        """
        转账给个人用户
        
        Args:
            out_biz_no: 商户转账唯一订单号
            payee_account: 收款方账户（支付宝账号或用户ID）
            payee_type: 收款方账户类型（ALIPAY_LOGONID或ALIPAY_USERID）
            amount: 转账金额（元）
            payer_show_name: 付款方显示名称（可选）
            payee_real_name: 收款方真实姓名（可选）
            remark: 转账备注（可选）
            
        Returns:
            dict: 转账结果
        """
        try:
            # 构建转账参数
            transfer_params = {
                'out_biz_no': out_biz_no,
                'payee_type': payee_type,
                'payee_account': payee_account,
                'amount': amount
            }
            
            # 添加可选参数
            if payer_show_name:
                transfer_params['payer_show_name'] = payer_show_name
            if payee_real_name:
                transfer_params['payee_real_name'] = payee_real_name
            if remark:
                transfer_params['remark'] = remark
            
            # 调用转账接口
            result = self.alipay.api_alipay_fund_trans_toaccount_transfer(**transfer_params)
            
            return result
            
        except Exception as e:
            print(f"支付宝转账接口调用失败：{str(e)}")
            return None
    
    def simple_transfer(self, payee_account, amount, remark=None):
        """
        转账给个人用户（简化版本）
        
        Args:
            payee_account: 收款方支付宝账号
            amount: 转账金额（元）
            remark: 转账备注
            
        Returns:
            dict: 转账结果
        """
        # 生成唯一订单号
        out_biz_no = f"TRANSFER_{int(time.time() * 1000)}"
        
        return self.transfer_to_account(
            out_biz_no=out_biz_no,
            payee_account=payee_account,
            payee_type="ALIPAY_LOGONID",  # 使用支付宝账号
            amount=amount,
            payer_show_name="测试付款方",  # 付款方显示名称
            payee_real_name=None,  # 不校验收款方真实姓名
            remark=remark
        )
    
    def handle_transfer_response(self, response):
        """
        处理转账结果
        
        Args:
            response: 转账响应
        """
        if response is None:
            print("转账请求失败")
            return
        
        if response.get('code') == '10000':
            print("转账成功！")
            print(f"订单号：{response.get('out_biz_no')}")
            print(f"支付宝转账单据号：{response.get('order_id')}")
            print(f"支付时间：{response.get('pay_date')}")
        else:
            print("转账失败！")
            print(f"错误码：{response.get('code')}")
            print(f"错误信息：{response.get('msg')}")
            print(f"子错误码：{response.get('sub_code')}")
            print(f"子错误信息：{response.get('sub_msg')}")
    
    def validate_amount(self, amount):
        """
        验证转账金额
        
        Args:
            amount: 转账金额
            
        Returns:
            bool: 是否有效
        """
        try:
            amount_float = float(amount)
            if amount_float < 0.1:
                print("转账金额不能少于0.1元")
                return False
            if amount_float > 50000:
                print("转账给个人账户单笔不能超过5万元")
                return False
            return True
        except ValueError:
            print("转账金额格式错误")
            return False

def main():
    """
    主方法 - 测试转账功能
    """
    # 配置参数（请替换为实际值）
    APP_ID = "your_app_id"
    PRIVATE_KEY = """your_private_key"""
    ALIPAY_PUBLIC_KEY = """your_alipay_public_key"""
    
    # 创建转账实例
    transfer_example = AlipayTransferExample(
        app_id=APP_ID,
        private_key=PRIVATE_KEY,
        alipay_public_key=ALIPAY_PUBLIC_KEY,
        is_sandbox=True  # 测试时使用沙箱环境
    )
    
    # 测试转账
    payee_account = "test@example.com"  # 收款方支付宝账号
    amount = "0.01"  # 转账金额（测试金额）
    remark = "测试转账"  # 转账备注
    
    # 验证金额
    if not transfer_example.validate_amount(amount):
        return
    
    # 执行转账
    response = transfer_example.simple_transfer(
        payee_account=payee_account,
        amount=amount,
        remark=remark
    )
    
    # 处理结果
    transfer_example.handle_transfer_response(response)

if __name__ == "__main__":
    main()

"""
安装依赖：
pip install alipay-sdk-python

配置文件示例（config.py）：
APP_ID = "your_app_id"
PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
your_private_key_content
-----END RSA PRIVATE KEY-----'''
ALIPAY_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
your_alipay_public_key_content
-----END PUBLIC KEY-----'''

使用示例：
from alipay_transfer_python_example import AlipayTransferExample
from config import APP_ID, PRIVATE_KEY, ALIPAY_PUBLIC_KEY

# 创建实例
transfer = AlipayTransferExample(APP_ID, PRIVATE_KEY, ALIPAY_PUBLIC_KEY)

# 执行转账
result = transfer.simple_transfer("user@example.com", "1.00", "测试转账")
transfer.handle_transfer_response(result)
"""