"""
缓存管理模块
支持Redis缓存和内存缓存
"""
import json
import asyncio
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_ttl = settings.cache_ttl
        self.max_memory_cache_size = settings.max_cache_size
    
    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(settings.redis_url)
            await self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败，将使用内存缓存: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        # 将参数排序后生成MD5哈希
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            # 先尝试从Redis获取
            if self.redis_client:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            
            # 从内存缓存获取
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                if cache_item['expires_at'] > datetime.now():
                    return cache_item['data']
                else:
                    del self.memory_cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        data: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存数据"""
        try:
            ttl = ttl or self.cache_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # 存储到Redis
            if self.redis_client:
                await self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(data, ensure_ascii=False, default=str)
                )
            
            # 存储到内存缓存
            self.memory_cache[key] = {
                'data': data,
                'expires_at': expires_at
            }
            
            # 清理过期的内存缓存
            await self._cleanup_memory_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            # 从Redis删除
            if self.redis_client:
                await self.redis_client.delete(key)
            
            # 从内存缓存删除
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    async def _cleanup_memory_cache(self):
        """清理过期的内存缓存"""
        current_time = datetime.now()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if item['expires_at'] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # 如果内存缓存过大，删除最旧的条目
        if len(self.memory_cache) > self.max_memory_cache_size:
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]['expires_at']
            )
            excess_count = len(self.memory_cache) - self.max_memory_cache_size
            for i in range(excess_count):
                del self.memory_cache[sorted_items[i][0]]
    
    async def get_route_plan_cache(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        travel_type: Optional[str] = None,
        preferences: Optional[Dict] = None
    ) -> Optional[Dict]:
        """获取路线规划缓存"""
        cache_key = self._generate_cache_key(
            "route_plan",
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            travel_type=travel_type,
            preferences=preferences
        )
        return await self.get(cache_key)
    
    async def set_route_plan_cache(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        plan_data: Dict,
        budget: Optional[float] = None,
        travel_type: Optional[str] = None,
        preferences: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """设置路线规划缓存"""
        cache_key = self._generate_cache_key(
            "route_plan",
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            travel_type=travel_type,
            preferences=preferences
        )
        return await self.set(cache_key, plan_data, ttl)
    
    async def get_scenic_spots_cache(
        self,
        destination: str,
        category: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """获取景点信息缓存"""
        cache_key = self._generate_cache_key(
            "scenic_spots",
            destination=destination,
            category=category
        )
        return await self.get(cache_key)
    
    async def set_scenic_spots_cache(
        self,
        destination: str,
        spots_data: List[Dict],
        category: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """设置景点信息缓存"""
        cache_key = self._generate_cache_key(
            "scenic_spots",
            destination=destination,
            category=category
        )
        return await self.set(cache_key, spots_data, ttl)
    
    async def get_conversation_cache(
        self,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """获取对话历史缓存"""
        cache_key = self._generate_cache_key(
            "conversation",
            session_id=session_id,
            user_id=user_id
        )
        return await self.get(cache_key)
    
    async def set_conversation_cache(
        self,
        session_id: str,
        conversation_data: List[Dict],
        user_id: Optional[int] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """设置对话历史缓存"""
        cache_key = self._generate_cache_key(
            "conversation",
            session_id=session_id,
            user_id=user_id
        )
        return await self.set(cache_key, conversation_data, ttl)
    
    async def clear_user_cache(self, user_id: int):
        """清理用户相关缓存"""
        try:
            if self.redis_client:
                # 使用模式匹配删除用户相关缓存
                pattern = f"*:user_id:{user_id}"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            # 清理内存缓存中的用户相关数据
            user_keys = [
                key for key in self.memory_cache.keys()
                if f"user_id:{user_id}" in key
            ]
            for key in user_keys:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"清理用户缓存失败: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "memory_cache_size": len(self.memory_cache),
            "redis_connected": self.redis_client is not None,
            "cache_ttl": self.cache_ttl,
            "max_memory_cache_size": self.max_memory_cache_size
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    "redis_used_memory": info.get("used_memory_human", "N/A"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_keyspace_hits": info.get("keyspace_hits", 0),
                    "redis_keyspace_misses": info.get("keyspace_misses", 0)
                })
            except Exception as e:
                logger.error(f"获取Redis统计信息失败: {e}")
        
        return stats


# 创建全局缓存管理器实例
cache_manager = CacheManager()