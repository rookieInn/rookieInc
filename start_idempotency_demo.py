#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
幂等性演示启动脚本
启动Redis、Flask和FastAPI服务进行演示
"""

import subprocess
import time
import signal
import sys
import os
import threading
from pathlib import Path

def check_redis():
    """检查Redis是否运行"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis服务正常运行")
        return True
    except Exception as e:
        print(f"❌ Redis服务未运行: {e}")
        return False

def start_redis():
    """启动Redis服务"""
    try:
        # 尝试启动Redis
        subprocess.run(['redis-server', '--daemonize', 'yes'], check=True)
        time.sleep(2)
        if check_redis():
            print("✅ Redis服务启动成功")
            return True
    except Exception as e:
        print(f"⚠️ 无法启动Redis服务: {e}")
        print("请手动启动Redis服务或安装Redis")
        return False

def start_flask_app():
    """启动Flask应用"""
    try:
        print("🚀 启动Flask应用...")
        process = subprocess.Popen([
            sys.executable, 'tracking_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"❌ Flask应用启动失败: {e}")
        return None

def start_fastapi_app():
    """启动FastAPI应用"""
    try:
        print("🚀 启动FastAPI应用...")
        os.chdir('travel_route_planner')
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chdir('..')
        return process
    except Exception as e:
        print(f"❌ FastAPI应用启动失败: {e}")
        return None

def run_tests():
    """运行测试"""
    print("\n🧪 运行幂等性测试...")
    try:
        subprocess.run([sys.executable, 'test_idempotency.py'], check=True)
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")

def cleanup(processes):
    """清理进程"""
    print("\n🧹 清理进程...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    """主函数"""
    print("🎯 幂等性演示启动脚本")
    print("=" * 50)
    
    # 检查Redis
    if not check_redis():
        print("尝试启动Redis服务...")
        if not start_redis():
            print("请手动安装并启动Redis服务")
            return
    
    processes = []
    
    try:
        # 启动Flask应用
        flask_process = start_flask_app()
        if flask_process:
            processes.append(flask_process)
            time.sleep(3)
        
        # 启动FastAPI应用
        fastapi_process = start_fastapi_app()
        if fastapi_process:
            processes.append(fastapi_process)
            time.sleep(3)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 运行测试
        run_tests()
        
        print("\n✅ 演示完成！")
        print("服务正在运行，按Ctrl+C停止")
        
        # 保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        cleanup(processes)
        print("👋 演示结束")

if __name__ == "__main__":
    main()