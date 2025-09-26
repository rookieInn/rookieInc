"""
API数据模型和模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class RoutePlanRequest(BaseModel):
    """路线规划请求"""
    destination: str = Field(..., description="目的地", min_length=1, max_length=100)
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")
    budget: Optional[float] = Field(None, description="预算", ge=0, le=1000000)
    travel_type: Optional[str] = Field(None, description="旅行类型")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")
    max_daily_spots: Optional[int] = Field(3, description="每日最大景点数", ge=1, le=10)
    max_daily_hours: Optional[float] = Field(10.0, description="每日最大游览小时数", ge=1, le=16)
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('日期格式必须为 YYYY-MM-DD')
    
    @validator('destination')
    def validate_destination(cls, v):
        if not v.strip():
            raise ValueError('目的地不能为空')
        return v.strip()
    
    @validator('budget')
    def validate_budget(cls, v):
        if v is not None and v <= 0:
            raise ValueError('预算必须大于0')
        return v


class RoutePlanResponse(BaseModel):
    """路线规划响应"""
    plan_id: Optional[int] = None
    destination: str
    start_date: str
    end_date: str
    travel_days: int
    daily_plans: List[Dict[str, Any]]
    total_cost: Dict[str, float]
    map_data: Dict[str, Any]
    constraints: Dict[str, Any]
    generated_at: str
    status: str = "success"
    
    class Config:
        from_attributes = True


class ScenicSpotRequest(BaseModel):
    """景点查询请求"""
    destination: str = Field(..., description="目的地")
    category: Optional[str] = Field(None, description="景点类别")
    min_rating: Optional[float] = Field(None, description="最低评分", ge=0, le=5)
    max_price: Optional[float] = Field(None, description="最高价格", ge=0)


class ScenicSpotResponse(BaseModel):
    """景点信息响应"""
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


class ConversationRequest(BaseModel):
    """对话请求"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="用户消息", min_length=1, max_length=1000)
    plan_id: Optional[int] = Field(None, description="关联的路线规划ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="附加信息")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()


class ConversationResponse(BaseModel):
    """对话响应"""
    id: int
    session_id: str
    message_type: str
    content: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RouteOptimizationRequest(BaseModel):
    """路线优化请求"""
    plan_id: int = Field(..., description="路线规划ID")
    feedback: str = Field(..., description="用户反馈", min_length=1, max_length=1000)
    constraints: Optional[Dict[str, Any]] = Field(None, description="优化约束")
    
    @validator('feedback')
    def validate_feedback(cls, v):
        if not v.strip():
            raise ValueError('反馈内容不能为空')
        return v.strip()


class RouteOptimizationResponse(BaseModel):
    """路线优化响应"""
    original_plan: Dict[str, Any]
    optimized_plan: Dict[str, Any]
    optimization_suggestions: List[str]
    optimized_at: str


class UserPreferences(BaseModel):
    """用户偏好设置"""
    categories: Optional[List[str]] = Field(None, description="偏好的景点类别")
    min_rating: Optional[float] = Field(None, description="最低评分要求", ge=0, le=5)
    max_price: Optional[float] = Field(None, description="最高价格限制", ge=0)
    travel_style: Optional[str] = Field(None, description="旅行风格")
    special_requirements: Optional[List[str]] = Field(None, description="特殊要求")


class TravelPlanCreate(BaseModel):
    """创建旅游计划请求"""
    title: str = Field(..., description="计划标题", min_length=1, max_length=200)
    destination: str = Field(..., description="目的地", min_length=1, max_length=100)
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    budget: Optional[float] = Field(None, description="预算", ge=0)
    travel_type: Optional[str] = Field(None, description="旅行类型")
    preferences: Optional[UserPreferences] = Field(None, description="用户偏好")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v


class TravelPlanResponse(BaseModel):
    """旅游计划响应"""
    id: int
    title: str
    destination: str
    start_date: datetime
    end_date: datetime
    budget: Optional[float]
    travel_type: Optional[str]
    preferences: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """用户创建请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    email: str = Field(..., description="邮箱", max_length=100)
    password: str = Field(..., description="密码", min_length=6, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('邮箱格式不正确')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user: UserResponse


class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    status: str
    timestamp: str
    cache: Dict[str, Any]
    ai_model: str


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: str
    timestamp: str


class SuccessResponse(BaseModel):
    """成功响应"""
    message: str
    timestamp: str


class PaginationRequest(BaseModel):
    """分页请求"""
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(10, description="每页大小", ge=1, le=100)


class PaginationResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class MapDataResponse(BaseModel):
    """地图数据响应"""
    spots: List[Dict[str, Any]]
    routes: List[Dict[str, Any]]
    center: Optional[tuple]


class CostBreakdownResponse(BaseModel):
    """费用明细响应"""
    tickets: float
    meals: float
    transport: float
    accommodation: float
    total: float


class DailyPlanResponse(BaseModel):
    """每日计划响应"""
    date: str
    spots: List[Dict[str, Any]]
    total_spots: int
    total_duration: float
    total_cost: float
    recommendations: List[str]


class AIResponse(BaseModel):
    """AI响应"""
    content: str
    model: str
    generated_at: str
    confidence: Optional[float] = None


class CacheStatsResponse(BaseModel):
    """缓存统计响应"""
    memory_cache_size: int
    redis_connected: bool
    cache_ttl: int
    max_memory_cache_size: int
    redis_used_memory: Optional[str] = None
    redis_connected_clients: Optional[int] = None
    redis_keyspace_hits: Optional[int] = None
    redis_keyspace_misses: Optional[int] = None