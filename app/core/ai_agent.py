"""
AI智能体核心类
支持多轮对话、上下文理解和个性化推荐
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import openai
from app.core.config import settings
from app.core.cache import CacheManager
from app.core.content_filter import ContentFilter
from app.services.gis_service import GISService
from app.services.route_optimizer import RouteOptimizer

class TravelAgent:
    """旅游路线规划智能体"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.content_filter = ContentFilter()
        self.gis_service = GISService()
        self.route_optimizer = RouteOptimizer()
        self.conversation_history = {}  # 存储用户对话历史
        
        # 初始化OpenAI客户端
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
    
    async def process_request(self, user_id: str, request: str, context: Dict = None) -> Dict:
        """
        处理用户请求，生成个性化旅游路线
        
        Args:
            user_id: 用户ID
            request: 用户请求文本
            context: 上下文信息（目的地、时间、预算等）
        
        Returns:
            包含路线规划的响应字典
        """
        try:
            # 内容安全过滤
            if not await self.content_filter.is_safe(request):
                return {
                    "success": False,
                    "error": "输入内容包含敏感信息，请重新输入",
                    "error_code": "CONTENT_FILTERED"
                }
            
            # 获取用户历史对话
            conversation = self.conversation_history.get(user_id, [])
            
            # 解析用户需求
            requirements = await self._parse_requirements(request, context, conversation)
            
            # 验证需求完整性
            validation_result = await self._validate_requirements(requirements)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "error_code": "INVALID_INPUT"
                }
            
            # 生成路线规划
            route_plan = await self._generate_route_plan(requirements, user_id)
            
            # 更新对话历史
            self._update_conversation_history(user_id, request, route_plan)
            
            return {
                "success": True,
                "route_plan": route_plan,
                "requirements": requirements,
                "explanation": await self._generate_explanation(route_plan, requirements)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"处理请求时发生错误: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
    
    async def _parse_requirements(self, request: str, context: Dict, conversation: List) -> Dict:
        """解析用户需求"""
        # 使用LLM解析用户输入
        prompt = f"""
        请从以下用户输入中提取旅游需求信息：
        
        用户输入：{request}
        上下文信息：{json.dumps(context or {}, ensure_ascii=False)}
        历史对话：{json.dumps(conversation[-3:], ensure_ascii=False)}
        
        请提取以下信息并以JSON格式返回：
        {{
            "destination": "目的地",
            "travel_dates": "旅行日期",
            "duration_days": "行程天数",
            "budget": "预算范围",
            "travel_style": "旅行风格（亲子游/蜜月游/独自旅行等）",
            "interests": ["兴趣点列表"],
            "special_requirements": "特殊要求",
            "group_size": "人数"
        }}
        """
        
        try:
            response = await self._call_llm(prompt)
            requirements = json.loads(response)
            return requirements
        except:
            # 如果LLM解析失败，使用规则解析
            return self._rule_based_parse(request, context)
    
    def _rule_based_parse(self, request: str, context: Dict) -> Dict:
        """基于规则的简单解析"""
        requirements = {
            "destination": context.get("destination", ""),
            "travel_dates": context.get("travel_dates", ""),
            "duration_days": context.get("duration_days", 3),
            "budget": context.get("budget", ""),
            "travel_style": context.get("travel_style", ""),
            "interests": context.get("interests", []),
            "special_requirements": context.get("special_requirements", ""),
            "group_size": context.get("group_size", 1)
        }
        return requirements
    
    async def _validate_requirements(self, requirements: Dict) -> Dict:
        """验证需求完整性"""
        errors = []
        
        if not requirements.get("destination"):
            errors.append("请提供目的地信息")
        
        if not requirements.get("travel_dates"):
            errors.append("请提供旅行日期")
        
        if not requirements.get("duration_days") or requirements["duration_days"] < 1:
            errors.append("请提供合理的行程天数")
        
        if not requirements.get("budget"):
            errors.append("请提供预算信息")
        
        # 验证日期格式
        if requirements.get("travel_dates"):
            try:
                datetime.strptime(requirements["travel_dates"], "%Y-%m-%d")
            except ValueError:
                errors.append("日期格式不正确，请使用YYYY-MM-DD格式")
        
        return {
            "valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None
        }
    
    async def _generate_route_plan(self, requirements: Dict, user_id: str) -> Dict:
        """生成路线规划"""
        # 检查缓存
        cache_key = f"route_plan:{hash(json.dumps(requirements, sort_keys=True))}"
        cached_plan = await self.cache_manager.get(cache_key)
        if cached_plan:
            return cached_plan
        
        # 获取景点信息
        scenic_spots = await self.gis_service.get_scenic_spots(
            destination=requirements["destination"],
            interests=requirements.get("interests", [])
        )
        
        # 获取酒店信息
        hotels = await self.gis_service.get_hotels(
            destination=requirements["destination"],
            budget=requirements.get("budget", "")
        )
        
        # 优化路线
        optimized_route = await self.route_optimizer.optimize_route(
            scenic_spots=scenic_spots,
            hotels=hotels,
            requirements=requirements
        )
        
        # 生成详细路线
        route_plan = {
            "destination": requirements["destination"],
            "duration_days": requirements["duration_days"],
            "budget_estimate": self._calculate_budget_estimate(optimized_route, requirements),
            "daily_itinerary": self._generate_daily_itinerary(optimized_route, requirements),
            "accommodation": self._select_accommodation(hotels, requirements),
            "transportation": self._plan_transportation(optimized_route, requirements),
            "tips": self._generate_tips(requirements),
            "created_at": datetime.now().isoformat()
        }
        
        # 缓存结果
        await self.cache_manager.set(cache_key, route_plan, ttl=settings.cache_ttl)
        
        return route_plan
    
    def _calculate_budget_estimate(self, route: Dict, requirements: Dict) -> Dict:
        """计算预算估算"""
        # 简化的预算计算
        base_cost = 500  # 基础费用
        daily_cost = 300  # 每日费用
        days = requirements.get("duration_days", 3)
        
        return {
            "total_estimate": base_cost + (daily_cost * days),
            "breakdown": {
                "accommodation": daily_cost * days * 0.4,
                "meals": daily_cost * days * 0.3,
                "transportation": daily_cost * days * 0.2,
                "attractions": daily_cost * days * 0.1
            }
        }
    
    def _generate_daily_itinerary(self, route: Dict, requirements: Dict) -> List[Dict]:
        """生成每日行程"""
        days = requirements.get("duration_days", 3)
        itinerary = []
        
        for day in range(1, days + 1):
            daily_plan = {
                "day": day,
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "morning": f"上午游览景点A（推荐理由：符合您的兴趣偏好）",
                "afternoon": f"下午游览景点B（推荐理由：距离适中，交通便利）",
                "evening": f"晚上体验当地特色活动",
                "meals": {
                    "breakfast": "推荐当地特色早餐",
                    "lunch": "推荐景点附近餐厅",
                    "dinner": "推荐当地特色晚餐"
                }
            }
            itinerary.append(daily_plan)
        
        return itinerary
    
    def _select_accommodation(self, hotels: List[Dict], requirements: Dict) -> Dict:
        """选择住宿"""
        if not hotels:
            return {"name": "待定", "reason": "暂无可用酒店信息"}
        
        # 根据预算和偏好选择酒店
        selected_hotel = hotels[0]  # 简化选择逻辑
        return {
            "name": selected_hotel.get("name", "待定"),
            "location": selected_hotel.get("location", ""),
            "price_range": selected_hotel.get("price_range", ""),
            "reason": "根据您的预算和位置偏好推荐"
        }
    
    def _plan_transportation(self, route: Dict, requirements: Dict) -> List[Dict]:
        """规划交通"""
        return [
            {
                "type": "到达目的地",
                "method": "飞机/火车",
                "duration": "2-4小时",
                "cost": "根据距离和方式而定"
            },
            {
                "type": "市内交通",
                "method": "地铁/公交/出租车",
                "duration": "根据景点距离",
                "cost": "每日约50-100元"
            }
        ]
    
    def _generate_tips(self, requirements: Dict) -> List[str]:
        """生成旅行贴士"""
        tips = [
            "建议提前预订热门景点门票",
            "注意当地天气情况，准备合适衣物",
            "了解当地交通规则和习惯",
            "准备常用药品和应急联系方式"
        ]
        
        if requirements.get("travel_style") == "亲子游":
            tips.append("选择适合儿童的景点和活动")
        elif requirements.get("travel_style") == "蜜月游":
            tips.append("选择浪漫的景点和餐厅")
        
        return tips
    
    async def _generate_explanation(self, route_plan: Dict, requirements: Dict) -> str:
        """生成推荐理由解释"""
        explanations = []
        
        # 景点选择理由
        explanations.append("景点选择基于您的兴趣偏好和地理位置优化")
        
        # 时间安排理由
        explanations.append("时间安排考虑了景点开放时间和交通便利性")
        
        # 住宿选择理由
        if route_plan.get("accommodation", {}).get("reason"):
            explanations.append(f"住宿选择：{route_plan['accommodation']['reason']}")
        
        return "；".join(explanations)
    
    async def _call_llm(self, prompt: str) -> str:
        """调用大语言模型"""
        try:
            # 这里应该调用实际的LLM API
            # 简化实现，返回模拟响应
            return json.dumps({
                "destination": "北京",
                "travel_dates": "2024-01-01",
                "duration_days": 3,
                "budget": "中等",
                "travel_style": "独自旅行",
                "interests": ["历史文化", "美食"],
                "special_requirements": "",
                "group_size": 1
            }, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
    
    def _update_conversation_history(self, user_id: str, request: str, response: Dict):
        """更新对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_input": request,
            "agent_response": response
        })
        
        # 保持最近10轮对话
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]