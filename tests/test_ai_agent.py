"""
AI智能体测试
"""

import pytest
import asyncio
from app.core.ai_agent import TravelAgent

class TestTravelAgent:
    """旅游智能体测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建智能体实例"""
        return TravelAgent()
    
    @pytest.mark.asyncio
    async def test_process_request_success(self, agent):
        """测试成功处理请求"""
        request = "我想去北京旅游3天，预算中等，喜欢历史文化"
        context = {
            "destination": "北京",
            "travel_dates": "2024-01-01",
            "duration_days": 3,
            "budget": "中等"
        }
        
        result = await agent.process_request("test_user", request, context)
        
        assert result["success"] is True
        assert "route_plan" in result
        assert result["route_plan"]["destination"] == "北京"
        assert result["route_plan"]["duration_days"] == 3
    
    @pytest.mark.asyncio
    async def test_process_request_invalid_input(self, agent):
        """测试无效输入处理"""
        request = "我想去旅游"
        context = {}
        
        result = await agent.process_request("test_user", request, context)
        
        assert result["success"] is False
        assert "error" in result
        assert result["error_code"] == "INVALID_INPUT"
    
    @pytest.mark.asyncio
    async def test_content_filtering(self, agent):
        """测试内容过滤"""
        request = "我想去一些危险的地方旅游"
        context = {}
        
        result = await agent.process_request("test_user", request, context)
        
        # 由于内容过滤，应该返回错误
        assert result["success"] is False
        assert result["error_code"] == "CONTENT_FILTERED"
    
    def test_conversation_history(self, agent):
        """测试对话历史记录"""
        user_id = "test_user"
        
        # 第一次对话
        agent._update_conversation_history(user_id, "我想去北京", {"response": "好的"})
        
        # 检查历史记录
        assert user_id in agent.conversation_history
        assert len(agent.conversation_history[user_id]) == 1
        
        # 第二次对话
        agent._update_conversation_history(user_id, "预算1000元", {"response": "了解"})
        
        # 检查历史记录更新
        assert len(agent.conversation_history[user_id]) == 2
        
        # 测试历史记录限制
        for i in range(15):
            agent._update_conversation_history(user_id, f"消息{i}", {"response": f"回复{i}"})
        
        # 应该只保留最近10条记录
        assert len(agent.conversation_history[user_id]) == 10