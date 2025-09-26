"""
路线优化器
基于用户需求和地理信息优化旅游路线
"""

from typing import List, Dict, Tuple
import math
from app.services.gis_service import GISService

class RouteOptimizer:
    """路线优化器"""
    
    def __init__(self):
        self.gis_service = GISService()
    
    async def optimize_route(self, scenic_spots: List[Dict], hotels: List[Dict], requirements: Dict) -> Dict:
        """优化旅游路线"""
        if not scenic_spots:
            return {"error": "没有找到合适的景点"}
        
        # 根据用户偏好筛选景点
        filtered_spots = self._filter_spots_by_preferences(scenic_spots, requirements)
        
        # 根据行程天数分组景点
        daily_spots = self._group_spots_by_days(filtered_spots, requirements.get("duration_days", 3))
        
        # 优化每日路线
        optimized_daily_routes = []
        for day, spots in daily_spots.items():
            if spots:
                daily_route = await self._optimize_daily_route(spots, day)
                optimized_daily_routes.append(daily_route)
        
        # 选择最佳住宿
        best_hotel = self._select_best_hotel(hotels, requirements, scenic_spots)
        
        return {
            "daily_routes": optimized_daily_routes,
            "accommodation": best_hotel,
            "total_spots": len(filtered_spots),
            "optimization_score": self._calculate_optimization_score(optimized_daily_routes, requirements)
        }
    
    def _filter_spots_by_preferences(self, spots: List[Dict], requirements: Dict) -> List[Dict]:
        """根据用户偏好筛选景点"""
        filtered = spots.copy()
        
        # 根据兴趣筛选
        interests = requirements.get("interests", [])
        if interests:
            filtered = [
                spot for spot in filtered
                if any(interest in spot.get("category", "") for interest in interests)
            ]
        
        # 根据旅行风格筛选
        travel_style = requirements.get("travel_style", "")
        if travel_style == "亲子游":
            # 选择适合儿童的景点
            filtered = [
                spot for spot in filtered
                if spot.get("category") in ["自然风光", "主题公园", "博物馆"]
            ]
        elif travel_style == "蜜月游":
            # 选择浪漫的景点
            filtered = [
                spot for spot in filtered
                if spot.get("category") in ["自然风光", "园林景观", "现代建筑"]
            ]
        
        # 根据评分筛选（选择评分较高的景点）
        filtered.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        return filtered
    
    def _group_spots_by_days(self, spots: List[Dict], duration_days: int) -> Dict:
        """将景点按天数分组"""
        daily_spots = {i: [] for i in range(1, duration_days + 1)}
        
        # 简单分组：平均分配景点
        spots_per_day = max(1, len(spots) // duration_days)
        
        for i, spot in enumerate(spots):
            day = min(i // spots_per_day + 1, duration_days)
            daily_spots[day].append(spot)
        
        return daily_spots
    
    async def _optimize_daily_route(self, spots: List[Dict], day: int) -> Dict:
        """优化单日路线"""
        if not spots:
            return {"day": day, "spots": [], "total_distance": 0}
        
        # 使用贪心算法优化路线
        optimized_spots = []
        remaining_spots = spots.copy()
        
        # 选择第一个景点（通常是评分最高的）
        current_spot = remaining_spots.pop(0)
        optimized_spots.append(current_spot)
        
        # 贪心选择下一个最近的景点
        while remaining_spots:
            next_spot = self._find_nearest_spot(current_spot, remaining_spots)
            if next_spot:
                optimized_spots.append(next_spot)
                remaining_spots.remove(next_spot)
                current_spot = next_spot
            else:
                break
        
        # 计算总距离
        total_distance = self._calculate_route_distance(optimized_spots)
        
        return {
            "day": day,
            "spots": optimized_spots,
            "total_distance": total_distance,
            "estimated_time": self._estimate_route_time(optimized_spots)
        }
    
    def _find_nearest_spot(self, current_spot: Dict, remaining_spots: List[Dict]) -> Dict:
        """找到最近的景点"""
        if not remaining_spots:
            return None
        
        min_distance = float('inf')
        nearest_spot = None
        
        for spot in remaining_spots:
            distance = self._calculate_distance(current_spot, spot)
            if distance < min_distance:
                min_distance = distance
                nearest_spot = spot
        
        return nearest_spot
    
    def _calculate_distance(self, spot1: Dict, spot2: Dict) -> float:
        """计算两个景点间的距离"""
        lat1, lon1 = spot1.get("latitude", 0), spot1.get("longitude", 0)
        lat2, lon2 = spot2.get("latitude", 0), spot2.get("longitude", 0)
        
        # 使用欧几里得距离作为简化计算
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
    
    def _calculate_route_distance(self, spots: List[Dict]) -> float:
        """计算路线总距离"""
        if len(spots) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(spots) - 1):
            total_distance += self._calculate_distance(spots[i], spots[i + 1])
        
        return total_distance
    
    def _estimate_route_time(self, spots: List[Dict]) -> str:
        """估算路线时间"""
        if not spots:
            return "0小时"
        
        # 每个景点预计游览2-3小时，加上交通时间
        visit_time = len(spots) * 2.5  # 小时
        travel_time = self._calculate_route_distance(spots) * 0.1  # 简化计算
        
        total_time = visit_time + travel_time
        return f"{total_time:.1f}小时"
    
    def _select_best_hotel(self, hotels: List[Dict], requirements: Dict, scenic_spots: List[Dict]) -> Dict:
        """选择最佳酒店"""
        if not hotels:
            return {"name": "待定", "reason": "暂无可用酒店"}
        
        # 根据预算筛选
        budget = requirements.get("budget", "")
        filtered_hotels = hotels.copy()
        
        if "经济" in budget or "低" in budget:
            filtered_hotels = [
                hotel for hotel in filtered_hotels
                if "600" in hotel.get("price_range", "") or "800" in hotel.get("price_range", "")
            ]
        elif "豪华" in budget or "高" in budget:
            filtered_hotels = [
                hotel for hotel in filtered_hotels
                if "1200" in hotel.get("price_range", "") or "1500" in hotel.get("price_range", "")
            ]
        
        if not filtered_hotels:
            filtered_hotels = hotels
        
        # 选择评分最高的酒店
        best_hotel = max(filtered_hotels, key=lambda x: x.get("rating", 0))
        
        # 计算到景点的平均距离
        if scenic_spots:
            avg_distance = self._calculate_average_distance_to_spots(best_hotel, scenic_spots)
            best_hotel["avg_distance_to_spots"] = f"{avg_distance:.1f}公里"
        
        return best_hotel
    
    def _calculate_average_distance_to_spots(self, hotel: Dict, spots: List[Dict]) -> float:
        """计算酒店到景点的平均距离"""
        if not spots:
            return 0
        
        total_distance = 0
        for spot in spots:
            total_distance += self._calculate_distance(hotel, spot)
        
        return total_distance / len(spots)
    
    def _calculate_optimization_score(self, daily_routes: List[Dict], requirements: Dict) -> float:
        """计算路线优化评分"""
        if not daily_routes:
            return 0
        
        # 基于以下因素计算评分：
        # 1. 景点数量
        # 2. 路线效率（距离）
        # 3. 用户偏好匹配度
        
        total_spots = sum(len(route["spots"]) for route in daily_routes)
        total_distance = sum(route["total_distance"] for route in daily_routes)
        
        # 评分计算（0-100分）
        spot_score = min(total_spots * 10, 50)  # 景点数量得分
        distance_score = max(0, 30 - total_distance * 2)  # 距离效率得分
        preference_score = 20  # 偏好匹配得分（简化）
        
        return min(spot_score + distance_score + preference_score, 100)