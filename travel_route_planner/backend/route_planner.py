"""
旅游路线规划核心算法
"""
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScenicSpot:
    """景点数据类"""
    id: int
    name: str
    latitude: float
    longitude: float
    category: str
    rating: float
    duration_hours: float
    opening_hours: str
    ticket_price: float
    description: str


@dataclass
class RouteConstraint:
    """路线约束条件"""
    max_daily_spots: int = 3
    max_daily_hours: float = 10.0
    min_spot_duration: float = 1.0
    max_travel_distance: float = 50.0  # 公里
    budget_limit: Optional[float] = None
    preferred_categories: Optional[List[str]] = None


class RoutePlanner:
    """路线规划器"""
    
    def __init__(self):
        self.constraints = RouteConstraint()
    
    async def plan_route(
        self,
        destination: str,
        start_date: datetime,
        end_date: datetime,
        scenic_spots: List[ScenicSpot],
        constraints: Optional[RouteConstraint] = None,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """生成旅游路线规划"""
        
        if constraints:
            self.constraints = constraints
        
        # 计算旅行天数
        travel_days = (end_date - start_date).days + 1
        
        # 过滤和排序景点
        filtered_spots = self._filter_spots(scenic_spots, user_preferences)
        sorted_spots = self._sort_spots_by_rating(filtered_spots)
        
        # 生成每日行程
        daily_plans = []
        remaining_spots = sorted_spots.copy()
        
        for day in range(travel_days):
            current_date = start_date + timedelta(days=day)
            day_plan = await self._plan_single_day(
                current_date, remaining_spots, day == 0
            )
            daily_plans.append(day_plan)
            
            # 移除已安排的景点
            for spot in day_plan['spots']:
                remaining_spots = [s for s in remaining_spots if s.id != spot['id']]
        
        # 计算总费用
        total_cost = self._calculate_total_cost(daily_plans)
        
        # 生成路线地图数据
        map_data = self._generate_map_data(daily_plans)
        
        return {
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "travel_days": travel_days,
            "daily_plans": daily_plans,
            "total_cost": total_cost,
            "map_data": map_data,
            "constraints": self.constraints.__dict__,
            "generated_at": datetime.now().isoformat()
        }
    
    def _filter_spots(
        self, 
        spots: List[ScenicSpot], 
        preferences: Optional[Dict]
    ) -> List[ScenicSpot]:
        """根据用户偏好过滤景点"""
        
        filtered = spots.copy()
        
        if preferences:
            # 按类别过滤
            if 'categories' in preferences:
                preferred_categories = preferences['categories']
                filtered = [s for s in filtered if s.category in preferred_categories]
            
            # 按评分过滤
            if 'min_rating' in preferences:
                min_rating = preferences['min_rating']
                filtered = [s for s in filtered if s.rating >= min_rating]
            
            # 按价格过滤
            if 'max_price' in preferences:
                max_price = preferences['max_price']
                filtered = [s for s in filtered if s.ticket_price <= max_price]
        
        return filtered
    
    def _sort_spots_by_rating(self, spots: List[ScenicSpot]) -> List[ScenicSpot]:
        """按评分排序景点"""
        return sorted(spots, key=lambda x: x.rating, reverse=True)
    
    async def _plan_single_day(
        self, 
        date: datetime, 
        available_spots: List[ScenicSpot],
        is_first_day: bool = False
    ) -> Dict[str, Any]:
        """规划单日行程"""
        
        day_spots = []
        current_time = 9.0  # 上午9点开始
        total_duration = 0.0
        
        # 如果是第一天，可能需要考虑到达时间
        if is_first_day:
            current_time = 10.0  # 第一天10点开始
        
        for spot in available_spots:
            # 检查是否超过每日景点数量限制
            if len(day_spots) >= self.constraints.max_daily_spots:
                break
            
            # 检查是否超过每日时间限制
            if total_duration + spot.duration_hours > self.constraints.max_daily_hours:
                break
            
            # 检查开放时间
            if not self._is_spot_open(spot, date, current_time):
                continue
            
            # 计算到达时间（简化处理）
            travel_time = self._calculate_travel_time(day_spots, spot)
            arrival_time = current_time + travel_time
            
            # 检查是否在开放时间内到达
            if not self._is_spot_open(spot, date, arrival_time):
                continue
            
            # 添加景点到当日行程
            spot_plan = {
                "id": spot.id,
                "name": spot.name,
                "category": spot.category,
                "arrival_time": f"{int(arrival_time):02d}:{int((arrival_time % 1) * 60):02d}",
                "duration_hours": spot.duration_hours,
                "departure_time": f"{int(arrival_time + spot.duration_hours):02d}:{int(((arrival_time + spot.duration_hours) % 1) * 60):02d}",
                "ticket_price": spot.ticket_price,
                "rating": spot.rating,
                "description": spot.description,
                "latitude": spot.latitude,
                "longitude": spot.longitude
            }
            
            day_spots.append(spot_plan)
            current_time = arrival_time + spot.duration_hours
            total_duration += spot.duration_hours
        
        # 生成当日总结
        day_summary = {
            "date": date.strftime("%Y-%m-%d"),
            "spots": day_spots,
            "total_spots": len(day_spots),
            "total_duration": total_duration,
            "total_cost": sum(spot['ticket_price'] for spot in day_spots),
            "recommendations": self._generate_day_recommendations(day_spots, date)
        }
        
        return day_summary
    
    def _is_spot_open(self, spot: ScenicSpot, date: datetime, time: float) -> bool:
        """检查景点是否在指定时间开放"""
        # 简化处理：假设所有景点都开放
        # 实际应用中应该解析opening_hours字段
        return True
    
    def _calculate_travel_time(
        self, 
        previous_spots: List[Dict], 
        next_spot: ScenicSpot
    ) -> float:
        """计算景点间旅行时间（小时）"""
        
        if not previous_spots:
            return 0.5  # 从酒店出发，假设30分钟
        
        last_spot = previous_spots[-1]
        distance = geodesic(
            (last_spot['latitude'], last_spot['longitude']),
            (next_spot.latitude, next_spot.longitude)
        ).kilometers
        
        # 假设平均速度30km/h
        travel_time = distance / 30.0
        return min(travel_time, 2.0)  # 最多2小时
    
    def _generate_day_recommendations(
        self, 
        spots: List[Dict], 
        date: datetime
    ) -> List[str]:
        """生成当日建议"""
        
        recommendations = []
        
        # 天气建议
        recommendations.append("建议关注当日天气预报，合理安排着装")
        
        # 交通建议
        if len(spots) > 1:
            recommendations.append("景点间建议使用公共交通或打车，注意交通拥堵时间")
        
        # 餐饮建议
        recommendations.append("建议提前了解景点附近的美食推荐")
        
        # 安全建议
        recommendations.append("注意保管好个人物品，遵守景点规定")
        
        return recommendations
    
    def _calculate_total_cost(self, daily_plans: List[Dict]) -> Dict[str, float]:
        """计算总费用"""
        
        total_tickets = sum(day['total_cost'] for day in daily_plans)
        
        # 估算其他费用
        estimated_meals = len(daily_plans) * 100  # 每天100元餐费
        estimated_transport = len(daily_plans) * 50  # 每天50元交通费
        estimated_accommodation = (len(daily_plans) - 1) * 200  # 每晚200元住宿费
        
        return {
            "tickets": total_tickets,
            "meals": estimated_meals,
            "transport": estimated_transport,
            "accommodation": estimated_accommodation,
            "total": total_tickets + estimated_meals + estimated_transport + estimated_accommodation
        }
    
    def _generate_map_data(self, daily_plans: List[Dict]) -> Dict[str, Any]:
        """生成地图数据"""
        
        all_spots = []
        routes = []
        
        for day_idx, day_plan in enumerate(daily_plans):
            day_spots = []
            for spot in day_plan['spots']:
                spot_data = {
                    "id": spot['id'],
                    "name": spot['name'],
                    "latitude": spot['latitude'],
                    "longitude": spot['longitude'],
                    "day": day_idx + 1,
                    "arrival_time": spot['arrival_time']
                }
                all_spots.append(spot_data)
                day_spots.append(spot_data)
            
            # 生成当日路线
            if len(day_spots) > 1:
                route = {
                    "day": day_idx + 1,
                    "coordinates": [(spot['longitude'], spot['latitude']) for spot in day_spots]
                }
                routes.append(route)
        
        return {
            "spots": all_spots,
            "routes": routes,
            "center": self._calculate_map_center(all_spots) if all_spots else None
        }
    
    def _calculate_map_center(self, spots: List[Dict]) -> Tuple[float, float]:
        """计算地图中心点"""
        if not spots:
            return (0, 0)
        
        avg_lat = sum(spot['latitude'] for spot in spots) / len(spots)
        avg_lon = sum(spot['longitude'] for spot in spots) / len(spots)
        
        return (avg_lat, avg_lon)
    
    async def optimize_route(
        self,
        current_plan: Dict[str, Any],
        feedback: str,
        constraints: Optional[RouteConstraint] = None
    ) -> Dict[str, Any]:
        """优化现有路线"""
        
        if constraints:
            self.constraints = constraints
        
        # 解析反馈信息
        optimization_suggestions = self._parse_feedback(feedback)
        
        # 应用优化建议
        optimized_plan = current_plan.copy()
        
        # 这里可以添加具体的优化逻辑
        # 例如：调整景点顺序、替换景点、调整时间等
        
        return {
            "original_plan": current_plan,
            "optimized_plan": optimized_plan,
            "optimization_suggestions": optimization_suggestions,
            "optimized_at": datetime.now().isoformat()
        }
    
    def _parse_feedback(self, feedback: str) -> List[str]:
        """解析用户反馈"""
        # 简化处理：返回原始反馈
        # 实际应用中可以使用NLP技术解析反馈
        return [feedback]


# 创建全局路线规划器实例
route_planner = RoutePlanner()