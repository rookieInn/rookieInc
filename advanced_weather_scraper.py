#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级天气爬取和分析系统
支持真实天气API和更精确的地理位置计算
"""

import requests
import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
import os

@dataclass
class WeatherInfo:
    """天气信息数据类"""
    city: str
    date: str
    weather: str
    temperature: str
    latitude: float
    longitude: float
    humidity: str = ""
    wind_speed: str = ""
    description: str = ""

class AdvancedWeatherScraper:
    """高级天气爬取器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 扩展的中国城市坐标数据
        self.city_coordinates = {
            '北京': (39.9042, 116.4074),
            '上海': (31.2304, 121.4737),
            '广州': (23.1291, 113.2644),
            '深圳': (22.5431, 113.0579),
            '杭州': (30.2741, 120.1551),
            '南京': (32.0603, 118.7969),
            '苏州': (31.2989, 120.5853),
            '成都': (30.5728, 104.0668),
            '重庆': (29.4316, 106.9123),
            '武汉': (30.5928, 114.3055),
            '西安': (34.3416, 108.9398),
            '天津': (39.3434, 117.3616),
            '青岛': (36.0986, 120.3719),
            '大连': (38.9140, 121.6147),
            '厦门': (24.4798, 118.0819),
            '福州': (26.0745, 119.2965),
            '济南': (36.6512, 117.1201),
            '郑州': (34.7466, 113.6254),
            '长沙': (28.2278, 112.9388),
            '南昌': (28.6820, 115.8579),
            '合肥': (31.8206, 117.2272),
            '石家庄': (38.0428, 114.5149),
            '太原': (37.8706, 112.5489),
            '呼和浩特': (40.8414, 111.7519),
            '沈阳': (41.8057, 123.4315),
            '长春': (43.8171, 125.3235),
            '哈尔滨': (45.7732, 126.6577),
            '昆明': (25.0389, 102.7183),
            '贵阳': (26.6470, 106.6302),
            '南宁': (22.8170, 108.3669),
            '海口': (20.0444, 110.1999),
            '兰州': (36.0611, 103.8343),
            '西宁': (36.6232, 101.7781),
            '银川': (38.4872, 106.2309),
            '乌鲁木齐': (43.8256, 87.6168),
            '拉萨': (29.6520, 91.1721),
            # 添加更多城市
            '无锡': (31.4912, 120.3124),
            '宁波': (29.8683, 121.5440),
            '温州': (28.0006, 120.6994),
            '嘉兴': (30.7462, 120.7555),
            '湖州': (30.8703, 120.1033),
            '绍兴': (30.0024, 120.5820),
            '金华': (29.1078, 119.6495),
            '衢州': (28.9569, 118.8721),
            '舟山': (30.0360, 122.2074),
            '台州': (28.6564, 121.4206),
            '丽水': (28.4514, 119.9229),
            '徐州': (34.2619, 117.2008),
            '常州': (31.8114, 119.9739),
            '南通': (32.0103, 120.8646),
            '连云港': (34.5965, 119.1788),
            '淮安': (33.6104, 119.0151),
            '盐城': (33.3776, 120.1636),
            '扬州': (32.3932, 119.4213),
            '镇江': (32.2044, 119.4528),
            '泰州': (32.4846, 119.9252),
            '宿迁': (33.9630, 118.2752)
        }
    
    def get_real_weather_data(self, city: str, days: int = 7) -> List[WeatherInfo]:
        """
        使用真实API获取天气数据
        
        Args:
            city: 城市名称
            days: 获取天数，默认7天
            
        Returns:
            天气信息列表
        """
        if city not in self.city_coordinates:
            raise ValueError(f"不支持的城市: {city}")
        
        lat, lon = self.city_coordinates[city]
        
        if not self.api_key:
            print("警告: 未提供OpenWeatherMap API key，使用模拟数据")
            return self._get_mock_weather_data(city, lat, lon, days)
        
        try:
            # 使用OpenWeatherMap API获取天气数据
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            weather_data = []
            
            # 解析API返回的数据
            for item in data['list'][:days]:
                date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                weather = item['weather'][0]['main']
                description = item['weather'][0]['description']
                temp = f"{item['main']['temp']:.1f}°C"
                humidity = f"{item['main']['humidity']}%"
                wind_speed = f"{item['wind']['speed']} m/s"
                
                weather_info = WeatherInfo(
                    city=city,
                    date=date,
                    weather=weather,
                    temperature=temp,
                    latitude=lat,
                    longitude=lon,
                    humidity=humidity,
                    wind_speed=wind_speed,
                    description=description
                )
                weather_data.append(weather_info)
            
            return weather_data
            
        except Exception as e:
            print(f"获取真实天气数据失败: {e}，使用模拟数据")
            return self._get_mock_weather_data(city, lat, lon, days)
    
    def _get_mock_weather_data(self, city: str, lat: float, lon: float, days: int) -> List[WeatherInfo]:
        """生成更真实的模拟天气数据"""
        import random
        
        # 根据地理位置调整天气概率
        weather_probabilities = self._get_weather_probabilities(lat, lon)
        
        weather_data = []
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 根据概率选择天气
            rand = random.random()
            cumulative = 0
            weather = "晴天"
            
            for w, prob in weather_probabilities.items():
                cumulative += prob
                if rand <= cumulative:
                    weather = w
                    break
            
            temp = self._generate_temperature(lat, lon, i)
            humidity = f"{random.randint(30, 90)}%"
            wind_speed = f"{random.uniform(1, 8):.1f} m/s"
            
            weather_info = WeatherInfo(
                city=city,
                date=date,
                weather=weather,
                temperature=temp,
                latitude=lat,
                longitude=lon,
                humidity=humidity,
                wind_speed=wind_speed,
                description=f"{weather}天气"
            )
            weather_data.append(weather_info)
        
        return weather_data
    
    def _get_weather_probabilities(self, lat: float, lon: float) -> Dict[str, float]:
        """根据地理位置获取天气概率"""
        # 南方城市更容易下雨
        if lat < 30:
            return {
                '晴天': 0.4,
                '多云': 0.3,
                '小雨': 0.2,
                '中雨': 0.08,
                '大雨': 0.02
            }
        # 北方城市
        elif lat > 40:
            return {
                '晴天': 0.5,
                '多云': 0.3,
                '小雨': 0.15,
                '中雨': 0.04,
                '雪': 0.01
            }
        # 中部城市
        else:
            return {
                '晴天': 0.45,
                '多云': 0.3,
                '小雨': 0.18,
                '中雨': 0.06,
                '大雨': 0.01
            }
    
    def _generate_temperature(self, lat: float, lon: float, day_offset: int) -> str:
        """根据地理位置和日期生成温度"""
        import random
        
        # 基础温度根据纬度调整
        base_temp = 25 - (lat - 30) * 0.5
        
        # 添加随机变化
        variation = random.uniform(-5, 5)
        temp = base_temp + variation + day_offset * 0.5
        
        return f"{temp:.1f}°C"
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两个坐标点之间的距离（公里）"""
        R = 6371  # 地球半径（公里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def find_nearest_sunny_city(self, rainy_city: str, target_date: str, 
                               max_distance: float = 500) -> Optional[Tuple[str, float, WeatherInfo]]:
        """
        找到离下雨城市最近的晴天城市
        
        Args:
            rainy_city: 下雨的城市
            target_date: 目标日期
            max_distance: 最大搜索距离（公里）
            
        Returns:
            (最近晴天城市名, 距离, 天气信息) 或 None
        """
        # 获取下雨城市的天气数据
        rainy_weather_data = self.get_real_weather_data(rainy_city, 7)
        rainy_city_info = None
        
        # 找到目标日期的天气信息
        for weather_info in rainy_weather_data:
            if weather_info.date == target_date:
                rainy_city_info = weather_info
                break
        
        if not rainy_city_info:
            print(f"未找到 {rainy_city} 在 {target_date} 的天气数据")
            return None
        
        # 检查是否真的下雨
        if not self._is_rainy_weather(rainy_city_info.weather):
            print(f"{rainy_city} 在 {target_date} 不是雨天")
            return None
        
        print(f"{rainy_city} 在 {target_date} 的天气: {rainy_city_info.weather} ({rainy_city_info.description})")
        
        # 遍历所有城市，找到最近的晴天城市
        nearest_sunny_city = None
        min_distance = float('inf')
        
        for city in self.city_coordinates:
            if city == rainy_city:
                continue
                
            # 先检查距离是否在合理范围内
            city_lat, city_lon = self.city_coordinates[city]
            distance = self.calculate_distance(
                rainy_city_info.latitude, rainy_city_info.longitude,
                city_lat, city_lon
            )
            
            if distance > max_distance:
                continue
                
            # 获取该城市的天气数据
            city_weather_data = self.get_real_weather_data(city, 7)
            
            # 找到目标日期的天气信息
            for weather_info in city_weather_data:
                if weather_info.date == target_date and self._is_sunny_weather(weather_info.weather):
                    if distance < min_distance:
                        min_distance = distance
                        nearest_sunny_city = (city, distance, weather_info)
                    break
        
        return nearest_sunny_city
    
    def _is_rainy_weather(self, weather: str) -> bool:
        """判断是否为雨天"""
        rainy_keywords = ['Rain', 'Drizzle', 'Thunderstorm', 'Snow', '雨', '雷', '雪']
        return any(keyword in weather for keyword in rainy_keywords)
    
    def _is_sunny_weather(self, weather: str) -> bool:
        """判断是否为晴天"""
        sunny_keywords = ['Clear', 'Sunny', '晴', '多云']
        return any(keyword in weather for keyword in sunny_keywords)
    
    def get_weather_recommendations(self, cities: List[str], days: int = 7) -> Dict:
        """
        获取天气推荐结果
        
        Args:
            cities: 要分析的城市列表
            days: 分析天数
            
        Returns:
            推荐结果字典
        """
        results = {
            'analysis_period': f"{datetime.now().strftime('%Y-%m-%d')} 到 {(datetime.now() + timedelta(days=days-1)).strftime('%Y-%m-%d')}",
            'rainy_days': {},
            'recommendations': []
        }
        
        print(f"正在分析 {len(cities)} 个城市未来 {days} 天的天气...")
        
        # 收集所有城市的天气数据
        all_weather_data = {}
        for i, city in enumerate(cities):
            print(f"获取 {city} 的天气数据... ({i+1}/{len(cities)})")
            all_weather_data[city] = self.get_real_weather_data(city, days)
            time.sleep(0.5)  # 避免API限制
        
        # 按日期分析天气模式
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            rainy_cities = []
            
            for city, weather_data in all_weather_data.items():
                if i < len(weather_data):
                    weather_info = weather_data[i]
                    if self._is_rainy_weather(weather_info.weather):
                        rainy_cities.append(city)
            
            results['rainy_days'][date] = rainy_cities
            
            # 为每个下雨城市找到最近的晴天城市
            for rainy_city in rainy_cities:
                print(f"为 {rainy_city} 寻找最近的晴天城市...")
                nearest_sunny = self.find_nearest_sunny_city(rainy_city, date)
                if nearest_sunny:
                    results['recommendations'].append({
                        'date': date,
                        'rainy_city': rainy_city,
                        'nearest_sunny_city': nearest_sunny[0],
                        'distance': nearest_sunny[1],
                        'weather_info': nearest_sunny[2]
                    })
        
        return results
    
    def print_recommendations(self, results: Dict):
        """打印推荐结果"""
        print("\n" + "="*60)
        print("天气推荐结果")
        print("="*60)
        print(f"分析期间: {results['analysis_period']}")
        
        if not results['recommendations']:
            print("在分析期间内，没有城市下雨，无需推荐。")
            return
        
        print(f"\n找到 {len(results['recommendations'])} 个推荐:")
        print("-" * 60)
        
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec['date']}")
            print(f"   下雨城市: {rec['rainy_city']}")
            print(f"   推荐城市: {rec['nearest_sunny_city']}")
            print(f"   距离: {rec['distance']:.2f} 公里")
            print(f"   天气: {rec['weather_info'].weather} ({rec['weather_info'].description})")
            print(f"   温度: {rec['weather_info'].temperature}")
            print(f"   湿度: {rec['weather_info'].humidity}")
            print(f"   风速: {rec['weather_info'].wind_speed}")
            print()

def main():
    """主函数 - 使用示例"""
    print("=== 高级天气爬取和分析系统 ===\n")
    
    # 创建爬取器实例
    scraper = AdvancedWeatherScraper()
    
    # 示例1: 查找特定城市在特定日期的最近晴天城市
    print("示例1: 查找北京在明天最近的晴天城市")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    result = scraper.find_nearest_sunny_city('北京', tomorrow)
    
    if result:
        city, distance, weather_info = result
        print(f"推荐城市: {city}")
        print(f"距离: {distance:.2f} 公里")
        print(f"天气: {weather_info.weather} ({weather_info.description})")
        print(f"温度: {weather_info.temperature}")
    else:
        print("未找到合适的晴天城市")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 分析多个城市的天气模式
    print("示例2: 分析多个城市的天气模式")
    cities_to_analyze = ['北京', '上海', '广州', '深圳', '杭州', '南京', '苏州']
    results = scraper.get_weather_recommendations(cities_to_analyze, 3)
    scraper.print_recommendations(results)

if __name__ == "__main__":
    main()