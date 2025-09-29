#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI幂等性中间件
为FastAPI应用提供幂等性保护
"""

import json
import logging
from typing import Dict, Any, Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import asyncio
from datetime import datetime

from idempotency_manager import idempotency_manager

logger = logging.getLogger(__name__)


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """FastAPI幂等性中间件"""
    
    def __init__(self, app, 
                 enable_rate_limit: bool = True,
                 enable_duplicate_check: bool = True,
                 protected_paths: list = None,
                 excluded_paths: list = None):
        """
        初始化幂等性中间件
        
        Args:
            app: FastAPI应用实例
            enable_rate_limit: 是否启用频率限制
            enable_duplicate_check: 是否启用重复检查
            protected_paths: 需要保护的路径列表（如果为None则保护所有POST/PUT/DELETE请求）
            excluded_paths: 排除的路径列表
        """
        super().__init__(app)
        self.enable_rate_limit = enable_rate_limit
        self.enable_duplicate_check = enable_duplicate_check
        self.protected_paths = protected_paths or []
        self.excluded_paths = excluded_paths or []
    
    def _should_protect_path(self, path: str, method: str) -> bool:
        """判断路径是否需要保护"""
        # 排除的路径
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return False
        
        # 只保护POST、PUT、DELETE请求
        if method not in ['POST', 'PUT', 'DELETE']:
            return False
        
        # 如果指定了保护路径，只保护这些路径
        if self.protected_paths:
            return any(path.startswith(protected) for protected in self.protected_paths)
        
        # 默认保护所有POST/PUT/DELETE请求
        return True
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """提取请求信息"""
        # 获取用户ID和会话ID（从请求状态或头部）
        user_id = getattr(request.state, 'user_id', None)
        session_id = getattr(request.state, 'session_id', None)
        
        # 从头部获取
        if not user_id:
            user_id = request.headers.get('X-User-ID')
        if not session_id:
            session_id = request.headers.get('X-Session-ID')
        
        # 获取IP地址
        ip_address = request.client.host if request.client else 'unknown'
        
        # 获取请求数据
        request_data = {}
        try:
            if hasattr(request, '_json'):
                request_data = request._json
            else:
                # 尝试从body获取
                body = request.body()
                if body:
                    request_data = json.loads(body.decode('utf-8'))
        except Exception as e:
            logger.warning(f"无法解析请求数据: {e}")
        
        return {
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'request_data': request_data
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检查是否需要保护此路径
        if not self._should_protect_path(request.url.path, request.method):
            return await call_next(request)
        
        # 提取请求信息
        request_info = self._extract_request_info(request)
        
        # 生成请求键
        request_key = idempotency_manager._generate_request_key(
            user_id=request_info['user_id'],
            session_id=request_info['session_id'],
            endpoint=f"{request.method}:{request.url.path}",
            request_data=request_info['request_data'],
            ip_address=request_info['ip_address']
        )
        
        # 检查幂等性
        check_result = idempotency_manager.check_idempotency(
            user_id=request_info['user_id'],
            session_id=request_info['session_id'],
            endpoint=f"{request.method}:{request.url.path}",
            request_data=request_info['request_data'],
            ip_address=request_info['ip_address'],
            enable_rate_limit=self.enable_rate_limit,
            enable_duplicate_check=self.enable_duplicate_check
        )
        
        # 如果是重复请求
        if check_result['is_duplicate']:
            logger.warning(f"检测到重复请求: {request_key}")
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    'success': False,
                    'error': '重复请求，请勿重复提交',
                    'error_code': 'DUPLICATE_REQUEST',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        # 如果超过频率限制
        if check_result['is_rate_limited']:
            logger.warning(f"请求频率过高: {request_key}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    'success': False,
                    'error': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        # 如果有缓存响应，直接返回
        if check_result['cached_response']:
            logger.info(f"返回缓存响应: {request_key}")
            return JSONResponse(
                status_code=200,
                content=check_result['cached_response']
            )
        
        # 执行原请求
        try:
            response = await call_next(request)
            
            # 如果响应成功，存储到缓存
            if response.status_code in [200, 201, 202]:
                try:
                    # 获取响应内容
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    
                    # 解析响应内容
                    response_data = json.loads(response_body.decode('utf-8'))
                    
                    # 存储到缓存
                    idempotency_manager.store_response(request_key, response_data)
                    
                    # 重新创建响应
                    return JSONResponse(
                        status_code=response.status_code,
                        content=response_data,
                        headers=dict(response.headers)
                    )
                except Exception as e:
                    logger.warning(f"存储响应缓存失败: {e}")
                    # 如果缓存失败，返回原响应
                    return JSONResponse(
                        status_code=response.status_code,
                        content=response_body.decode('utf-8'),
                        headers=dict(response.headers)
                    )
            else:
                return response
                
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            raise


def create_idempotency_middleware(enable_rate_limit: bool = True,
                                 enable_duplicate_check: bool = True,
                                 protected_paths: list = None,
                                 excluded_paths: list = None):
    """
    创建幂等性中间件工厂函数
    
    Args:
        enable_rate_limit: 是否启用频率限制
        enable_duplicate_check: 是否启用重复检查
        protected_paths: 需要保护的路径列表
        excluded_paths: 排除的路径列表
        
    Returns:
        中间件类
    """
    def middleware_factory(app):
        return IdempotencyMiddleware(
            app=app,
            enable_rate_limit=enable_rate_limit,
            enable_duplicate_check=enable_duplicate_check,
            protected_paths=protected_paths,
            excluded_paths=excluded_paths
        )
    
    return middleware_factory


# FastAPI装饰器
def idempotent_fastapi(ttl: int = None, 
                      enable_rate_limit: bool = True,
                      enable_duplicate_check: bool = True):
    """
    FastAPI幂等性装饰器
    
    Args:
        ttl: 响应缓存时间（秒）
        enable_rate_limit: 是否启用频率限制
        enable_duplicate_check: 是否启用重复检查
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从参数中提取request对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # 如果没有找到request对象，直接执行原函数
                return await func(*args, **kwargs)
            
            # 提取请求信息
            user_id = getattr(request.state, 'user_id', None)
            session_id = getattr(request.state, 'session_id', None)
            ip_address = request.client.host if request.client else 'unknown'
            
            # 获取请求数据
            request_data = {}
            try:
                if hasattr(request, '_json'):
                    request_data = request._json
                else:
                    body = await request.body()
                    if body:
                        request_data = json.loads(body.decode('utf-8'))
            except Exception as e:
                logger.warning(f"无法解析请求数据: {e}")
            
            # 生成请求键
            endpoint = f"{request.method}:{request.url.path}"
            request_key = idempotency_manager._generate_request_key(
                user_id=user_id,
                session_id=session_id,
                endpoint=endpoint,
                request_data=request_data,
                ip_address=ip_address
            )
            
            # 检查幂等性
            check_result = idempotency_manager.check_idempotency(
                user_id=user_id,
                session_id=session_id,
                endpoint=endpoint,
                request_data=request_data,
                ip_address=ip_address,
                enable_rate_limit=enable_rate_limit,
                enable_duplicate_check=enable_duplicate_check
            )
            
            # 如果是重复请求
            if check_result['is_duplicate']:
                logger.warning(f"检测到重复请求: {request_key}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        'success': False,
                        'error': '重复请求，请勿重复提交',
                        'error_code': 'DUPLICATE_REQUEST'
                    }
                )
            
            # 如果超过频率限制
            if check_result['is_rate_limited']:
                logger.warning(f"请求频率过高: {request_key}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        'success': False,
                        'error': '请求过于频繁，请稍后再试',
                        'error_code': 'RATE_LIMIT_EXCEEDED'
                    }
                )
            
            # 如果有缓存响应，直接返回
            if check_result['cached_response']:
                logger.info(f"返回缓存响应: {request_key}")
                return check_result['cached_response']
            
            # 执行原函数
            try:
                result = await func(*args, **kwargs)
                
                # 存储响应到缓存
                if isinstance(result, dict):
                    idempotency_manager.store_response(request_key, result, ttl)
                
                return result
                
            except Exception as e:
                logger.error(f"函数执行失败: {e}")
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试代码
    print("FastAPI幂等性中间件已加载")