#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸活体检测演示脚本
展示如何使用不同功能
"""

import cv2
import numpy as np
import time
from face_liveness_detection import FaceLivenessDetector
from advanced_liveness_detection import AdvancedFaceLivenessDetector, DetectionConfig, DetectionMethod

def demo_basic_detection():
    """基础检测演示"""
    print("=== 基础人脸活体检测演示 ===")
    
    # 创建基础检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("基础检测模式启动")
    print("按 'q' 键退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # 检测活体特征
        results = detector.detect_liveness(frame)
        
        # 显示结果
        if results['face_detected']:
            # 绘制关键点
            frame = detector.draw_landmarks(frame, results['landmarks'])
            
            # 显示状态
            cv2.putText(frame, f"Blinks: {results['total_blinks']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Mouth Opens: {results['total_mouth_opens']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if results['blink_detected']:
                cv2.putText(frame, "BLINK!", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if results['mouth_open_detected']:
                cv2.putText(frame, "MOUTH OPEN!", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No Face Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('Basic Face Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def demo_advanced_detection():
    """高级检测演示"""
    print("=== 高级人脸活体检测演示 ===")
    
    # 创建高级配置
    config = DetectionConfig(
        ear_threshold=0.25,
        mar_threshold=0.5,
        detection_method=DetectionMethod.HYBRID,
        skip_frames=1,
        head_pose_threshold=20.0
    )
    
    # 创建高级检测器
    detector = AdvancedFaceLivenessDetector(config=config, use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("高级检测模式启动")
    print("按 'q' 键退出")
    print("按 'r' 键重置计数器")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # 高级活体检测
        results = detector.detect_liveness_advanced(frame)
        
        # 显示结果
        if results['face_detected']:
            # 显示状态信息
            cv2.putText(frame, f"Blinks: {results['total_blinks']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Mouth Opens: {results['total_mouth_opens']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {results['performance_stats']['fps']:.1f}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示检测状态
            if results['blink_detected']:
                cv2.putText(frame, "BLINK!", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if results['mouth_open_detected']:
                cv2.putText(frame, "MOUTH OPEN!", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if not results['head_pose_valid']:
                cv2.putText(frame, "HEAD POSE INVALID!", (10, 180), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 显示数值信息
            cv2.putText(frame, f"EAR: {results.get('ear', 0):.3f}", 
                       (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"MAR: {results.get('mar', 0):.3f}", 
                       (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "No Face Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('Advanced Face Detection', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            detector.reset_counters()
            print("计数器已重置")
    
    cap.release()
    cv2.destroyAllWindows()

def demo_image_detection():
    """图像检测演示"""
    print("=== 图像检测演示 ===")
    
    # 创建检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 创建测试图像
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    image.fill(128)
    
    cv2.putText(image, "Test Image for Face Detection", (50, 240), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "Please place your face in front of camera", (50, 280), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 检测
    results = detector.detect_liveness(image)
    
    print(f"人脸检测: {'成功' if results['face_detected'] else '失败'}")
    print(f"眨眼检测: {'是' if results['blink_detected'] else '否'}")
    print(f"张嘴检测: {'是' if results['mouth_open_detected'] else '否'}")
    
    # 保存结果
    cv2.imwrite("test_result.jpg", image)
    print("测试图像已保存: test_result.jpg")

def demo_performance_test():
    """性能测试演示"""
    print("=== 性能测试演示 ===")
    
    # 创建检测器
    detector = AdvancedFaceLivenessDetector(use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("性能测试开始 (10秒)")
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 10:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # 检测
        results = detector.detect_liveness_advanced(frame)
        frame_count += 1
        
        # 显示FPS
        cv2.putText(frame, f"FPS: {results['performance_stats']['fps']:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Frames: {frame_count}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Performance Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n性能测试结果:")
    print(f"总时间: {total_time:.2f}秒")
    print(f"总帧数: {frame_count}")
    print(f"平均FPS: {frame_count/total_time:.2f}")
    print(f"检测器FPS: {results['performance_stats']['fps']:.2f}")
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    """主演示函数"""
    print("人脸活体检测系统演示")
    print("请选择演示模式:")
    print("1. 基础检测演示")
    print("2. 高级检测演示")
    print("3. 图像检测演示")
    print("4. 性能测试演示")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-5): ").strip()
            
            if choice == '1':
                demo_basic_detection()
            elif choice == '2':
                demo_advanced_detection()
            elif choice == '3':
                demo_image_detection()
            elif choice == '4':
                demo_performance_test()
            elif choice == '5':
                print("退出演示")
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