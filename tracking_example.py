#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面埋点使用示例
演示如何使用埋点系统进行用户行为统计
"""

import time
import random
from datetime import datetime, timedelta
from tracking_models import TrackingDatabase, UserEvent, PageView, generate_session_id, generate_event_id
from tracking_analytics import TrackingAnalytics

def simulate_user_behavior():
    """模拟用户行为数据"""
    print("🎭 开始模拟用户行为...")
    
    # 初始化数据库
    try:
        db = TrackingDatabase()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 模拟用户数据
    users = ['user_001', 'user_002', 'user_003', 'user_004', 'user_005']
    pages = [
        {'url': 'https://example.com/', 'title': '首页'},
        {'url': 'https://example.com/products', 'title': '产品列表'},
        {'url': 'https://example.com/product/123', 'title': '产品详情'},
        {'url': 'https://example.com/cart', 'title': '购物车'},
        {'url': 'https://example.com/checkout', 'title': '结算页面'},
        {'url': 'https://example.com/login', 'title': '登录页面'},
        {'url': 'https://example.com/profile', 'title': '个人中心'}
    ]
    
    event_types = ['page_view', 'click', 'scroll', 'form_submit', 'custom_event']
    
    # 模拟多天数据
    for day in range(7):
        print(f"📅 模拟第 {day + 1} 天的数据...")
        
        for user in users:
            session_id = generate_session_id()
            user_events = random.randint(5, 20)  # 每个用户每天5-20个事件
            
            for event_num in range(user_events):
                # 随机选择页面
                page = random.choice(pages)
                
                # 随机选择事件类型
                event_type = random.choice(event_types)
                
                # 创建用户事件
                event = UserEvent(
                    event_id=generate_event_id(),
                    user_id=user,
                    session_id=session_id,
                    event_type=event_type,
                    page_url=page['url'],
                    page_title=page['title'],
                    element_id=f"element_{random.randint(1, 100)}" if event_type == 'click' else None,
                    element_class=f"btn btn-{random.choice(['primary', 'secondary', 'success'])}" if event_type == 'click' else None,
                    element_text=f"按钮文本_{random.randint(1, 10)}" if event_type == 'click' else None,
                    x_position=random.randint(0, 1920) if event_type == 'click' else None,
                    y_position=random.randint(0, 1080) if event_type == 'click' else None,
                    scroll_depth=random.uniform(0, 100) if event_type == 'scroll' else None,
                    referrer=random.choice(['https://google.com', 'https://baidu.com', 'https://bing.com', None]),
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    screen_resolution=f"{random.choice([1920, 1366, 1440, 1536])}x{random.choice([1080, 768, 900, 864])}",
                    viewport_size=f"{random.randint(1200, 1920)}x{random.randint(600, 1080)}",
                    timestamp=datetime.now() - timedelta(days=day) + timedelta(minutes=random.randint(0, 1440)),
                    custom_data={'source': 'simulation', 'day': day + 1} if event_type == 'custom_event' else None,
                    duration=random.uniform(0.1, 5.0) if event_type in ['page_view', 'form_submit'] else None
                )
                
                # 插入事件
                db.insert_event(event)
                
                # 如果是页面访问事件，也插入页面访问记录
                if event_type == 'page_view':
                    pageview = PageView(
                        page_id=generate_event_id(),
                        user_id=user,
                        session_id=session_id,
                        page_url=page['url'],
                        page_title=page['title'],
                        referrer=event.referrer,
                        user_agent=event.user_agent,
                        screen_resolution=event.screen_resolution,
                        viewport_size=event.viewport_size,
                        load_time=random.uniform(0.5, 3.0),
                        timestamp=event.timestamp,
                        exit_timestamp=event.timestamp + timedelta(seconds=random.uniform(10, 300)),
                        duration=random.uniform(10, 300)
                    )
                    db.insert_pageview(pageview)
                
                # 添加一些延迟，模拟真实用户行为
                time.sleep(0.01)
    
    print("✅ 用户行为模拟完成")
    db.close()

def demo_analytics():
    """演示数据分析功能"""
    print("\n📊 开始数据分析演示...")
    
    try:
        # 初始化数据库和分析器
        db = TrackingDatabase()
        analytics = TrackingAnalytics(db)
        
        # 1. 获取用户行为摘要
        print("\n1️⃣ 用户行为摘要:")
        summary = analytics.get_user_behavior_summary(days=7)
        print(f"   总事件数: {summary['overview']['total_events']:,}")
        print(f"   页面访问: {summary['overview']['total_page_views']:,}")
        print(f"   活跃用户: {summary['overview']['active_users']:,}")
        print(f"   总会话数: {summary['overview']['total_sessions']:,}")
        
        # 2. 事件类型分布
        print("\n2️⃣ 事件类型分布:")
        for event_type in summary['event_types']:
            print(f"   {event_type['event_type']}: {event_type['count']:,} 次")
        
        # 3. 热门页面TOP5
        print("\n3️⃣ 热门页面TOP5:")
        for i, page in enumerate(summary['top_pages'][:5], 1):
            print(f"   {i}. {page['page_title']} - {page['views']:,} 次访问")
        
        # 4. 漏斗分析
        print("\n4️⃣ 漏斗分析:")
        funnel_steps = ['page_view', 'click', 'form_submit']
        funnel = analytics.get_funnel_analysis(funnel_steps, days=7)
        for step in funnel['funnel_steps']:
            print(f"   {step['step']}: {step['users']:,} 用户 (转化率: {step['conversion_rate']:.1f}%)")
        
        # 5. 实时统计
        print("\n5️⃣ 实时统计:")
        realtime = analytics.get_real_time_stats()
        print(f"   最近1小时事件: {realtime['recent_events_1h']:,}")
        print(f"   最近24小时事件: {realtime['recent_events_24h']:,}")
        print(f"   当前在线用户: {realtime['online_users']:,}")
        
        # 6. 生成可视化报告
        print("\n6️⃣ 生成可视化报告...")
        report_path = analytics.generate_visualization_report(days=7)
        if report_path:
            print(f"   📈 报告已生成: {report_path}")
        
        # 7. 导出数据
        print("\n7️⃣ 导出数据...")
        exported_files = analytics.export_data_to_csv(days=7)
        if exported_files:
            print(f"   📁 数据已导出: {exported_files}")
        
        db.close()
        print("\n✅ 数据分析演示完成")
        
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")

def demo_api_usage():
    """演示API使用"""
    print("\n🌐 API使用演示:")
    print("   1. 启动API服务: python tracking_api.py")
    print("   2. 健康检查: GET http://localhost:5000/api/health")
    print("   3. 发送事件: POST http://localhost:5000/api/track/event")
    print("   4. 发送页面访问: POST http://localhost:5000/api/track/pageview")
    print("   5. 批量发送: POST http://localhost:5000/api/track/batch")
    print("   6. 获取事件统计: GET http://localhost:5000/api/stats/events")
    print("   7. 获取页面统计: GET http://localhost:5000/api/stats/pages")

def demo_frontend_integration():
    """演示前端集成"""
    print("\n💻 前端集成演示:")
    print("   1. 在HTML中引入SDK:")
    print("      <script src='tracking_sdk.js'></script>")
    print("   2. 初始化埋点:")
    print("      <script>")
    print("      initTracking({")
    print("          apiUrl: 'http://localhost:5000/api',")
    print("          userId: 'user_123',")
    print("          debug: true")
    print("      });")
    print("      </script>")
    print("   3. 手动跟踪事件:")
    print("      getTracking().trackEvent('custom_event', {")
    print("          custom_data: { action: 'button_click' }")
    print("      });")

def main():
    """主函数"""
    print("🚀 页面埋点系统演示")
    print("=" * 50)
    
    # 选择演示模式
    print("\n请选择演示模式:")
    print("1. 模拟用户行为数据")
    print("2. 数据分析演示")
    print("3. API使用说明")
    print("4. 前端集成说明")
    print("5. 全部演示")
    
    try:
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            simulate_user_behavior()
        elif choice == '2':
            demo_analytics()
        elif choice == '3':
            demo_api_usage()
        elif choice == '4':
            demo_frontend_integration()
        elif choice == '5':
            simulate_user_behavior()
            demo_analytics()
            demo_api_usage()
            demo_frontend_integration()
        else:
            print("❌ 无效选择")
            return
        
        print("\n🎉 演示完成！")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")

if __name__ == '__main__':
    main()