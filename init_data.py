#!/usr/bin/env python3
"""
初始化演示数据
"""

import asyncio
from app.core.database import init_db, AsyncSessionLocal
from app.models.user import User
from app.models.travel import ScenicSpot, Hotel, Transportation
from app.core.security import get_password_hash

async def init_demo_data():
    """初始化演示数据"""
    # 初始化数据库
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # 创建演示用户
        demo_user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=get_password_hash("demo123"),
            is_active=True,
            preferred_language="zh",
            travel_style="独自旅行",
            budget_range="中等",
            interests='["历史文化", "美食", "自然风光"]'
        )
        
        # 检查用户是否已存在
        existing_user = await session.get(User, 1)
        if not existing_user:
            session.add(demo_user)
            await session.commit()
            print("✅ 演示用户创建成功: demo/demo123")
        
        # 创建演示景点数据
        scenic_spots = [
            ScenicSpot(
                name="故宫博物院",
                description="明清两朝的皇家宫殿，世界文化遗产",
                location="北京市东城区景山前街4号",
                latitude=39.9163,
                longitude=116.3972,
                opening_hours="08:30-17:00",
                ticket_price="60元",
                rating=4.8,
                category="历史文化"
            ),
            ScenicSpot(
                name="天安门广场",
                description="世界上最大的城市广场",
                location="北京市东城区东长安街",
                latitude=39.9042,
                longitude=116.4074,
                opening_hours="全天开放",
                ticket_price="免费",
                rating=4.7,
                category="历史文化"
            ),
            ScenicSpot(
                name="颐和园",
                description="中国古典园林之首",
                location="北京市海淀区新建宫门路19号",
                latitude=39.9999,
                longitude=116.2755,
                opening_hours="06:30-18:00",
                ticket_price="30元",
                rating=4.6,
                category="园林景观"
            ),
            ScenicSpot(
                name="外滩",
                description="上海标志性景观，万国建筑博览群",
                location="上海市黄浦区中山东一路",
                latitude=31.2397,
                longitude=121.4998,
                opening_hours="全天开放",
                ticket_price="免费",
                rating=4.5,
                category="现代建筑"
            ),
            ScenicSpot(
                name="西湖",
                description="中国著名的风景名胜区",
                location="浙江省杭州市西湖区龙井路1号",
                latitude=30.2741,
                longitude=120.1551,
                opening_hours="全天开放",
                ticket_price="免费",
                rating=4.7,
                category="自然风光"
            )
        ]
        
        # 检查景点是否已存在
        from sqlalchemy import text
        existing_spots = await session.execute(text("SELECT COUNT(*) FROM scenic_spots"))
        count = existing_spots.scalar()
        
        if count == 0:
            for spot in scenic_spots:
                session.add(spot)
            await session.commit()
            print("✅ 演示景点数据创建成功")
        
        # 创建演示酒店数据
        hotels = [
            Hotel(
                name="北京饭店",
                description="历史悠久的豪华酒店",
                location="北京市东城区东长安街33号",
                latitude=39.9042,
                longitude=116.4074,
                price_range="800-1500元/晚",
                rating=4.5,
                amenities='["WiFi", "健身房", "餐厅", "会议室"]'
            ),
            Hotel(
                name="上海和平饭店",
                description="外滩标志性建筑",
                location="上海市黄浦区南京东路20号",
                latitude=31.2397,
                longitude=121.4998,
                price_range="1200-2500元/晚",
                rating=4.6,
                amenities='["WiFi", "健身房", "餐厅", "酒吧", "SPA"]'
            ),
            Hotel(
                name="杭州西湖国宾馆",
                description="西湖边的豪华度假酒店",
                location="浙江省杭州市西湖区杨公堤18号",
                latitude=30.2741,
                longitude=120.1551,
                price_range="600-1200元/晚",
                rating=4.4,
                amenities='["WiFi", "健身房", "餐厅", "游泳池"]'
            )
        ]
        
        # 检查酒店是否已存在
        existing_hotels = await session.execute(text("SELECT COUNT(*) FROM hotels"))
        hotel_count = existing_hotels.scalar()
        
        if hotel_count == 0:
            for hotel in hotels:
                session.add(hotel)
            await session.commit()
            print("✅ 演示酒店数据创建成功")
        
        print("🎉 演示数据初始化完成！")
        print("📝 可以使用以下账号登录:")
        print("   用户名: demo")
        print("   密码: demo123")

if __name__ == "__main__":
    asyncio.run(init_demo_data())