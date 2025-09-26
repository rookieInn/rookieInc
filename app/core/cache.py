"""
缓存管理模块
使用Redis实现高性能缓存
"""

import json
import pickle
from typing import Any, Optional
from app.core.database import get_redis

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = None
    
    async def _get_redis(self):
        """获取Redis客户端"""
        if self.redis_client is None:
            self.redis_client = await get_redis()
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        try:
            redis_client = await self._get_redis()
            data = await redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存数据"""
        try:
            redis_client = await self._get_redis()
            data = pickle.dumps(value)
            await redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            redis_client = await self._get_redis()
            await redis_client.delete(key)
            return True
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        try:
            redis_client = await self._get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"缓存清除失败: {e}")
            return 0