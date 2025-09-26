"""
旅游相关数据模式
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TravelRequest(BaseModel):
    """旅游请求模型"""
    destination: str = Field(..., description="目的地")
    travel_dates: str = Field(..., description="旅行日期")
    duration_days: int = Field(..., ge=1, le=30, description="行程天数")
    budget: str = Field(..., description="预算范围")
    travel_style: Optional[str] = Field(None, description="旅行风格")
    interests: Optional[List[str]] = Field(default=[], description="兴趣点")
    special_requirements: Optional[str] = Field(None, description="特殊要求")
    group_size: int = Field(default=1, ge=1, description="人数")

class ScenicSpotResponse(BaseModel):
    """景点响应模型"""
    id: int
    name: str
    description: str
    location: str
    latitude: float
    longitude: float
    opening_hours: str
    ticket_price: str
    rating: float
    category: str

class HotelResponse(BaseModel):
    """酒店响应模型"""
    id: int
    name: str
    description: str
    location: str
    latitude: float
    longitude: float
    price_range: str
    rating: float
    amenities: List[str]

class DailyItinerary(BaseModel):
    """每日行程模型"""
    day: int
    date: str
    morning: str
    afternoon: str
    evening: str
    meals: Dict[str, str]

class BudgetEstimate(BaseModel):
    """预算估算模型"""
    total_estimate: float
    breakdown: Dict[str, float]

class RoutePlanResponse(BaseModel):
    """路线规划响应模型"""
    destination: str
    duration_days: int
    budget_estimate: BudgetEstimate
    daily_itinerary: List[DailyItinerary]
    accommodation: Dict[str, Any]
    transportation: List[Dict[str, Any]]
    tips: List[str]
    created_at: str

class TravelResponse(BaseModel):
    """旅游响应模型"""
    success: bool
    route_plan: Optional[RoutePlanResponse] = None
    requirements: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

class UserProfile(BaseModel):
    """用户档案模型"""
    username: str
    email: str
    preferred_language: str = "zh"
    travel_style: Optional[str] = None
    budget_range: Optional[str] = None
    interests: Optional[List[str]] = None

class UserHistoryResponse(BaseModel):
    """用户历史记录响应模型"""
    id: int
    destination: str
    travel_dates: str
    budget: str
    route_plan: Dict[str, Any]
    created_at: datetime

class UserFavoriteResponse(BaseModel):
    """用户收藏响应模型"""
    id: int
    route_id: str
    route_name: str
    route_data: Dict[str, Any]
    created_at: datetime