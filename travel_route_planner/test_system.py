#!/usr/bin/env python3
"""
AI旅游路线规划系统测试脚本
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.route_planner import RoutePlanner, ScenicSpot, RouteConstraint
from backend.ai_models import AIModelManager
from backend.cache_manager import CacheManager
from database.models import User, TravelPlan, ScenicSpot as DBSpot
from database.database import get_db, init_db
from config.settings import settings


async def test_route_planner():
    """测试路线规划功能"""
    print("🧪 测试路线规划功能...")
    
    # 创建测试景点数据
    test_spots = [
        ScenicSpot(
            id=1,
            name="天安门广场",
            latitude=39.9042,
            longitude=116.4074,
            category="人文景观",
            rating=4.8,
            duration_hours=2.0,
            opening_hours="05:00-22:00",
            ticket_price=0.0,
            description="世界最大的城市广场"
        ),
        ScenicSpot(
            id=2,
            name="故宫博物院",
            latitude=39.9163,
            longitude=116.3972,
            category="人文景观",
            rating=4.7,
            duration_hours=3.0,
            opening_hours="08:30-17:00",
            ticket_price=60.0,
            description="明清两代皇家宫殿"
        ),
        ScenicSpot(
            id=3,
            name="颐和园",
            latitude=39.9999,
            longitude=116.2755,
            category="人文景观",
            rating=4.6,
            duration_hours=4.0,
            opening_hours="06:30-18:00",
            ticket_price=30.0,
            description="中国古典园林之首"
        )
    ]
    
    # 创建路线规划器
    planner = RoutePlanner()
    
    # 设置约束条件
    constraints = RouteConstraint(
        max_daily_spots=3,
        max_daily_hours=8.0,
        budget_limit=500.0
    )
    
    # 生成路线规划
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=2)
    
    try:
        route_plan = await planner.plan_route(
            destination="北京",
            start_date=start_date,
            end_date=end_date,
            scenic_spots=test_spots,
            constraints=constraints
        )
        
        print("✅ 路线规划测试通过")
        print(f"   目的地: {route_plan['destination']}")
        print(f"   旅行天数: {route_plan['travel_days']}")
        print(f"   总费用: ¥{route_plan['total_cost']['total']}")
        print(f"   每日计划数: {len(route_plan['daily_plans'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 路线规划测试失败: {e}")
        return False


async def test_cache_manager():
    """测试缓存管理功能"""
    print("🧪 测试缓存管理功能...")
    
    try:
        cache_manager = CacheManager()
        await cache_manager.init_redis()
        
        # 测试基本缓存操作
        test_key = "test_key"
        test_data = {"message": "Hello, World!", "timestamp": datetime.now().isoformat()}
        
        # 设置缓存
        await cache_manager.set(test_key, test_data, ttl=60)
        
        # 获取缓存
        cached_data = await cache_manager.get(test_key)
        
        if cached_data and cached_data["message"] == test_data["message"]:
            print("✅ 缓存管理测试通过")
            
            # 清理测试数据
            await cache_manager.delete(test_key)
            return True
        else:
            print("❌ 缓存管理测试失败: 数据不匹配")
            return False
            
    except Exception as e:
        print(f"❌ 缓存管理测试失败: {e}")
        return False


def test_database_models():
    """测试数据库模型"""
    print("🧪 测试数据库模型...")
    
    try:
        # 测试用户模型
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        # 测试旅游计划模型
        plan = TravelPlan(
            user_id=1,
            title="测试计划",
            destination="北京",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=1)
        )
        
        # 测试景点模型
        spot = DBSpot(
            name="测试景点",
            location="北京",
            latitude=39.9042,
            longitude=116.4074,
            category="测试",
            rating=4.5
        )
        
        print("✅ 数据库模型测试通过")
        print(f"   用户模型: {user.username}")
        print(f"   计划模型: {plan.title}")
        print(f"   景点模型: {spot.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库模型测试失败: {e}")
        return False


def test_configuration():
    """测试配置系统"""
    print("🧪 测试配置系统...")
    
    try:
        # 测试基本配置
        assert settings.app_name == "AI旅游路线规划系统"
        assert settings.port == 8000
        assert settings.host == "0.0.0.0"
        
        print("✅ 配置系统测试通过")
        print(f"   应用名称: {settings.app_name}")
        print(f"   端口: {settings.port}")
        print(f"   主机: {settings.host}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False


async def test_ai_models():
    """测试AI模型集成"""
    print("🧪 测试AI模型集成...")
    
    try:
        ai_manager = AIModelManager()
        
        # 测试模型初始化
        qwen_available = ai_manager._init_qwen()
        qianfan_available = ai_manager._init_qianfan()
        openai_available = ai_manager._init_openai()
        
        print("✅ AI模型集成测试通过")
        print(f"   通义千问: {'可用' if qwen_available else '不可用'}")
        print(f"   文心一言: {'可用' if qianfan_available else '不可用'}")
        print(f"   OpenAI: {'可用' if openai_available else '不可用'}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI模型集成测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行AI旅游路线规划系统测试...")
    print("=" * 50)
    
    tests = [
        ("配置系统", test_configuration),
        ("数据库模型", test_database_models),
        ("缓存管理", test_cache_manager),
        ("AI模型集成", test_ai_models),
        ("路线规划", test_route_planner),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")
        return False


def print_system_info():
    """打印系统信息"""
    print("🔧 系统信息:")
    print(f"   Python版本: {sys.version}")
    print(f"   工作目录: {os.getcwd()}")
    print(f"   配置文件: {settings.app_name} v{settings.app_version}")
    print(f"   调试模式: {settings.debug}")
    print()


if __name__ == "__main__":
    print_system_info()
    
    # 运行测试
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ 系统测试完成，可以启动服务！")
        print("   运行命令: python main.py")
        print("   访问地址: http://localhost:8000")
    else:
        print("\n❌ 系统测试失败，请检查配置后重试。")
        sys.exit(1)