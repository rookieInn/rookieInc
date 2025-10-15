"""
API路由定义
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database.database import get_db
from database.models import User, TravelPlan, ScenicSpot, Conversation, Comment, CommentLike
from backend.ai_models import ai_manager
from backend.route_planner import route_planner, RouteConstraint
from backend.cache_manager import cache_manager
from backend.auth import get_current_user, create_access_token, verify_password, get_password_hash
from backend.schemas import (
    UserCreate, UserResponse, TravelPlanCreate, TravelPlanResponse,
    ConversationCreate, ConversationResponse, RoutePlanRequest, RoutePlanResponse,
    CommentCreate, CommentResponse, CommentLikeCreate, CommentLikeResponse, CommentUpdate
)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()
security = HTTPBearer()

# 认证相关路由
@router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/auth/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

# 路线规划相关路由
@router.post("/route/plan", response_model=RoutePlanResponse)
async def create_route_plan(
    plan_request: RoutePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建旅游路线规划"""
    
    # 检查缓存
    cached_plan = await cache_manager.get_route_plan_cache(
        destination=plan_request.destination,
        start_date=plan_request.start_date,
        end_date=plan_request.end_date,
        budget=plan_request.budget,
        travel_type=plan_request.travel_type,
        preferences=plan_request.preferences
    )
    
    if cached_plan:
        logger.info("返回缓存的路线规划")
        return RoutePlanResponse(**cached_plan)
    
    try:
        # 获取景点数据
        scenic_spots = await get_scenic_spots_for_destination(
            plan_request.destination, 
            db
        )
        
        # 设置路线约束
        constraints = RouteConstraint(
            max_daily_spots=plan_request.max_daily_spots or 3,
            max_daily_hours=plan_request.max_daily_hours or 10.0,
            budget_limit=plan_request.budget,
            preferred_categories=plan_request.preferences.get('categories') if plan_request.preferences else None
        )
        
        # 生成路线规划
        start_date = datetime.fromisoformat(plan_request.start_date)
        end_date = datetime.fromisoformat(plan_request.end_date)
        
        route_plan = await route_planner.plan_route(
            destination=plan_request.destination,
            start_date=start_date,
            end_date=end_date,
            scenic_spots=scenic_spots,
            constraints=constraints,
            user_preferences=plan_request.preferences
        )
        
        # 保存到数据库
        travel_plan = TravelPlan(
            user_id=current_user.id,
            title=f"{plan_request.destination}旅游路线",
            destination=plan_request.destination,
            start_date=start_date,
            end_date=end_date,
            budget=plan_request.budget,
            travel_type=plan_request.travel_type,
            preferences=plan_request.preferences
        )
        
        db.add(travel_plan)
        db.commit()
        db.refresh(travel_plan)
        
        # 缓存结果
        await cache_manager.set_route_plan_cache(
            destination=plan_request.destination,
            start_date=plan_request.start_date,
            end_date=plan_request.end_date,
            plan_data=route_plan,
            budget=plan_request.budget,
            travel_type=plan_request.travel_type,
            preferences=plan_request.preferences
        )
        
        return RoutePlanResponse(
            plan_id=travel_plan.id,
            **route_plan
        )
        
    except Exception as e:
        logger.error(f"路线规划失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"路线规划失败: {str(e)}"
        )

@router.post("/route/optimize")
async def optimize_route(
    plan_id: int,
    feedback: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """优化现有路线"""
    
    # 获取现有路线规划
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user.id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="路线规划不存在"
        )
    
    try:
        # 使用AI优化路线
        optimized_plan = await ai_manager.optimize_route(
            current_plan={
                "destination": travel_plan.destination,
                "start_date": travel_plan.start_date.isoformat(),
                "end_date": travel_plan.end_date.isoformat(),
                "budget": travel_plan.budget,
                "travel_type": travel_plan.travel_type,
                "preferences": travel_plan.preferences
            },
            feedback=feedback
        )
        
        return optimized_plan
        
    except Exception as e:
        logger.error(f"路线优化失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"路线优化失败: {str(e)}"
        )

