"""
AI模型集成模块
支持通义千问、文心一言、OpenAI等模型
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
import dashscope
from qianfan import ChatCompletion
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.models = {
            "qwen": self._init_qwen,
            "qianfan": self._init_qianfan,
            "openai": self._init_openai
        }
        self.current_model = "qwen"  # 默认使用通义千问
        
    def _init_qwen(self):
        """初始化通义千问"""
        if settings.dashscope_api_key:
            dashscope.api_key = settings.dashscope_api_key
            return True
        return False
    
    def _init_qianfan(self):
        """初始化文心一言"""
        if settings.qianfan_ak and settings.qianfan_sk:
            return True
        return False
    
    def _init_openai(self):
        """初始化OpenAI"""
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            return True
        return False
    
    async def generate_route_plan(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        travel_type: Optional[str] = None,
        preferences: Optional[Dict] = None,
        scenic_spots: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """生成旅游路线规划"""
        
        # 构建提示词
        prompt = self._build_route_prompt(
            destination, start_date, end_date, budget, 
            travel_type, preferences, scenic_spots
        )
        
        try:
            if self.current_model == "qwen":
                response = await self._call_qwen(prompt)
            elif self.current_model == "qianfan":
                response = await self._call_qianfan(prompt)
            elif self.current_model == "openai":
                response = await self._call_openai(prompt)
            else:
                raise ValueError(f"不支持的模型: {self.current_model}")
            
            # 解析响应并生成结构化路线规划
            route_plan = self._parse_route_response(response, destination, start_date, end_date)
            return route_plan
            
        except Exception as e:
            logger.error(f"AI模型调用失败: {e}")
            raise
    
    def _build_route_prompt(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float],
        travel_type: Optional[str],
        preferences: Optional[Dict],
        scenic_spots: Optional[List[Dict]]
    ) -> str:
        """构建路线规划提示词"""
        
        prompt = f"""
你是一个专业的旅游路线规划师。请根据以下信息为用户制定详细的旅游路线规划：

**基本信息：**
- 目的地：{destination}
- 出发时间：{start_date}
- 返回时间：{end_date}
- 旅行类型：{travel_type or '休闲游'}
- 预算：{f'{budget}元' if budget else '无限制'}

**用户偏好：**
{json.dumps(preferences, ensure_ascii=False, indent=2) if preferences else '无特殊偏好'}

**可选景点信息：**
{json.dumps(scenic_spots, ensure_ascii=False, indent=2) if scenic_spots else '请推荐当地热门景点'}

**请按以下格式输出路线规划：**

1. **行程概览**：简要介绍整体行程安排
2. **每日详细行程**：
   - 第X天：日期
     - 上午：景点名称 + 游览时间 + 简要介绍
     - 下午：景点名称 + 游览时间 + 简要介绍
     - 晚上：活动安排 + 住宿建议
3. **费用预算**：详细列出各项费用
4. **交通建议**：各景点间的交通方式
5. **注意事项**：天气、着装、安全等提醒
6. **推荐理由**：解释为什么选择这些景点和安排

请确保路线规划合理、实用，符合用户的时间、预算和偏好要求。
"""
        return prompt
    
    async def _call_qwen(self, prompt: str) -> str:
        """调用通义千问模型"""
        try:
            response = dashscope.Generation.call(
                model=settings.qwen_model,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.text
            else:
                raise Exception(f"通义千问调用失败: {response.message}")
                
        except Exception as e:
            logger.error(f"通义千问调用异常: {e}")
            raise
    
    async def _call_qianfan(self, prompt: str) -> str:
        """调用文心一言模型"""
        try:
            chat_comp = ChatCompletion()
            response = chat_comp.do(
                model="ERNIE-Bot-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_output_tokens=2000
            )
            
            if response.get("code") == 200:
                return response["result"]
            else:
                raise Exception(f"文心一言调用失败: {response.get('message', '未知错误')}")
                
        except Exception as e:
            logger.error(f"文心一言调用异常: {e}")
            raise
    
    async def _call_openai(self, prompt: str) -> str:
        """调用OpenAI模型"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI调用异常: {e}")
            raise
    
    def _parse_route_response(self, response: str, destination: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """解析AI响应并生成结构化路线规划"""
        
        # 这里可以添加更复杂的解析逻辑
        # 目前返回基本结构
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "plan_content": response,
            "generated_at": datetime.now().isoformat(),
            "ai_model": self.current_model,
            "status": "success"
        }
    
    async def optimize_route(
        self,
        current_plan: Dict[str, Any],
        feedback: str,
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """根据用户反馈优化路线"""
        
        prompt = f"""
请根据用户反馈优化以下旅游路线规划：

**当前路线规划：**
{json.dumps(current_plan, ensure_ascii=False, indent=2)}

**用户反馈：**
{feedback}

**优化约束：**
{json.dumps(constraints, ensure_ascii=False, indent=2) if constraints else '无特殊约束'}

请提供优化后的路线规划，保持原有格式，并说明优化的原因。
"""
        
        try:
            if self.current_model == "qwen":
                response = await self._call_qwen(prompt)
            elif self.current_model == "qianfan":
                response = await self._call_qianfan(prompt)
            elif self.current_model == "openai":
                response = await self._call_openai(prompt)
            else:
                raise ValueError(f"不支持的模型: {self.current_model}")
            
            return {
                "optimized_plan": response,
                "optimization_reason": "根据用户反馈进行了优化",
                "optimized_at": datetime.now().isoformat(),
                "ai_model": self.current_model
            }
            
        except Exception as e:
            logger.error(f"路线优化失败: {e}")
            raise
    
    async def chat_with_user(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> str:
        """与用户进行对话"""
        
        # 构建对话上下文
        messages = []
        
        if conversation_history:
            for msg in conversation_history[-10:]:  # 只保留最近10条对话
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # 添加上下文信息
        if context:
            context_prompt = f"当前旅游规划上下文：{json.dumps(context, ensure_ascii=False)}"
            messages.append({"role": "system", "content": context_prompt})
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            if self.current_model == "qwen":
                response = await self._call_qwen("\n".join([f"{msg['role']}: {msg['content']}" for msg in messages]))
            elif self.current_model == "qianfan":
                response = await self._call_qianfan("\n".join([f"{msg['role']}: {msg['content']}" for msg in messages]))
            elif self.current_model == "openai":
                response = await self._call_openai("\n".join([f"{msg['role']}: {msg['content']}" for msg in messages]))
            else:
                raise ValueError(f"不支持的模型: {self.current_model}")
            
            return response
            
        except Exception as e:
            logger.error(f"对话生成失败: {e}")
            raise


# 创建全局AI模型管理器实例
ai_manager = AIModelManager()