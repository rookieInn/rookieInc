#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接口幂等性管理器
提供防重复提交、请求去重、限流等功能
"""

import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
import redis
from configparser import ConfigParser

logger = logging.getLogger(__name__)


class IdempotencyManager:
    """幂等性管理器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, config_file: str = 'config.ini'):
        """
        初始化幂等性管理器
        
        Args:
            redis_client: Redis客户端实例
            config_file: 配置文件路径
        """
        self.redis_client = redis_client
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 从配置文件读取设置
        self.default_ttl = self.config.getint('idempotency', 'default_ttl', fallback=300)  # 5分钟
        self.max_requests_per_minute = self.config.getint('idempotency', 'max_requests_per_minute', fallback=60)
        self.max_requests_per_hour = self.config.getint('idempotency', 'max_requests_per_hour', fallback=1000)
        self.duplicate_window = self.config.getint('idempotency', 'duplicate_window', fallback=30)  # 30秒内重复请求视为重复
        
        # 如果没有提供Redis客户端，尝试创建默认连接
        if not self.redis_client:
            try:
                redis_host = self.config.get('redis', 'host', fallback='localhost')
                redis_port = self.config.getint('redis', 'port', fallback=6379)
                redis_db = self.config.getint('redis', 'db', fallback=0)
                redis_password = self.config.get('redis', 'password', fallback=None)
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True
                )
                # 测试连接
                self.redis_client.ping()
                logger.info("✅ Redis连接成功")
            except Exception as e:
                logger.warning(f"⚠️ Redis连接失败，将使用内存存储: {e}")
                self.redis_client = None
                self._memory_cache = {}
    
    def _generate_request_key(self, 
                            user_id: Optional[str] = None,
                            session_id: Optional[str] = None,
                            endpoint: str = '',
                            request_data: Dict[str, Any] = None,
                            ip_address: Optional[str] = None) -> str:
        """
        生成请求唯一标识符
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            endpoint: 接口端点
            request_data: 请求数据
            ip_address: IP地址
            
        Returns:
            请求唯一标识符
        """
        # 构建请求指纹
        fingerprint_data = {
            'user_id': user_id,
            'session_id': session_id,
            'endpoint': endpoint,
            'ip_address': ip_address,
            'data': request_data or {}
        }
        
        # 生成MD5哈希
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(fingerprint_str.encode('utf-8')).hexdigest()
    
    def _get_cache_key(self, request_key: str, key_type: str = 'idempotency') -> str:
        """生成缓存键"""
        return f"idempotency:{key_type}:{request_key}"
    
    def _is_duplicate_request(self, request_key: str) -> bool:
        """
        检查是否为重复请求
        
        Args:
            request_key: 请求唯一标识符
            
        Returns:
            是否为重复请求
        """
        cache_key = self._get_cache_key(request_key, 'duplicate')
        
        if self.redis_client:
            try:
                # 使用Redis的SET命令，如果键不存在则设置，存在则返回False
                result = self.redis_client.set(cache_key, '1', ex=self.duplicate_window, nx=True)
                return not result  # 如果设置失败（键已存在），则为重复请求
            except Exception as e:
                logger.error(f"Redis操作失败: {e}")
                return False
        else:
            # 使用内存缓存
            current_time = time.time()
            if cache_key in self._memory_cache:
                last_request_time = self._memory_cache[cache_key]
                if current_time - last_request_time < self.duplicate_window:
                    return True
                else:
                    # 过期，更新为当前时间
                    self._memory_cache[cache_key] = current_time
                    return False
            else:
                self._memory_cache[cache_key] = current_time
                return False
    
    def _check_rate_limit(self, user_id: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """
        检查请求频率限制
        
        Args:
            user_id: 用户ID
            ip_address: IP地址
            
        Returns:
            是否超过频率限制
        """
        # 优先使用用户ID，其次使用IP地址
        identifier = user_id or ip_address or 'anonymous'
        
        minute_key = f"rate_limit:minute:{identifier}:{int(time.time() // 60)}"
        hour_key = f"rate_limit:hour:{identifier}:{int(time.time() // 3600)}"
        
        if self.redis_client:
            try:
                # 检查分钟级限制
                minute_count = self.redis_client.incr(minute_key)
                if minute_count == 1:
                    self.redis_client.expire(minute_key, 60)
                
                # 检查小时级限制
                hour_count = self.redis_client.incr(hour_key)
                if hour_count == 1:
                    self.redis_client.expire(hour_key, 3600)
                
                return minute_count > self.max_requests_per_minute or hour_count > self.max_requests_per_hour
                
            except Exception as e:
                logger.error(f"Redis频率限制检查失败: {e}")
                return False
        else:
            # 内存模式下的简化频率限制
            current_time = time.time()
            minute_window = int(current_time // 60)
            hour_window = int(current_time // 3600)
            
            minute_key = f"rate_limit:minute:{identifier}:{minute_window}"
            hour_key = f"rate_limit:hour:{identifier}:{hour_window}"
            
            # 清理过期的内存缓存
            expired_keys = [k for k, v in self._memory_cache.items() 
                          if k.startswith('rate_limit:') and current_time - v > 3600]
            for k in expired_keys:
                del self._memory_cache[k]
            
            # 检查限制
            minute_count = self._memory_cache.get(minute_key, 0) + 1
            hour_count = self._memory_cache.get(hour_key, 0) + 1
            
            self._memory_cache[minute_key] = minute_count
            self._memory_cache[hour_key] = hour_count
            
            return minute_count > self.max_requests_per_minute or hour_count > self.max_requests_per_hour
    
    def _store_response(self, request_key: str, response_data: Dict[str, Any], ttl: int = None):
        """
        存储响应数据
        
        Args:
            request_key: 请求唯一标识符
            response_data: 响应数据
            ttl: 生存时间（秒）
        """
        if ttl is None:
            ttl = self.default_ttl
            
        cache_key = self._get_cache_key(request_key, 'response')
        
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, ttl, json.dumps(response_data, ensure_ascii=False))
            except Exception as e:
                logger.error(f"存储响应失败: {e}")
        else:
            # 内存存储
            self._memory_cache[cache_key] = {
                'data': response_data,
                'expires': time.time() + ttl
            }
    
    def _get_cached_response(self, request_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的响应数据
        
        Args:
            request_key: 请求唯一标识符
            
        Returns:
            缓存的响应数据，如果不存在则返回None
        """
        cache_key = self._get_cache_key(request_key, 'response')
        
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.error(f"获取缓存响应失败: {e}")
        else:
            # 内存缓存
            if cache_key in self._memory_cache:
                cache_entry = self._memory_cache[cache_key]
                if time.time() < cache_entry['expires']:
                    return cache_entry['data']
                else:
                    # 过期，删除
                    del self._memory_cache[cache_key]
        
        return None
    
    def check_idempotency(self, 
                         user_id: Optional[str] = None,
                         session_id: Optional[str] = None,
                         endpoint: str = '',
                         request_data: Dict[str, Any] = None,
                         ip_address: Optional[str] = None,
                         enable_rate_limit: bool = True,
                         enable_duplicate_check: bool = True) -> Dict[str, Any]:
        """
        检查请求的幂等性
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            endpoint: 接口端点
            request_data: 请求数据
            ip_address: IP地址
            enable_rate_limit: 是否启用频率限制
            enable_duplicate_check: 是否启用重复检查
            
        Returns:
            检查结果字典
        """
        request_key = self._generate_request_key(
            user_id=user_id,
            session_id=session_id,
            endpoint=endpoint,
            request_data=request_data,
            ip_address=ip_address
        )
        
        result = {
            'is_duplicate': False,
            'is_rate_limited': False,
            'cached_response': None,
            'request_key': request_key
        }
        
        # 检查重复请求
        if enable_duplicate_check:
            result['is_duplicate'] = self._is_duplicate_request(request_key)
        
        # 检查频率限制
        if enable_rate_limit and not result['is_duplicate']:
            result['is_rate_limited'] = self._check_rate_limit(user_id, ip_address)
        
        # 如果不是重复请求且未超过频率限制，检查是否有缓存响应
        if not result['is_duplicate'] and not result['is_rate_limited']:
            result['cached_response'] = self._get_cached_response(request_key)
        
        return result
    
    def store_response(self, 
                      request_key: str, 
                      response_data: Dict[str, Any], 
                      ttl: int = None):
        """
        存储响应数据
        
        Args:
            request_key: 请求唯一标识符
            response_data: 响应数据
            ttl: 生存时间（秒）
        """
        self._store_response(request_key, response_data, ttl)
    
    def clear_cache(self, request_key: str = None):
        """
        清除缓存
        
        Args:
            request_key: 要清除的请求键，如果为None则清除所有缓存
        """
        if self.redis_client:
            try:
                if request_key:
                    # 清除特定请求的缓存
                    duplicate_key = self._get_cache_key(request_key, 'duplicate')
                    response_key = self._get_cache_key(request_key, 'response')
                    self.redis_client.delete(duplicate_key, response_key)
                else:
                    # 清除所有幂等性相关缓存
                    pattern = "idempotency:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"清除缓存失败: {e}")
        else:
            # 内存缓存清理
            if request_key:
                duplicate_key = self._get_cache_key(request_key, 'duplicate')
                response_key = self._get_cache_key(request_key, 'response')
                self._memory_cache.pop(duplicate_key, None)
                self._memory_cache.pop(response_key, None)
            else:
                # 清除所有幂等性相关缓存
                keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith('idempotency:')]
                for k in keys_to_remove:
                    del self._memory_cache[k]


# 全局幂等性管理器实例
idempotency_manager = IdempotencyManager()


def idempotent(ttl: int = None, 
               enable_rate_limit: bool = True,
               enable_duplicate_check: bool = True,
               key_fields: list = None):
    """
    幂等性装饰器
    
    Args:
        ttl: 响应缓存时间（秒）
        enable_rate_limit: 是否启用频率限制
        enable_duplicate_check: 是否启用重复检查
        key_fields: 用于生成请求键的字段列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从函数参数中提取信息
            request = None
            user_id = None
            session_id = None
            ip_address = None
            request_data = {}
            
            # 尝试从参数中获取request对象
            for arg in args:
                if hasattr(arg, 'get_json') or hasattr(arg, 'json'):  # Flask或FastAPI request
                    request = arg
                    break
            
            if request:
                # 获取请求信息
                if hasattr(request, 'remote_addr'):  # Flask
                    ip_address = request.remote_addr
                    user_id = getattr(request, 'user_id', None)
                    session_id = getattr(request, 'session_id', None)
                    try:
                        request_data = request.get_json() or {}
                    except:
                        request_data = {}
                elif hasattr(request, 'client'):  # FastAPI
                    ip_address = request.client.host
                    user_id = getattr(request.state, 'user_id', None)
                    session_id = getattr(request.state, 'session_id', None)
                    try:
                        request_data = request.json() if hasattr(request, 'json') else {}
                    except:
                        request_data = {}
            
            # 生成请求键
            endpoint = f"{func.__module__}.{func.__name__}"
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
                return {
                    'success': False,
                    'error': '重复请求，请勿重复提交',
                    'error_code': 'DUPLICATE_REQUEST'
                }
            
            # 如果超过频率限制
            if check_result['is_rate_limited']:
                logger.warning(f"请求频率过高: {request_key}")
                return {
                    'success': False,
                    'error': '请求过于频繁，请稍后再试',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }
            
            # 如果有缓存响应，直接返回
            if check_result['cached_response']:
                logger.info(f"返回缓存响应: {request_key}")
                return check_result['cached_response']
            
            # 执行原函数
            try:
                result = func(*args, **kwargs)
                
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
    manager = IdempotencyManager()
    
    # 测试请求键生成
    test_key = manager._generate_request_key(
        user_id="test_user",
        endpoint="/api/test",
        request_data={"test": "data"},
        ip_address="127.0.0.1"
    )
    print(f"生成的请求键: {test_key}")
    
    # 测试幂等性检查
    result = manager.check_idempotency(
        user_id="test_user",
        endpoint="/api/test",
        request_data={"test": "data"},
        ip_address="127.0.0.1"
    )
    print(f"幂等性检查结果: {result}")