# 对话相关路由
@router.post("/chat", response_model=ConversationResponse)
async def chat_with_ai(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """与AI进行对话"""
    
    try:
        # 获取对话历史
        conversation_history = await cache_manager.get_conversation_cache(
            session_id=conversation.session_id,
            user_id=current_user.id
        ) or []
        
        # 获取上下文信息
        context = None
        if conversation.plan_id:
            travel_plan = db.query(TravelPlan).filter(
                TravelPlan.id == conversation.plan_id,
                TravelPlan.user_id == current_user.id
            ).first()
            if travel_plan:
                context = {
                    "plan_id": travel_plan.id,
                    "destination": travel_plan.destination,
                    "travel_type": travel_plan.travel_type
                }
        
        # 生成AI回复
        ai_response = await ai_manager.chat_with_user(
            user_message=conversation.content,
            conversation_history=conversation_history,
            context=context
        )
        
        # 保存用户消息
        user_message = Conversation(
            user_id=current_user.id,
            plan_id=conversation.plan_id,
            session_id=conversation.session_id,
            message_type="user",
            content=conversation.content,
            metadata=conversation.metadata
        )
        db.add(user_message)
        
        # 保存AI回复
        ai_message = Conversation(
            user_id=current_user.id,
            plan_id=conversation.plan_id,
            session_id=conversation.session_id,
            message_type="assistant",
            content=ai_response
        )
        db.add(ai_message)
        
        db.commit()
        db.refresh(ai_message)
        
        # 更新对话缓存
        conversation_history.extend([
            {"role": "user", "content": conversation.content},
            {"role": "assistant", "content": ai_response}
        ])
        await cache_manager.set_conversation_cache(
            session_id=conversation.session_id,
            conversation_data=conversation_history,
            user_id=current_user.id
        )
        
        return ai_message
        
    except Exception as e:
        logger.error(f"对话生成失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话生成失败: {str(e)}"
        )

@router.get("/chat/history/{session_id}")
async def get_conversation_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    
    conversations = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at).all()
    
    return conversations

# 用户路线管理
@router.get("/plans", response_model=List[TravelPlanResponse])
async def get_user_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的路线规划列表"""
    
    plans = db.query(TravelPlan).filter(
        TravelPlan.user_id == current_user.id
    ).order_by(TravelPlan.created_at.desc()).all()
    
    return plans

@router.get("/plans/{plan_id}", response_model=TravelPlanResponse)
async def get_plan_detail(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取路线规划详情"""
    
    plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="路线规划不存在"
        )
    
    return plan

@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除路线规划"""
    
    plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="路线规划不存在"
        )
    
    db.delete(plan)
    db.commit()
    
    return {"message": "路线规划已删除"}

# 景点相关路由
@router.get("/scenic-spots")
async def get_scenic_spots(
    destination: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取景点列表"""
    
    # 检查缓存
    cached_spots = await cache_manager.get_scenic_spots_cache(
        destination=destination,
        category=category
    )
    
    if cached_spots:
        return cached_spots
    
    # 从数据库查询
    query = db.query(ScenicSpot).filter(ScenicSpot.is_active == True)
    
    if category:
        query = query.filter(ScenicSpot.category == category)
    
    spots = query.all()
    
    # 缓存结果
    spots_data = [
        {
            "id": spot.id,
            "name": spot.name,
            "description": spot.description,
            "location": spot.location,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "category": spot.category,
            "opening_hours": spot.opening_hours,
            "ticket_price": spot.ticket_price,
            "rating": spot.rating,
            "image_url": spot.image_url
        }
        for spot in spots
    ]
    
    await cache_manager.set_scenic_spots_cache(
        destination=destination,
        spots_data=spots_data,
        category=category
    )
    
    return spots_data

# 系统状态路由
@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    
    cache_stats = await cache_manager.get_cache_stats()
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "cache": cache_stats,
        "ai_model": ai_manager.current_model
    }

# 辅助函数
async def get_scenic_spots_for_destination(destination: str, db: Session) -> List:
    """获取目的地的景点数据"""
    
    # 这里应该根据目的地查询景点
    # 简化处理：返回示例数据
    from backend.route_planner import ScenicSpot
    
    sample_spots = [
        ScenicSpot(
            id=1,
            name=f"{destination}著名景点1",
            latitude=39.9042,
            longitude=116.4074,
            category="人文景观",
            rating=4.5,
            duration_hours=2.0,
            opening_hours="09:00-17:00",
            ticket_price=50.0,
            description="这是一个著名的旅游景点"
        ),
        ScenicSpot(
            id=2,
            name=f"{destination}著名景点2",
            latitude=39.9142,
            longitude=116.4174,
            category="自然风光",
            rating=4.2,
            duration_hours=3.0,
            opening_hours="08:00-18:00",
            ticket_price=80.0,
            description="这是一个美丽的自然景点"
        )
    ]
    
    return sample_spots


