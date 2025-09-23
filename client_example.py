#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端示例：展示如何通过代理访问微信公众号API
"""

import asyncio
import aiohttp
import json

class WeChatClient:
    """微信公众号API客户端"""
    
    def __init__(self, proxy_url: str, api_key: str = None):
        self.proxy_url = proxy_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self):
        """获取请求头"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WeChat-Client/1.0'
        }
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers
    
    async def get_access_token(self, appid: str, secret: str):
        """获取access_token"""
        url = f"{self.proxy_url}/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': appid,
            'secret': secret
        }
        
        async with self.session.get(url, params=params, headers=self._get_headers()) as response:
            return await response.json()
    
    async def send_template_message(self, access_token: str, template_data: dict):
        """发送模板消息"""
        url = f"{self.proxy_url}/cgi-bin/message/template/send"
        params = {'access_token': access_token}
        data = json.dumps(template_data, ensure_ascii=False)
        
        async with self.session.post(
            url, 
            params=params, 
            data=data, 
            headers=self._get_headers()
        ) as response:
            return await response.json()
    
    async def get_user_info(self, access_token: str, openid: str):
        """获取用户信息"""
        url = f"{self.proxy_url}/cgi-bin/user/info"
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        async with self.session.get(url, params=params, headers=self._get_headers()) as response:
            return await response.json()
    
    async def create_menu(self, access_token: str, menu_data: dict):
        """创建自定义菜单"""
        url = f"{self.proxy_url}/cgi-bin/menu/create"
        params = {'access_token': access_token}
        data = json.dumps(menu_data, ensure_ascii=False)
        
        async with self.session.post(
            url, 
            params=params, 
            data=data, 
            headers=self._get_headers()
        ) as response:
            return await response.json()

async def main():
    """示例用法"""
    # 配置代理服务器地址和API密钥
    proxy_url = "http://your-aliyun-server:8080"  # 替换为您的阿里云服务器地址
    api_key = "your-api-key"  # 如果配置了API密钥
    
    # 微信公众号配置
    appid = "your-appid"
    secret = "your-secret"
    
    async with WeChatClient(proxy_url, api_key) as client:
        try:
            # 1. 获取access_token
            print("正在获取access_token...")
            token_result = await client.get_access_token(appid, secret)
            print(f"Token结果: {json.dumps(token_result, indent=2, ensure_ascii=False)}")
            
            if 'access_token' in token_result:
                access_token = token_result['access_token']
                
                # 2. 获取用户信息示例
                print("\n正在获取用户信息...")
                user_info = await client.get_user_info(access_token, "user-openid")
                print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
                
                # 3. 发送模板消息示例
                print("\n正在发送模板消息...")
                template_data = {
                    "touser": "user-openid",
                    "template_id": "template-id",
                    "data": {
                        "first": {"value": "测试消息", "color": "#173177"},
                        "keyword1": {"value": "测试", "color": "#173177"},
                        "remark": {"value": "这是通过代理发送的消息", "color": "#173177"}
                    }
                }
                message_result = await client.send_template_message(access_token, template_data)
                print(f"消息发送结果: {json.dumps(message_result, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"请求失败: {e}")

if __name__ == '__main__':
    asyncio.run(main())