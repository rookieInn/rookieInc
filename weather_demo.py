#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气爬取系统使用示例
"""

from weather_scraper import WeatherScraper
from advanced_weather_scraper import AdvancedWeatherScraper
from datetime import datetime, timedelta

def demo_basic_scraper():
    """演示基础天气爬取器"""
    print("=== 基础天气爬取器演示 ===\n")
    
    scraper = WeatherScraper()
    
    # 查找北京明天最近的晴天城市
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"查找北京在 {tomorrow} 最近的晴天城市...")
    
    result = scraper.find_nearest_sunny_city('北京', tomorrow)
    
    if result:
        city, distance, weather_info = result
        print(f"✅ 推荐城市: {city}")
        print(f"📍 距离: {distance:.2f} 公里")
        print(f"🌤️  天气: {weather_info.weather}")
        print(f"🌡️  温度: {weather_info.temperature}")
    else:
        print("❌ 未找到合适的晴天城市")

def demo_advanced_scraper():
    """演示高级天气爬取器"""
    print("\n=== 高级天气爬取器演示 ===\n")
    
    scraper = AdvancedWeatherScraper()
    
    # 分析多个城市的天气模式
    cities = ['北京', '上海', '广州', '深圳', '杭州']
    print(f"分析城市: {', '.join(cities)}")
    print("分析天数: 3天\n")
    
    results = scraper.get_weather_recommendations(cities, 3)
    scraper.print_recommendations(results)

def interactive_demo():
    """交互式演示"""
    print("\n=== 交互式天气查询 ===\n")
    
    scraper = AdvancedWeatherScraper()
    
    # 显示支持的城市
    print("支持的城市:")
    cities = list(scraper.city_coordinates.keys())
    for i, city in enumerate(cities, 1):
        print(f"{i:2d}. {city}", end="  ")
        if i % 5 == 0:
            print()
    print("\n")
    
    # 用户输入
    try:
        city = input("请输入要查询的城市名称: ").strip()
        if city not in scraper.city_coordinates:
            print(f"❌ 不支持的城市: {city}")
            return
        
        days = int(input("请输入要查询的天数 (1-7): "))
        if not 1 <= days <= 7:
            print("❌ 天数必须在1-7之间")
            return
        
        print(f"\n正在查询 {city} 未来 {days} 天的天气...")
        
        # 获取天气数据
        weather_data = scraper.get_real_weather_data(city, days)
        
        print(f"\n{city} 未来 {days} 天天气:")
        print("-" * 40)
        for weather_info in weather_data:
            print(f"{weather_info.date}: {weather_info.weather} - {weather_info.temperature}")
        
        # 查找下雨天的替代城市
        print(f"\n查找 {city} 下雨天的替代城市...")
        for weather_info in weather_data:
            if scraper._is_rainy_weather(weather_info.weather):
                print(f"\n{weather_info.date} {city} 下雨，寻找替代城市...")
                result = scraper.find_nearest_sunny_city(city, weather_info.date)
                if result:
                    alt_city, distance, alt_weather = result
                    print(f"✅ 推荐: {alt_city} (距离: {distance:.2f}km, 天气: {alt_weather.weather})")
                else:
                    print("❌ 未找到合适的替代城市")
    
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def main():
    """主函数"""
    print("🌤️  天气爬取和分析系统演示")
    print("=" * 50)
    
    while True:
        print("\n请选择演示模式:")
        print("1. 基础天气爬取器演示")
        print("2. 高级天气爬取器演示")
        print("3. 交互式查询")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            demo_basic_scraper()
        elif choice == '2':
            demo_advanced_scraper()
        elif choice == '3':
            interactive_demo()
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()