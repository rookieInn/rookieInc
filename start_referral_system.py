#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享返佣裂变系统 - 快速启动脚本
Referral Commission Fission System - Quick Start Script

一键启动整个系统，包括：
1. 数据库初始化
2. API服务启动
3. 演示数据生成
4. 分析报告生成
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║            🚀 分享返佣裂变系统 - 快速启动 🚀                    ║
    ║                                                              ║
    ║        Referral Commission Fission System - Quick Start      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包检查完成")
    return True

def init_database():
    """初始化数据库"""
    print("\n🗄️  初始化数据库...")
    
    try:
        from referral_system import ReferralSystem
        system = ReferralSystem()
        print("✅ 数据库初始化完成")
        return system
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return None

def generate_demo_data(system):
    """生成演示数据"""
    print("\n📊 生成演示数据...")
    
    try:
        # 创建演示用户
        users = []
        
        # 创建根用户
        root_user = system.register_user("系统管理员", "admin@example.com", "13800000000")
        users.append(root_user)
        print(f"  ✅ 创建根用户: {root_user.username}")
        
        # 创建多级用户
        for i in range(1, 6):
            username = f"用户{i:02d}"
            email = f"user{i:02d}@example.com"
            phone = f"138000000{i:02d}"
            referrer = users[i-1] if i > 1 else root_user
            
            user = system.register_user(username, email, phone, referrer.invite_code)
            users.append(user)
            print(f"  ✅ 创建用户: {user.username} (层级: {user.level})")
        
        # 创建分享链接
        for i, user in enumerate(users[:3]):  # 只为前3个用户创建链接
            link = system.create_referral_link(
                user.user_id, 
                f"https://example.com/product/{i+1}",
                expires_days=30
            )
            print(f"  ✅ 创建分享链接: {link.short_code}")
        
        # 模拟点击和转化
        print("  🔄 模拟用户行为...")
        
        # 模拟点击
        for i in range(20):
            link_code = "abc123"  # 使用第一个链接的代码
            system.track_click(link_code, f"192.168.1.{i%10}", "Mozilla/5.0")
        
        # 模拟转化
        for i, user in enumerate(users[1:4]):  # 为第2-4个用户模拟转化
            order_id = f"ORDER_{i+1:03d}"
            amount = 1000 + i * 500
            commissions = system.process_conversion(user.user_id, order_id, amount)
            print(f"  ✅ 模拟转化: 订单 {order_id}, 金额 ¥{amount}")
        
        print("✅ 演示数据生成完成")
        return True
        
    except Exception as e:
        print(f"❌ 演示数据生成失败: {e}")
        return False

def start_api_server():
    """启动API服务器"""
    print("\n🌐 启动API服务器...")
    
    try:
        # 在后台启动API服务器
        process = subprocess.Popen([
            sys.executable, 'referral_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ API服务器启动成功")
            print("  📱 数据看板: http://localhost:5000")
            print("  🔗 API接口: http://localhost:5000/api/analytics")
            return process
        else:
            print("❌ API服务器启动失败")
            return None
            
    except Exception as e:
        print(f"❌ 启动API服务器失败: {e}")
        return None

def generate_analytics_report():
    """生成分析报告"""
    print("\n📈 生成分析报告...")
    
    try:
        from tracking_analytics import TrackingAnalytics
        analytics = TrackingAnalytics()
        
        # 生成分析报告
        report_file = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        analytics.generate_analytics_report(days=30, output_file=report_file)
        print(f"  ✅ 分析报告: {report_file}")
        
        # 创建可视化图表
        charts_dir = f"charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        analytics.create_visualization_charts(days=30, output_dir=charts_dir)
        print(f"  ✅ 可视化图表: {charts_dir}/")
        
        # 显示实时指标
        metrics = analytics.get_real_time_metrics()
        print(f"  📊 实时指标:")
        print(f"    今日注册: {metrics['today_registrations']}人")
        print(f"    今日点击: {metrics['today_clicks']}次")
        print(f"    今日转化: {metrics['today_conversions']}次")
        print(f"    今日返佣: ¥{metrics['today_commission']:.2f}")
        
        print("✅ 分析报告生成完成")
        return True
        
    except Exception as e:
        print(f"❌ 生成分析报告失败: {e}")
        return False

def show_usage_guide():
    """显示使用指南"""
    guide = """
    📖 使用指南:
    
    1. 🌐 访问数据看板
       - 打开浏览器访问: http://localhost:5000
       - 在界面中管理用户、创建链接、查看数据
    
    2. 🔗 API接口使用
       - 查看API文档: http://localhost:5000/api/analytics
       - 使用Postman或其他工具测试API
    
    3. 📊 数据分析
       - 查看生成的分析报告文件
       - 查看charts目录中的可视化图表
    
    4. 🛠️  系统管理
       - 修改配置: 编辑 referral_system.py
       - 查看日志: 检查控制台输出
       - 停止服务: Ctrl+C
    
    5. 📱 移动端访问
       - 系统支持响应式设计
       - 可在手机浏览器中正常使用
    
    💡 提示:
    - 系统使用SQLite数据库，数据持久化保存
    - 所有API接口都支持CORS跨域访问
    - 可以随时添加更多用户和数据进行测试
    """
    print(guide)

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装依赖包")
        return
    
    # 初始化数据库
    system = init_database()
    if not system:
        print("\n❌ 数据库初始化失败")
        return
    
    # 生成演示数据
    if not generate_demo_data(system):
        print("\n❌ 演示数据生成失败")
        return
    
    # 启动API服务器
    api_process = start_api_server()
    if not api_process:
        print("\n❌ API服务器启动失败")
        return
    
    # 生成分析报告
    generate_analytics_report()
    
    # 显示使用指南
    show_usage_guide()
    
    print("\n🎉 系统启动完成！")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 保持服务运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        if api_process:
            api_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()