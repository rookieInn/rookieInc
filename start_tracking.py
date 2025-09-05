#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面埋点系统快速启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否已安装"""
    print("🔍 检查依赖...")
    try:
        import pymongo
        import flask
        import pandas
        import matplotlib
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_mongodb():
    """检查MongoDB是否运行"""
    print("🔍 检查MongoDB连接...")
    try:
        from tracking_models import TrackingDatabase
        db = TrackingDatabase()
        db.close()
        print("✅ MongoDB连接正常")
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        print("请确保MongoDB正在运行，并检查config.ini配置")
        return False

def start_api_server():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    try:
        # 在后台启动API服务器
        process = subprocess.Popen([
            sys.executable, 'tracking_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否启动成功
        if process.poll() is None:
            print("✅ API服务器启动成功")
            print("📊 API地址: http://localhost:5000")
            print("🔍 健康检查: http://localhost:5000/api/health")
            return process
        else:
            print("❌ API服务器启动失败")
            return None
    except Exception as e:
        print(f"❌ 启动API服务器失败: {e}")
        return None

def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎉 页面埋点系统启动完成！")
    print("="*60)
    
    print("\n📋 使用步骤：")
    print("1. 打开浏览器访问: http://localhost:5000/api/health")
    print("2. 在HTML页面中引入 tracking_sdk.js")
    print("3. 运行演示页面: 打开 demo.html")
    print("4. 查看数据分析: python tracking_example.py")
    
    print("\n📚 重要文件：")
    print("- API服务: tracking_api.py")
    print("- 前端SDK: tracking_sdk.js")
    print("- 数据分析: tracking_analytics.py")
    print("- 使用示例: tracking_example.py")
    print("- 演示页面: demo.html")
    print("- 详细文档: TRACKING_README.md")
    
    print("\n🔧 配置说明：")
    print("- MongoDB配置: 编辑 config.ini 中的 [mongodb] 部分")
    print("- API配置: 编辑 config.ini 中的 [tracking_api] 部分")
    
    print("\n📊 数据分析命令：")
    print("- 模拟数据: python tracking_example.py (选择选项1)")
    print("- 数据分析: python tracking_example.py (选择选项2)")
    print("- 生成报告: python tracking_analytics.py")

def main():
    """主函数"""
    print("🚀 页面埋点系统快速启动")
    print("="*40)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查MongoDB
    if not check_mongodb():
        return
    
    # 启动API服务器
    api_process = start_api_server()
    if not api_process:
        return
    
    # 显示使用说明
    show_usage()
    
    print("\n⏹️  按 Ctrl+C 停止服务器")
    
    try:
        # 保持程序运行
        api_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务器...")
        api_process.terminate()
        api_process.wait()
        print("✅ 服务器已停止")

if __name__ == '__main__':
    main()