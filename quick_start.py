#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 一键运行人脸活体检测
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    
    required_packages = [
        'cv2', 'numpy', 'dlib', 'mediapipe', 
        'tensorflow', 'scipy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'numpy':
                import numpy
            elif package == 'dlib':
                import dlib
            elif package == 'mediapipe':
                import mediapipe
            elif package == 'tensorflow':
                import tensorflow
            elif package == 'scipy':
                import scipy
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("所有依赖检查通过!")
    return True

def check_camera():
    """检查摄像头是否可用"""
    print("\n检查摄像头...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ 摄像头可用")
            cap.release()
            return True
        else:
            print("✗ 摄像头不可用")
            return False
    except Exception as e:
        print(f"✗ 摄像头检查失败: {e}")
        return False

def check_gpu():
    """检查GPU是否可用"""
    print("\n检查GPU...")
    
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✓ GPU可用: {len(gpus)} 个GPU")
            return True
        else:
            print("✗ 未检测到GPU，将使用CPU")
            return False
    except Exception as e:
        print(f"✗ GPU检查失败: {e}")
        return False

def run_basic_detection():
    """运行基础检测"""
    print("\n启动基础人脸活体检测...")
    try:
        from face_liveness_detection import main
        main()
    except Exception as e:
        print(f"运行失败: {e}")

def run_advanced_detection():
    """运行高级检测"""
    print("\n启动高级人脸活体检测...")
    try:
        from advanced_liveness_detection import main
        main()
    except Exception as e:
        print(f"运行失败: {e}")

def run_demo():
    """运行演示"""
    print("\n启动演示程序...")
    try:
        from demo import main
        main()
    except Exception as e:
        print(f"运行失败: {e}")

def install_dependencies():
    """安装依赖"""
    print("\n开始安装依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("依赖安装完成!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("人脸活体检测系统 - 快速启动")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n是否要自动安装依赖? (y/n): ", end="")
        if input().lower() == 'y':
            if not install_dependencies():
                print("依赖安装失败，请手动安装")
                return
        else:
            print("请手动安装依赖后重试")
            return
    
    # 检查摄像头
    if not check_camera():
        print("请检查摄像头连接")
        return
    
    # 检查GPU
    gpu_available = check_gpu()
    
    print("\n" + "=" * 50)
    print("系统检查完成!")
    print("=" * 50)
    
    # 选择运行模式
    while True:
        print("\n请选择运行模式:")
        print("1. 基础检测 (简单易用)")
        print("2. 高级检测 (功能完整)")
        print("3. 演示程序 (多种模式)")
        print("4. 退出")
        
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                run_basic_detection()
                break
            elif choice == '2':
                run_advanced_detection()
                break
            elif choice == '3':
                run_demo()
                break
            elif choice == '4':
                print("退出程序")
                break
            else:
                print("无效选择，请重新输入")
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()