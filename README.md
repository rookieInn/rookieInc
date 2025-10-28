# 天气爬取和分析系统

一个智能的天气爬取系统，可以获取城市未来几天的天气状况，并帮助用户找到下雨城市附近最近的晴天城市。

## 功能特点

- 🌤️ **天气数据获取**: 支持获取城市未来7天的详细天气信息
- 🗺️ **地理位置计算**: 精确计算城市间距离，使用Haversine公式
- 🔍 **智能推荐**: 自动为下雨城市推荐最近的晴天城市
- 📊 **批量分析**: 支持同时分析多个城市的天气模式
- 🎯 **灵活配置**: 可设置最大搜索距离和查询天数

## 支持的城市

系统内置了50+个中国主要城市的坐标数据，包括：

**一线城市**: 北京、上海、广州、深圳
**省会城市**: 杭州、南京、成都、重庆、武汉、西安等
**重要城市**: 苏州、青岛、大连、厦门、福州等
**更多城市**: 无锡、宁波、温州、嘉兴等长三角城市

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基础使用

```python
from weather_scraper import WeatherScraper

# 创建爬取器实例
scraper = WeatherScraper()

# 查找北京明天最近的晴天城市
tomorrow = "2024-01-15"  # 替换为实际日期
result = scraper.find_nearest_sunny_city('北京', tomorrow)

if result:
    city, distance, weather_info = result
    print(f"推荐城市: {city}")
    print(f"距离: {distance:.2f} 公里")
    print(f"天气: {weather_info.weather}")
```

### 2. 高级使用

```python
from advanced_weather_scraper import AdvancedWeatherScraper

# 创建高级爬取器实例
scraper = AdvancedWeatherScraper()

# 分析多个城市的天气模式
cities = ['北京', '上海', '广州', '深圳']
results = scraper.get_weather_recommendations(cities, 7)
scraper.print_recommendations(results)
```

### 3. 交互式演示

```bash
python weather_demo.py
```

## 核心功能

### 天气数据获取

系统支持两种数据获取方式：

1. **模拟数据**: 基于地理位置和季节生成合理的模拟天气数据
2. **真实API**: 集成OpenWeatherMap API获取实时天气数据（需要API key）

### 距离计算

使用Haversine公式精确计算地球表面两点间的距离：

```python
def calculate_distance(lat1, lon1, lat2, lon2):
    # 返回距离（公里）
```

### 天气判断

系统能智能识别不同类型的天气：

- **雨天**: 包含"雨"、"雷"、"雪"等关键词
- **晴天**: 包含"晴"、"多云"等关键词

### 推荐算法

1. 获取目标城市指定日期的天气数据
2. 判断是否为雨天
3. 遍历所有其他城市
4. 计算距离并筛选晴天城市
5. 返回距离最近的晴天城市

## 配置选项

### 环境变量

```bash
# 设置OpenWeatherMap API key（可选）
export OPENWEATHER_API_KEY="your_api_key_here"
```

### 参数配置

- `max_distance`: 最大搜索距离（默认500公里）
- `days`: 查询天数（默认7天）
- `cities`: 要分析的城市列表

## 示例输出

```
=== 天气推荐结果 ===
分析期间: 2024-01-15 到 2024-01-17

找到 2 个推荐:
------------------------------------------------------------
1. 2024-01-15
   下雨城市: 北京
   推荐城市: 天津
   距离: 120.45 公里
   天气: 晴天
   温度: 18.5°C
   湿度: 65%
   风速: 3.2 m/s

2. 2024-01-16
   下雨城市: 上海
   推荐城市: 杭州
   距离: 164.32 公里
   天气: 多云
   温度: 22.1°C
   湿度: 58%
   风速: 2.8 m/s
```

## 扩展功能

### 添加新城市

在 `city_coordinates` 字典中添加新城市：

```python
self.city_coordinates['新城市'] = (纬度, 经度)
```

### 自定义天气判断

重写 `_is_rainy_weather` 和 `_is_sunny_weather` 方法：

```python
def _is_rainy_weather(self, weather: str) -> bool:
    # 自定义雨天判断逻辑
    return "自定义关键词" in weather
```

## 注意事项

1. **API限制**: 使用真实API时请注意调用频率限制
2. **数据准确性**: 模拟数据仅供参考，实际使用建议配置真实API
3. **网络连接**: 需要稳定的网络连接获取天气数据
4. **城市支持**: 目前主要支持中国城市，可扩展支持其他国家

## 技术实现

- **语言**: Python 3.7+
- **依赖**: requests, math, datetime
- **算法**: Haversine距离计算
- **数据源**: OpenWeatherMap API / 模拟数据

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issues联系。