# 评论相关路由
@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建评论"""
    
    # 验证旅游计划是否存在
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == comment_data.plan_id,
        TravelPlan.user_id == current_user.id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅游计划不存在"
        )
    
    # 如果指定了父评论，验证父评论是否存在
    if comment_data.parent_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == comment_data.parent_id,
            Comment.plan_id == comment_data.plan_id,
            Comment.is_deleted == False
        ).first()
        
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )
    
    # 创建评论
    comment = Comment(
        user_id=current_user.id,
        plan_id=comment_data.plan_id,
        parent_id=comment_data.parent_id,
        content=comment_data.content
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # 返回评论信息
    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        plan_id=comment.plan_id,
        parent_id=comment.parent_id,
        content=comment.content,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        like_count=0,
        is_liked=False,
        user=UserResponse.from_orm(current_user),
        replies=[]
    )


@router.get("/comments/plan/{plan_id}", response_model=List[CommentResponse])
async def get_plan_comments(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取旅游计划的评论列表（包含多级回复）"""
    
    # 验证旅游计划是否存在
    travel_plan = db.query(TravelPlan).filter(
        TravelPlan.id == plan_id,
        TravelPlan.user_id == current_user.id
    ).first()
    
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅游计划不存在"
        )
    
    # 获取所有评论
    comments = db.query(Comment).filter(
        Comment.plan_id == plan_id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at).all()
    
    # 构建评论树
    comment_dict = {}
    root_comments = []
    
    for comment in comments:
        # 获取点赞数
        like_count = db.query(CommentLike).filter(
            CommentLike.comment_id == comment.id
        ).count()
        
        # 检查当前用户是否点赞
        is_liked = db.query(CommentLike).filter(
            CommentLike.comment_id == comment.id,
            CommentLike.user_id == current_user.id
        ).first() is not None
        
        # 获取用户信息
        user = db.query(User).filter(User.id == comment.user_id).first()
        
        comment_response = CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            plan_id=comment.plan_id,
            parent_id=comment.parent_id,
            content=comment.content,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            like_count=like_count,
            is_liked=is_liked,
            user=UserResponse.from_orm(user) if user else None,
            replies=[]
        )
        
        comment_dict[comment.id] = comment_response
        
        if comment.parent_id is None:
            root_comments.append(comment_response)
        else:
            if comment.parent_id in comment_dict:
                comment_dict[comment.parent_id].replies.append(comment_response)
    
    return root_comments


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新评论"""
    
    # 获取评论
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权限修改"
        )
    
    # 更新评论内容
    comment.content = comment_data.content
    comment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(comment)
    
    # 获取点赞数
    like_count = db.query(CommentLike).filter(
        CommentLike.comment_id == comment.id
    ).count()
    
    # 检查当前用户是否点赞
    is_liked = db.query(CommentLike).filter(
        CommentLike.comment_id == comment.id,
        CommentLike.user_id == current_user.id
    ).first() is not None
    
    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        plan_id=comment.plan_id,
        parent_id=comment.parent_id,
        content=comment.content,
        is_deleted=comment.is_deleted,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        like_count=like_count,
        is_liked=is_liked,
        user=UserResponse.from_orm(current_user),
        replies=[]
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除评论（软删除）"""
    
    # 获取评论
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == current_user.id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或无权限删除"
        )
    
    # 软删除评论
    comment.is_deleted = True
    comment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "评论已删除"}


@router.post("/comments/{comment_id}/like", response_model=CommentLikeResponse)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞评论"""
    
    # 验证评论是否存在
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查是否已经点赞
    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经点赞过此评论"
        )
    
    # 创建点赞记录
    like = CommentLike(
        user_id=current_user.id,
        comment_id=comment_id
    )
    
    db.add(like)
    db.commit()
    db.refresh(like)
    
    return CommentLikeResponse.from_orm(like)


@router.delete("/comments/{comment_id}/like")
async def unlike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消点赞评论"""
    
    # 查找点赞记录
    like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到点赞记录"
        )
    
    # 删除点赞记录
    db.delete(like)
    db.commit()
    
    return {"message": "已取消点赞"}


@router.get("/comments/{comment_id}/likes")
async def get_comment_likes(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取评论的点赞列表"""
    
    # 验证评论是否存在
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.is_deleted == False
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 获取点赞记录
    likes = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id
    ).order_by(CommentLike.created_at.desc()).all()
    
    # 获取用户信息
    like_responses = []
    for like in likes:
        user = db.query(User).filter(User.id == like.user_id).first()
        like_responses.append({
            "id": like.id,
            "user": UserResponse.from_orm(user) if user else None,
            "created_at": like.created_at
        })
    
    return {
        "comment_id": comment_id,
        "total_likes": len(like_responses),
        "likes": like_responses
    }