#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号API代理服务器
用于海外服务器通过阿里云服务器访问微信公众号接口
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
from aiohttp.web import Request, Response
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_proxy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeChatProxy:
    """微信公众号API代理类"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.config = self.load_config(config_path)
        self.session: Optional[ClientSession] = None
        self.wechat_base_url = "https://api.weixin.qq.com"
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 8080
            },
            'security': {
                'allowed_ips': [],  # 允许访问的IP列表，空表示允许所有
                'api_key': '',  # API密钥，用于验证请求
                'rate_limit': {
                    'enabled': True,
                    'requests_per_minute': 100
                }
            },
            'wechat': {
                'timeout': 30,
                'retry_times': 3
            },
            'logging': {
                'level': 'INFO',
                'log_requests': True
            }
        }
    
    async def init_session(self):
        """初始化HTTP会话"""
        timeout = ClientTimeout(total=self.config['wechat']['timeout'])
        self.session = ClientSession(
            timeout=timeout,
            headers={
                'User-Agent': 'WeChat-Proxy/1.0',
                'Accept': 'application/json'
            }
        )
        logger.info("HTTP会话初始化完成")
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            logger.info("HTTP会话已关闭")
    
    def is_allowed_ip(self, client_ip: str) -> bool:
        """检查客户端IP是否被允许"""
        allowed_ips = self.config['security']['allowed_ips']
        if not allowed_ips:  # 空列表表示允许所有IP
            return True
        return client_ip in allowed_ips
    
    def verify_api_key(self, request: Request) -> bool:
        """验证API密钥"""
        api_key = self.config['security'].get('api_key')
        if not api_key:
            return True  # 未设置API密钥则跳过验证
        
        # 从Header或Query参数中获取API密钥
        auth_header = request.headers.get('X-API-Key')
        auth_query = request.query.get('api_key')
        
        return auth_header == api_key or auth_query == api_key
    
    async def proxy_request(self, request: Request) -> Response:
        """代理请求到微信公众号API"""
        try:
            # 获取客户端IP
            client_ip = request.remote
            
            # 检查IP白名单
            if not self.is_allowed_ip(client_ip):
                logger.warning(f"IP {client_ip} 不在白名单中")
                return web.json_response(
                    {'error': 'IP not allowed'}, 
                    status=403
                )
            
            # 验证API密钥
            if not self.verify_api_key(request):
                logger.warning(f"API密钥验证失败，IP: {client_ip}")
                return web.json_response(
                    {'error': 'Invalid API key'}, 
                    status=401
                )
            
            # 构建目标URL
            path = request.match_info.get('path', '')
            target_url = urljoin(self.wechat_base_url, path)
            
            # 添加查询参数
            if request.query:
                query_string = str(request.query)
                target_url = f"{target_url}?{query_string}"
            
            # 准备请求头
            headers = dict(request.headers)
            # 移除可能导致问题的头部
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # 获取请求体
            if request.can_read_body:
                body = await request.read()
            else:
                body = None
            
            # 记录请求日志
            if self.config['logging']['log_requests']:
                logger.info(f"代理请求: {request.method} {target_url} from {client_ip}")
            
            # 发送请求到微信公众号API
            retry_times = self.config['wechat']['retry_times']
            for attempt in range(retry_times + 1):
                try:
                    async with self.session.request(
                        method=request.method,
                        url=target_url,
                        headers=headers,
                        data=body
                    ) as response:
                        # 读取响应内容
                        response_body = await response.read()
                        
                        # 记录响应日志
                        if self.config['logging']['log_requests']:
                            logger.info(f"响应: {response.status} {len(response_body)} bytes")
                        
                        # 返回响应
                        return web.Response(
                            body=response_body,
                            status=response.status,
                            headers=dict(response.headers)
                        )
                        
                except asyncio.TimeoutError:
                    logger.warning(f"请求超时，尝试 {attempt + 1}/{retry_times + 1}")
                    if attempt == retry_times:
                        return web.json_response(
                            {'error': 'Request timeout'}, 
                            status=504
                        )
                    await asyncio.sleep(1)  # 等待1秒后重试
                    
                except Exception as e:
                    logger.error(f"请求失败: {e}")
                    if attempt == retry_times:
                        return web.json_response(
                            {'error': 'Proxy request failed'}, 
                            status=502
                        )
                    await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"代理请求处理失败: {e}")
            return web.json_response(
                {'error': 'Internal server error'}, 
                status=500
            )
    
    async def health_check(self, request: Request) -> Response:
        """健康检查接口"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': int(time.time()),
            'version': '1.0.0'
        })
    
    async def get_stats(self, request: Request) -> Response:
        """获取代理统计信息"""
        # 这里可以添加统计信息的收集和返回
        return web.json_response({
            'status': 'running',
            'uptime': 'N/A',  # 可以添加运行时间统计
            'requests_processed': 'N/A'  # 可以添加请求计数
        })

def create_app(config_path: str = 'config.yaml') -> web.Application:
    """创建Web应用"""
    proxy = WeChatProxy(config_path)
    
    app = web.Application()
    
    # 添加路由
    app.router.add_get('/health', proxy.health_check)
    app.router.add_get('/stats', proxy.get_stats)
    app.router.add_route('*', '/{path:.*}', proxy.proxy_request)
    
    # 添加中间件
    @web.middleware
    async def cors_middleware(request: Request, handler):
        """CORS中间件"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
        return response
    
    app.middlewares.append(cors_middleware)
    
    # 添加启动和关闭事件
    async def on_startup(app):
        await proxy.init_session()
        logger.info("代理服务器启动完成")
    
    async def on_cleanup(app):
        await proxy.close_session()
        logger.info("代理服务器关闭完成")
    
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    return app

async def main():
    """主函数"""
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    app = create_app(config_path)
    
    # 从配置文件获取服务器配置
    server_config = app['proxy'].config['server']
    host = server_config['host']
    port = server_config['port']
    
    logger.info(f"启动代理服务器: {host}:{port}")
    
    # 启动服务器
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"代理服务器已启动，监听 {host}:{port}")
    logger.info("按 Ctrl+C 停止服务器")
    
    try:
        # 保持服务器运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务器...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())