"""
地理信息服务
提供景点、酒店、交通等地理信息查询
"""

from typing import List, Dict, Optional
import json
from app.core.cache import CacheManager
from app.core.config import settings

class GISService:
    """地理信息服务类"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        # 模拟数据，实际应用中应该从数据库或外部API获取
        self.scenic_spots_data = self._load_scenic_spots_data()
        self.hotels_data = self._load_hotels_data()
        self.transportation_data = self._load_transportation_data()
    
    def _load_scenic_spots_data(self) -> List[Dict]:
        """加载景点数据"""
        return [
            {
                "id": 1,
                "name": "故宫博物院",
                "description": "明清两朝的皇家宫殿，世界文化遗产",
                "location": "北京市东城区景山前街4号",
                "latitude": 39.9163,
                "longitude": 116.3972,
                "opening_hours": "08:30-17:00",
                "ticket_price": "60元",
                "rating": 4.8,
                "category": "历史文化",
                "city": "北京"
            },
            {
                "id": 2,
                "name": "天安门广场",
                "description": "世界上最大的城市广场",
                "location": "北京市东城区东长安街",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "opening_hours": "全天开放",
                "ticket_price": "免费",
                "rating": 4.7,
                "category": "历史文化",
                "city": "北京"
            },
            {
                "id": 3,
                "name": "颐和园",
                "description": "中国古典园林之首",
                "location": "北京市海淀区新建宫门路19号",
                "latitude": 39.9999,
                "longitude": 116.2755,
                "opening_hours": "06:30-18:00",
                "ticket_price": "30元",
                "rating": 4.6,
                "category": "园林景观",
                "city": "北京"
            },
            {
                "id": 4,
                "name": "外滩",
                "description": "上海标志性景观，万国建筑博览群",
                "location": "上海市黄浦区中山东一路",
                "latitude": 31.2397,
                "longitude": 121.4998,
                "opening_hours": "全天开放",
                "ticket_price": "免费",
                "rating": 4.5,
                "category": "现代建筑",
                "city": "上海"
            },
            {
                "id": 5,
                "name": "西湖",
                "description": "中国著名的风景名胜区",
                "location": "浙江省杭州市西湖区龙井路1号",
                "latitude": 30.2741,
                "longitude": 120.1551,
                "opening_hours": "全天开放",
                "ticket_price": "免费",
                "rating": 4.7,
                "category": "自然风光",
                "city": "杭州"
            }
        ]
    
    def _load_hotels_data(self) -> List[Dict]:
        """加载酒店数据"""
        return [
            {
                "id": 1,
                "name": "北京饭店",
                "description": "历史悠久的豪华酒店",
                "location": "北京市东城区东长安街33号",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "price_range": "800-1500元/晚",
                "rating": 4.5,
                "amenities": ["WiFi", "健身房", "餐厅", "会议室"],
                "city": "北京"
            },
            {
                "id": 2,
                "name": "上海和平饭店",
                "description": "外滩标志性建筑",
                "location": "上海市黄浦区南京东路20号",
                "latitude": 31.2397,
                "longitude": 121.4998,
                "price_range": "1200-2500元/晚",
                "rating": 4.6,
                "amenities": ["WiFi", "健身房", "餐厅", "酒吧", "SPA"],
                "city": "上海"
            },
            {
                "id": 3,
                "name": "杭州西湖国宾馆",
                "description": "西湖边的豪华度假酒店",
                "location": "浙江省杭州市西湖区杨公堤18号",
                "latitude": 30.2741,
                "longitude": 120.1551,
                "price_range": "600-1200元/晚",
                "rating": 4.4,
                "amenities": ["WiFi", "健身房", "餐厅", "游泳池"],
                "city": "杭州"
            }
        ]
    
    def _load_transportation_data(self) -> List[Dict]:
        """加载交通数据"""
        return [
            {
                "id": 1,
                "from_location": "北京首都国际机场",
                "to_location": "北京市区",
                "transport_type": "机场快轨",
                "duration": "30分钟",
                "price": "25元",
                "distance": 30.0
            },
            {
                "id": 2,
                "from_location": "上海虹桥机场",
                "to_location": "上海市区",
                "transport_type": "地铁",
                "duration": "45分钟",
                "price": "6元",
                "distance": 25.0
            }
        ]
    
    async def get_scenic_spots(self, destination: str, interests: List[str] = None) -> List[Dict]:
        """获取景点信息"""
        cache_key = f"scenic_spots:{destination}:{hash(str(interests))}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # 根据目的地筛选景点
        filtered_spots = [
            spot for spot in self.scenic_spots_data 
            if spot["city"] == destination
        ]
        
        # 根据兴趣筛选
        if interests:
            filtered_spots = [
                spot for spot in filtered_spots
                if any(interest in spot["category"] for interest in interests)
            ]
        
        # 缓存结果
        await self.cache_manager.set(cache_key, filtered_spots, ttl=3600)
        
        return filtered_spots
    
    async def get_hotels(self, destination: str, budget: str = "") -> List[Dict]:
        """获取酒店信息"""
        cache_key = f"hotels:{destination}:{budget}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # 根据目的地筛选酒店
        filtered_hotels = [
            hotel for hotel in self.hotels_data 
            if hotel["city"] == destination
        ]
        
        # 根据预算筛选（简化实现）
        if budget:
            if "经济" in budget or "低" in budget:
                filtered_hotels = [
                    hotel for hotel in filtered_hotels
                    if "600" in hotel["price_range"] or "800" in hotel["price_range"]
                ]
            elif "豪华" in budget or "高" in budget:
                filtered_hotels = [
                    hotel for hotel in filtered_hotels
                    if "1200" in hotel["price_range"] or "1500" in hotel["price_range"]
                ]
        
        # 缓存结果
        await self.cache_manager.set(cache_key, filtered_hotels, ttl=3600)
        
        return filtered_hotels
    
    async def get_transportation(self, from_location: str, to_location: str) -> List[Dict]:
        """获取交通信息"""
        cache_key = f"transportation:{from_location}:{to_location}"
        cached_data = await self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # 查找匹配的交通方式
        filtered_transport = [
            transport for transport in self.transportation_data
            if (from_location in transport["from_location"] and 
                to_location in transport["to_location"])
        ]
        
        # 缓存结果
        await self.cache_manager.set(cache_key, filtered_transport, ttl=3600)
        
        return filtered_transport
    
    async def get_weather_info(self, location: str, date: str) -> Dict:
        """获取天气信息"""
        # 模拟天气数据
        weather_data = {
            "location": location,
            "date": date,
            "temperature": "15-25°C",
            "weather": "晴转多云",
            "humidity": "60%",
            "wind": "微风",
            "recommendation": "适合户外活动，建议携带薄外套"
        }
        
        return weather_data
    
    async def calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """计算两点间距离（公里）"""
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """计算两点间距离"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # 地球半径（公里）
            return c * r
        
        return haversine(
            point1["longitude"], point1["latitude"],
            point2["longitude"], point2["latitude"]
        )