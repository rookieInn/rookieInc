"""
数据库模型定义
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    travel_plans = relationship("TravelPlan", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class ScenicSpot(Base):
    """景点表"""
    __tablename__ = "scenic_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(String(50), index=True)  # 景点类型：自然风光、人文景观等
    opening_hours = Column(String(200))  # 开放时间
    ticket_price = Column(Float)  # 门票价格
    rating = Column(Float, default=0.0)  # 评分
    image_url = Column(String(500))  # 图片URL
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    plan_spots = relationship("PlanSpot", back_populates="scenic_spot")


class TravelPlan(Base):
    """旅游计划表"""
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    budget = Column(Float)  # 预算
    travel_type = Column(String(50))  # 旅行类型：亲子游、蜜月游、独自旅行等
    preferences = Column(JSON)  # 用户偏好设置
    status = Column(String(20), default="draft")  # 状态：draft, active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="travel_plans")
    plan_spots = relationship("PlanSpot", back_populates="travel_plan", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="travel_plan")


class PlanSpot(Base):
    """计划景点关联表"""
    __tablename__ = "plan_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("scenic_spots.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False)
    visit_order = Column(Integer, nullable=False)  # 访问顺序
    duration_hours = Column(Float, default=2.0)  # 预计游览时长
    notes = Column(Text)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    travel_plan = relationship("TravelPlan", back_populates="plan_spots")
    scenic_spot = relationship("ScenicSpot", back_populates="plan_spots")


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=True)
    session_id = Column(String(100), nullable=False, index=True)
    message_type = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    metadata = Column(JSON)  # 附加信息
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="conversations")
    travel_plan = relationship("TravelPlan", back_populates="conversations")


class SystemCache(Base):
    """系统缓存表"""
    __tablename__ = "system_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    cache_value = Column(Text, nullable=False)
    cache_type = Column(String(50), nullable=False)  # route_plan, scenic_spot, etc.
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic模型用于API序列化
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TravelPlanCreate(BaseModel):
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None
    travel_type: Optional[str] = None
    preferences: Optional[dict] = None


class TravelPlanResponse(BaseModel):
    id: int
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[float]
    travel_type: Optional[str]
    preferences: Optional[dict]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScenicSpotResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: str
    latitude: float
    longitude: float
    category: Optional[str]
    opening_hours: Optional[str]
    ticket_price: Optional[float]
    rating: float
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    session_id: str
    content: str
    plan_id: Optional[int] = None
    metadata: Optional[dict] = None


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    message_type: str
    content: str
    metadata: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True