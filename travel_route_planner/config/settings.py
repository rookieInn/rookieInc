"""
AI旅游路线规划系统配置文件
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """系统配置类"""
    
    # 应用基础配置
    app_name: str = "AI旅游路线规划系统"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "mysql+pymysql://root:password@localhost:3306/travel_planner"
    redis_url: str = "redis://localhost:6379/0"
    
    # AI模型配置
    # 通义千问配置
    dashscope_api_key: Optional[str] = None
    qwen_model: str = "qwen-turbo"
    
    # 文心一言配置
    qianfan_ak: Optional[str] = None
    qianfan_sk: Optional[str] = None
    
    # OpenAI配置（备用）
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # 地图服务配置
    mapbox_token: Optional[str] = None
    baidu_map_ak: Optional[str] = None
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 缓存配置
    cache_ttl: int = 3600  # 1小时
    max_cache_size: int = 1000
    
    # 性能配置
    max_concurrent_requests: int = 200
    request_timeout: int = 60
    
    # 文件存储配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()