"""
API路由定义
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List
import json

from app.schemas.travel import (
    TravelRequest, TravelResponse, UserProfile, 
    UserHistoryResponse, UserFavoriteResponse
)
from app.core.ai_agent import TravelAgent
from app.core.security import verify_token, check_admin_permission
from app.core.database import get_db
from sqlalchemy.orm import Session

# 创建路由器
router = APIRouter()

# 创建AI智能体实例
travel_agent = TravelAgent()

@router.post("/plan", response_model=TravelResponse)
async def create_travel_plan(
    request: TravelRequest,
    current_user: str = Depends(verify_token)
):
    """
    创建旅游路线规划
    
    - **destination**: 目的地
    - **travel_dates**: 旅行日期
    - **duration_days**: 行程天数
    - **budget**: 预算范围
    - **travel_style**: 旅行风格（可选）
    - **interests**: 兴趣点列表（可选）
    - **special_requirements**: 特殊要求（可选）
    - **group_size**: 人数
    """
    try:
        # 将请求转换为字典
        request_dict = request.dict()
        
        # 调用AI智能体处理请求
        result = await travel_agent.process_request(
            user_id=current_user,
            request=json.dumps(request_dict, ensure_ascii=False),
            context=request_dict
        )
        
        return TravelResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建路线规划失败: {str(e)}"
        )

@router.get("/history", response_model=List[UserHistoryResponse])
async def get_user_history(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """获取用户历史记录"""
    # 这里应该从数据库查询用户历史记录
    # 简化实现，返回空列表
    return []

@router.post("/favorites/{route_id}")
async def add_to_favorites(
    route_id: str,
    route_name: str,
    route_data: dict,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """添加路线到收藏"""
    # 这里应该将路线保存到数据库
    return {"message": "路线已添加到收藏", "route_id": route_id}

@router.get("/favorites", response_model=List[UserFavoriteResponse])
async def get_user_favorites(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """获取用户收藏的路线"""
    # 这里应该从数据库查询用户收藏
    # 简化实现，返回空列表
    return []

@router.delete("/favorites/{favorite_id}")
async def remove_from_favorites(
    favorite_id: int,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """从收藏中移除路线"""
    # 这里应该从数据库删除收藏记录
    return {"message": "路线已从收藏中移除", "favorite_id": favorite_id}

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """获取用户档案"""
    # 这里应该从数据库查询用户档案
    # 简化实现，返回默认档案
    return UserProfile(
        username=current_user,
        email=f"{current_user}@example.com",
        preferred_language="zh"
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile: UserProfile,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """更新用户档案"""
    # 这里应该更新数据库中的用户档案
    return profile

@router.get("/destinations")
async def get_popular_destinations():
    """获取热门目的地列表"""
    destinations = [
        {"name": "北京", "description": "历史文化名城", "image": "/images/beijing.jpg"},
        {"name": "上海", "description": "现代化国际都市", "image": "/images/shanghai.jpg"},
        {"name": "杭州", "description": "人间天堂", "image": "/images/hangzhou.jpg"},
        {"name": "西安", "description": "古都长安", "image": "/images/xian.jpg"},
        {"name": "成都", "description": "天府之国", "image": "/images/chengdu.jpg"}
    ]
    return destinations

@router.get("/weather/{location}")
async def get_weather_info(location: str, date: str = None):
    """获取天气信息"""
    from app.services.gis_service import GISService
    gis_service = GISService()
    
    weather_info = await gis_service.get_weather_info(location, date or "today")
    return weather_info

# 管理员接口
@router.post("/admin/scenic-spots")
async def add_scenic_spot(
    spot_data: dict,
    current_user: str = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """添加景点（管理员功能）"""
    # 这里应该将景点数据保存到数据库
    return {"message": "景点添加成功", "spot_id": 1}

@router.put("/admin/scenic-spots/{spot_id}")
async def update_scenic_spot(
    spot_id: int,
    spot_data: dict,
    current_user: str = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """更新景点信息（管理员功能）"""
    # 这里应该更新数据库中的景点信息
    return {"message": "景点信息更新成功", "spot_id": spot_id}

@router.delete("/admin/scenic-spots/{spot_id}")
async def delete_scenic_spot(
    spot_id: int,
    current_user: str = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """删除景点（管理员功能）"""
    # 这里应该从数据库删除景点
    return {"message": "景点删除成功", "spot_id": spot_id}

@router.get("/admin/stats")
async def get_admin_stats(
    current_user: str = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    """获取系统统计信息（管理员功能）"""
    stats = {
        "total_users": 1000,
        "total_plans": 5000,
        "popular_destinations": [
            {"name": "北京", "count": 500},
            {"name": "上海", "count": 400},
            {"name": "杭州", "count": 300}
        ],
        "system_status": "healthy"
    }
    return stats