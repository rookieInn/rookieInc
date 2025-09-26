"""
旅游相关数据模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class ScenicSpot(Base):
    """景点模型"""
    __tablename__ = "scenic_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(200))  # 位置
    latitude = Column(Float)  # 纬度
    longitude = Column(Float)  # 经度
    opening_hours = Column(String(200))  # 开放时间
    ticket_price = Column(String(100))  # 门票价格
    rating = Column(Float)  # 评分
    category = Column(String(50))  # 景点类别
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Hotel(Base):
    """酒店模型"""
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    price_range = Column(String(100))  # 价格范围
    rating = Column(Float)
    amenities = Column(Text)  # 设施，JSON格式
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Transportation(Base):
    """交通信息模型"""
    __tablename__ = "transportations"
    
    id = Column(Integer, primary_key=True, index=True)
    from_location = Column(String(200), nullable=False)
    to_location = Column(String(200), nullable=False)
    transport_type = Column(String(50))  # 交通方式：飞机、火车、汽车等
    duration = Column(String(50))  # 行程时间
    price = Column(String(100))  # 价格
    distance = Column(Float)  # 距离（公里）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RoutePlan(Base):
    """路线规划模型"""
    __tablename__ = "route_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(200), nullable=False)
    destination = Column(String(100), nullable=False)
    duration_days = Column(Integer)  # 行程天数
    budget_range = Column(String(50))
    route_data = Column(Text)  # 路线详情，JSON格式
    is_public = Column(Boolean, default=False)  # 是否公开
    created_by = Column(Integer)  # 创建者ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())