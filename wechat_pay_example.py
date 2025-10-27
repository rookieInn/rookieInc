#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信支付使用示例
演示如何使用微信支付API进行小程序支付、H5支付等
"""

import json
import requests
import time
from typing import Dict, Any

class WeChatPayExample:
    """微信支付使用示例"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        """初始化示例"""
        self.api_base_url = api_base_url
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def create_miniprogram_payment_example(self):
        """小程序支付示例"""
        print("=" * 60)
        print("小程序支付示例")
        print("=" * 60)
        
        # 支付参数
        payment_data = {
            "openid": "test_openid_123456",  # 用户openid
            "total_fee": 100,  # 支付金额（分）
            "body": "测试商品 - 小程序支付",
            "attach": "test_attach_data",
            "out_trade_no": f"WX{int(time.time())}"  # 商户订单号
        }
        
        print(f"支付参数: {json.dumps(payment_data, ensure_ascii=False, indent=2)}")
        
        try:
            # 调用API
            response = requests.post(
                f"{self.api_base_url}/api/wechat/pay/miniprogram",
                headers=self.headers,
                json=payment_data
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 小程序支付订单创建成功！")
                print(f"订单号: {result['data']['out_trade_no']}")
                print(f"预支付ID: {result['data']['prepay_id']}")
                print("\n小程序支付参数:")
                miniprogram_params = result['data']['miniprogram_params']
                for key, value in miniprogram_params.items():
                    print(f"  {key}: {value}")
                
                print("\n📱 在小程序中使用这些参数调用 wx.requestPayment()")
                return result['data']['out_trade_no']
            else:
                print(f"❌ 支付订单创建失败: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def create_h5_payment_example(self):
        """H5支付示例"""
        print("\n" + "=" * 60)
        print("H5支付示例")
        print("=" * 60)
        
        # 支付参数
        payment_data = {
            "total_fee": 200,  # 支付金额（分）
            "body": "测试商品 - H5支付",
            "attach": "h5_test_attach",
            "out_trade_no": f"H5{int(time.time())}"  # 商户订单号
        }
        
        print(f"支付参数: {json.dumps(payment_data, ensure_ascii=False, indent=2)}")
        
        try:
            # 调用API
            response = requests.post(
                f"{self.api_base_url}/api/wechat/pay/h5",
                headers=self.headers,
                json=payment_data
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ H5支付订单创建成功！")
                print(f"订单号: {result['data']['out_trade_no']}")
                print(f"预支付ID: {result['data']['prepay_id']}")
                print(f"H5支付链接: {result['data']['mweb_url']}")
                print("\n🌐 在浏览器中打开上述链接进行支付")
                return result['data']['out_trade_no']
            else:
                print(f"❌ 支付订单创建失败: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return None
    
    def query_payment_example(self, out_trade_no: str):
        """查询支付状态示例"""
        print("\n" + "=" * 60)
        print("查询支付状态示例")
        print("=" * 60)
        
        query_data = {
            "out_trade_no": out_trade_no
        }
        
        print(f"查询参数: {json.dumps(query_data, ensure_ascii=False, indent=2)}")
        
        try:
            # 调用API
            response = requests.post(
                f"{self.api_base_url}/api/wechat/pay/query",
                headers=self.headers,
                json=query_data
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 订单查询成功！")
                data = result['data']
                print(f"订单号: {data['out_trade_no']}")
                print(f"支付状态: {data['trade_state']}")
                print(f"状态描述: {data['trade_state_desc']}")
                if data.get('transaction_id'):
                    print(f"微信交易号: {data['transaction_id']}")
            else:
                print(f"❌ 订单查询失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def create_refund_example(self, out_trade_no: str):
        """退款示例"""
        print("\n" + "=" * 60)
        print("退款示例")
        print("=" * 60)
        
        refund_data = {
            "out_trade_no": out_trade_no,
            "out_refund_no": f"RF{int(time.time())}",  # 退款单号
            "total_fee": 100,  # 原订单金额
            "refund_fee": 100,  # 退款金额
            "refund_desc": "测试退款"
        }
        
        print(f"退款参数: {json.dumps(refund_data, ensure_ascii=False, indent=2)}")
        
        try:
            # 调用API
            response = requests.post(
                f"{self.api_base_url}/api/wechat/pay/refund",
                headers=self.headers,
                json=refund_data
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 退款申请成功！")
                data = result['data']
                print(f"退款单号: {data['out_refund_no']}")
                print(f"微信退款ID: {data['refund_id']}")
            else:
                print(f"❌ 退款申请失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def get_payment_status_example(self, out_trade_no: str):
        """获取支付状态示例"""
        print("\n" + "=" * 60)
        print("获取支付状态示例")
        print("=" * 60)
        
        try:
            # 调用API
            response = requests.get(
                f"{self.api_base_url}/api/wechat/pay/status/{out_trade_no}"
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 获取支付状态成功！")
                data = result['data']
                print(f"订单号: {data['out_trade_no']}")
                print(f"支付状态: {data['trade_state']}")
                print(f"创建时间: {data['create_time']}")
                print(f"更新时间: {data['update_time']}")
                if data.get('transaction_id'):
                    print(f"微信交易号: {data['transaction_id']}")
            else:
                print(f"❌ 获取支付状态失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def get_payment_records_example(self):
        """获取支付记录示例"""
        print("\n" + "=" * 60)
        print("获取支付记录示例")
        print("=" * 60)
        
        try:
            # 调用API
            response = requests.get(
                f"{self.api_base_url}/api/wechat/pay/records?page=1&limit=5"
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 获取支付记录成功！")
                data = result['data']
                records = data['records']
                pagination = data['pagination']
                
                print(f"总记录数: {pagination['total']}")
                print(f"当前页: {pagination['page']}")
                print(f"每页数量: {pagination['limit']}")
                print(f"总页数: {pagination['pages']}")
                
                print("\n支付记录:")
                for i, record in enumerate(records, 1):
                    print(f"  {i}. 订单号: {record['out_trade_no']}")
                    print(f"     金额: {record['total_fee']}分")
                    print(f"     商品: {record['body']}")
                    print(f"     状态: {record['trade_state']}")
                    print(f"     时间: {record['create_time']}")
                    print()
            else:
                print(f"❌ 获取支付记录失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def get_dashboard_example(self):
        """获取支付看板示例"""
        print("\n" + "=" * 60)
        print("获取支付看板示例")
        print("=" * 60)
        
        try:
            # 调用API
            response = requests.get(
                f"{self.api_base_url}/api/wechat/pay/dashboard"
            )
            
            result = response.json()
            print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("\n✅ 获取支付看板成功！")
                data = result['data']
                
                print("今日统计:")
                today = data['today']
                print(f"  总订单数: {today['total_orders']}")
                print(f"  成功订单数: {today['success_orders']}")
                print(f"  成功金额: {today['success_amount']}分")
                
                print("\n总体统计:")
                total = data['total']
                print(f"  总订单数: {total['total_orders']}")
                print(f"  成功订单数: {total['success_orders']}")
                print(f"  成功金额: {total['success_amount']}分")
                
                print("\n最近7天趋势:")
                for trend in data['trend']:
                    print(f"  {trend['date']}: {trend['orders']}单, {trend['amount']}分")
            else:
                print(f"❌ 获取支付看板失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def run_all_examples(self):
        """运行所有示例"""
        print("🚀 微信支付API使用示例")
        print("=" * 60)
        print("注意: 请确保微信支付API服务已启动 (python wechat_pay_api.py)")
        print("=" * 60)
        
        # 1. 小程序支付示例
        miniprogram_order = self.create_miniprogram_payment_example()
        
        # 2. H5支付示例
        h5_order = self.create_h5_payment_example()
        
        # 3. 查询支付状态示例
        if miniprogram_order:
            self.query_payment_example(miniprogram_order)
            self.get_payment_status_example(miniprogram_order)
        
        # 4. 获取支付记录示例
        self.get_payment_records_example()
        
        # 5. 获取支付看板示例
        self.get_dashboard_example()
        
        # 6. 退款示例（如果有订单号）
        if miniprogram_order:
            print("\n等待5秒后执行退款示例...")
            time.sleep(5)
            self.create_refund_example(miniprogram_order)
        
        print("\n" + "=" * 60)
        print("✅ 所有示例执行完成！")
        print("=" * 60)

def main():
    """主函数"""
    example = WeChatPayExample()
    example.run_all_examples()

if __name__ == "__main__":
    main()