"""
API接口测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPI:
    """API测试类"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "旅游路线规划智能体系统运行中"
        assert data["status"] == "healthy"
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_travel_plan_without_auth(self):
        """测试未认证用户创建路线规划"""
        travel_request = {
            "destination": "北京",
            "travel_dates": "2024-01-01",
            "duration_days": 3,
            "budget": "中等"
        }
        
        response = client.post("/api/v1/plan", json=travel_request)
        assert response.status_code == 401  # 未授权
    
    def test_get_destinations(self):
        """测试获取热门目的地"""
        response = client.get("/api/v1/destinations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "description" in data[0]
    
    def test_get_weather_info(self):
        """测试获取天气信息"""
        response = client.get("/api/v1/weather/北京")
        assert response.status_code == 200
        data = response.json()
        assert "location" in data
        assert "temperature" in data
        assert "weather" in data