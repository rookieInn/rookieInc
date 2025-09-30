#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分账程序启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_split_bill.txt"
        ])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖包失败: {e}")
        return False

def start_app():
    """启动应用"""
    print("正在启动分账程序...")
    print("=" * 50)
    print("分账程序已启动！")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止程序")
    print("=" * 50)
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:5000')
        except:
            pass
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Flask应用
    try:
        from split_bill_app import app, init_database
        init_database()
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def main():
    """主函数"""
    print("分账程序启动器")
    print("=" * 30)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查依赖文件
    if not Path("requirements_split_bill.txt").exists():
        print("错误: 找不到 requirements_split_bill.txt 文件")
        return
    
    if not Path("split_bill_app.py").exists():
        print("错误: 找不到 split_bill_app.py 文件")
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    # 启动应用
    start_app()

if __name__ == "__main__":
    main()