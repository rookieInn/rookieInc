"""
应用配置管理
"""

from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 数据库配置
    database_url: str = "sqlite:///./travel_agent.db"
    redis_url: str = "redis://localhost:6379"
    
    # AI模型配置
    openai_api_key: Optional[str] = None
    tongyi_api_key: Optional[str] = None
    wenxin_api_key: Optional[str] = None
    
    # 应用配置
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 外部API配置
    maps_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    
    # 性能配置
    max_concurrent_users: int = 200
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    
    # 安全配置
    enable_content_filtering: bool = True
    enable_sensitive_word_detection: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 全局配置实例
settings = Settings()