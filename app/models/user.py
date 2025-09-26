"""
用户相关数据模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 用户偏好设置
    preferred_language = Column(String(10), default="zh")
    travel_style = Column(String(50))  # 亲子游、蜜月游、独自旅行等
    budget_range = Column(String(50))  # 预算范围
    interests = Column(Text)  # 兴趣点，JSON格式存储

class UserHistory(Base):
    """用户历史记录模型"""
    __tablename__ = "user_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    destination = Column(String(100), nullable=False)
    travel_dates = Column(String(50))  # 旅行日期范围
    budget = Column(String(50))  # 预算
    route_plan = Column(Text)  # 路线规划详情，JSON格式
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class UserFavorite(Base):
    """用户收藏模型"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    route_id = Column(String(100), nullable=False)  # 路线ID
    route_name = Column(String(200), nullable=False)
    route_data = Column(Text)  # 路线数据，JSON格式
    created_at = Column(DateTime(timezone=True), server_default=func.now())