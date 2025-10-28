#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气爬取和分析系统
功能：
1. 爬取城市未来几天的天气状况
2. 找到下雨城市附近最近的晴天城市
"""

import requests
import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

@dataclass
class WeatherInfo:
    """天气信息数据类"""
    city: str
    date: str
    weather: str
    temperature: str
    latitude: float
    longitude: float

class WeatherScraper:
    """天气爬取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 中国主要城市坐标数据
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
            '拉萨': (29.6520, 91.1721)
        }
    
    def get_weather_data(self, city: str, days: int = 7) -> List[WeatherInfo]:
        """
        获取指定城市未来几天的天气数据
        
        Args:
            city: 城市名称
            days: 获取天数，默认7天
            
        Returns:
            天气信息列表
        """
        if city not in self.city_coordinates:
            raise ValueError(f"不支持的城市: {city}")
        
        lat, lon = self.city_coordinates[city]
        weather_data = []
        
        try:
            # 使用OpenWeatherMap API (需要API key，这里使用模拟数据)
            # 实际使用时需要注册OpenWeatherMap获取API key
            weather_data = self._get_mock_weather_data(city, lat, lon, days)
            
        except Exception as e:
            print(f"获取天气数据失败: {e}")
            # 使用模拟数据作为备选
            weather_data = self._get_mock_weather_data(city, lat, lon, days)
        
        return weather_data
    
    def _get_mock_weather_data(self, city: str, lat: float, lon: float, days: int) -> List[WeatherInfo]:
        """生成模拟天气数据"""
        import random
        
        weather_conditions = ['晴天', '多云', '阴天', '小雨', '中雨', '大雨', '雷阵雨', '雪']
        weather_data = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            weather = random.choice(weather_conditions)
            temp = f"{random.randint(15, 30)}°C"
            
            weather_info = WeatherInfo(
                city=city,
                date=date,
                weather=weather,
                temperature=temp,
                latitude=lat,
                longitude=lon
            )
            weather_data.append(weather_info)
        
        return weather_data
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        计算两个坐标点之间的距离（公里）
        使用Haversine公式
        """
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
    
    def find_nearest_sunny_city(self, rainy_city: str, target_date: str) -> Optional[Tuple[str, float, WeatherInfo]]:
        """
        找到离下雨城市最近的晴天城市
        
        Args:
            rainy_city: 下雨的城市
            target_date: 目标日期
            
        Returns:
            (最近晴天城市名, 距离, 天气信息) 或 None
        """
        # 获取下雨城市的天气数据
        rainy_weather_data = self.get_weather_data(rainy_city, 7)
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
        
        print(f"{rainy_city} 在 {target_date} 的天气: {rainy_city_info.weather}")
        
        # 遍历所有城市，找到最近的晴天城市
        nearest_sunny_city = None
        min_distance = float('inf')
        
        for city in self.city_coordinates:
            if city == rainy_city:
                continue
                
            # 获取该城市的天气数据
            city_weather_data = self.get_weather_data(city, 7)
            
            # 找到目标日期的天气信息
            for weather_info in city_weather_data:
                if weather_info.date == target_date and self._is_sunny_weather(weather_info.weather):
                    # 计算距离
                    distance = self.calculate_distance(
                        rainy_city_info.latitude, rainy_city_info.longitude,
                        weather_info.latitude, weather_info.longitude
                    )
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_sunny_city = (city, distance, weather_info)
                    break
        
        return nearest_sunny_city
    
    def _is_rainy_weather(self, weather: str) -> bool:
        """判断是否为雨天"""
        rainy_keywords = ['雨', '雷', '雪']
        return any(keyword in weather for keyword in rainy_keywords)
    
    def _is_sunny_weather(self, weather: str) -> bool:
        """判断是否为晴天"""
        sunny_keywords = ['晴', '多云']
        return any(keyword in weather for keyword in sunny_keywords)
    
    def analyze_weather_patterns(self, cities: List[str], days: int = 7) -> Dict:
        """
        分析多个城市的天气模式
        
        Args:
            cities: 城市列表
            days: 分析天数
            
        Returns:
            分析结果字典
        """
        results = {
            'rainy_days': {},  # 下雨日期和城市
            'sunny_days': {},  # 晴天日期和城市
            'recommendations': []  # 推荐结果
        }
        
        # 收集所有城市的天气数据
        all_weather_data = {}
        for city in cities:
            all_weather_data[city] = self.get_weather_data(city, days)
        
        # 按日期分析天气模式
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            rainy_cities = []
            sunny_cities = []
            
            for city, weather_data in all_weather_data.items():
                if i < len(weather_data):
                    weather_info = weather_data[i]
                    if self._is_rainy_weather(weather_info.weather):
                        rainy_cities.append(city)
                    elif self._is_sunny_weather(weather_info.weather):
                        sunny_cities.append(city)
            
            results['rainy_days'][date] = rainy_cities
            results['sunny_days'][date] = sunny_cities
            
            # 为每个下雨城市找到最近的晴天城市
            for rainy_city in rainy_cities:
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

def main():
    """主函数 - 使用示例"""
    scraper = WeatherScraper()
    
    print("=== 天气爬取和分析系统 ===\n")
    
    # 示例1: 查找特定城市在特定日期的最近晴天城市
    print("示例1: 查找北京在明天最近的晴天城市")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    result = scraper.find_nearest_sunny_city('北京', tomorrow)
    
    if result:
        city, distance, weather_info = result
        print(f"推荐城市: {city}")
        print(f"距离: {distance:.2f} 公里")
        print(f"天气: {weather_info.weather}, 温度: {weather_info.temperature}")
    else:
        print("未找到合适的晴天城市")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 分析多个城市的天气模式
    print("示例2: 分析多个城市的天气模式")
    cities_to_analyze = ['北京', '上海', '广州', '深圳', '杭州']
    analysis = scraper.analyze_weather_patterns(cities_to_analyze, 3)
    
    print("分析结果:")
    for date, rainy_cities in analysis['rainy_days'].items():
        if rainy_cities:
            print(f"\n{date}:")
            print(f"  下雨城市: {', '.join(rainy_cities)}")
            print(f"  晴天城市: {', '.join(analysis['sunny_days'][date])}")
    
    print("\n推荐结果:")
    for rec in analysis['recommendations']:
        print(f"{rec['date']}: {rec['rainy_city']} -> {rec['nearest_sunny_city']} "
              f"(距离: {rec['distance']:.2f}km, 天气: {rec['weather_info'].weather})")

if __name__ == "__main__":
    main()