#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸活体检测测试脚本
"""

import cv2
import numpy as np
import os
from face_liveness_detection import FaceLivenessDetector
import time

def test_image_detection(image_path: str):
    """测试单张图像的活体检测"""
    print(f"测试图像: {image_path}")
    
    # 创建检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return
    
    # 检测活体特征
    results = detector.detect_liveness(image)
    
    # 显示结果
    print(f"人脸检测: {'成功' if results['face_detected'] else '失败'}")
    print(f"眨眼检测: {'是' if results['blink_detected'] else '否'}")
    print(f"张嘴检测: {'是' if results['mouth_open_detected'] else '否'}")
    print(f"总眨眼次数: {results['total_blinks']}")
    print(f"总张嘴次数: {results['total_mouth_opens']}")
    
    # 绘制结果
    if results['face_detected']:
        result_image = detector.draw_landmarks(image, results['landmarks'])
        
        # 添加文本信息
        cv2.putText(result_image, f"Blinks: {results['total_blinks']}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(result_image, f"Mouth Opens: {results['total_mouth_opens']}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 保存结果图像
        output_path = f"result_{os.path.basename(image_path)}"
        cv2.imwrite(output_path, result_image)
        print(f"结果图像已保存: {output_path}")
        
        # 显示图像
        cv2.imshow('Test Result', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def test_video_detection(video_path: str, duration: int = 10):
    """测试视频文件的活体检测"""
    print(f"测试视频: {video_path} (时长: {duration}秒)")
    
    # 创建检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        return
    
    # 获取视频信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    max_frames = min(fps * duration, total_frames)
    
    print(f"视频FPS: {fps}, 总帧数: {total_frames}")
    print(f"将处理前 {max_frames} 帧")
    
    frame_count = 0
    start_time = time.time()
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 检测活体特征
        results = detector.detect_liveness(frame)
        
        # 显示进度
        if frame_count % (fps * 2) == 0:  # 每2秒显示一次
            print(f"处理进度: {frame_count}/{max_frames} 帧")
            print(f"当前眨眼次数: {results['total_blinks']}")
            print(f"当前张嘴次数: {results['total_mouth_opens']}")
        
        frame_count += 1
    
    # 最终结果
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n视频检测完成:")
    print(f"处理时间: {processing_time:.2f}秒")
    print(f"处理帧数: {frame_count}")
    print(f"平均FPS: {frame_count/processing_time:.2f}")
    print(f"总眨眼次数: {detector.total_blinks}")
    print(f"总张嘴次数: {detector.total_mouth_opens}")
    
    cap.release()

def test_camera_detection(duration: int = 30):
    """测试摄像头实时检测"""
    print(f"开始摄像头检测 (时长: {duration}秒)")
    
    # 创建检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start_time = time.time()
    frame_count = 0
    
    print("按 'q' 键提前退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 水平翻转图像
        frame = cv2.flip(frame, 1)
        
        # 检测活体特征
        results = detector.detect_liveness(frame)
        
        # 显示状态信息
        if results['face_detected']:
            # 绘制关键点
            frame = detector.draw_landmarks(frame, results['landmarks'])
            
            # 显示计数
            cv2.putText(frame, f"Blinks: {results['total_blinks']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Mouth Opens: {results['total_mouth_opens']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示检测状态
            if results['blink_detected']:
                cv2.putText(frame, "BLINK!", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if results['mouth_open_detected']:
                cv2.putText(frame, "MOUTH OPEN!", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No Face", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示处理时间
        current_time = time.time()
        elapsed = current_time - start_time
        cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 显示图像
        cv2.imshow('Live Detection Test', frame)
        
        frame_count += 1
        
        # 检查退出条件
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or elapsed >= duration:
            break
    
    # 最终结果
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n摄像头检测完成:")
    print(f"总时间: {total_time:.2f}秒")
    print(f"总帧数: {frame_count}")
    print(f"平均FPS: {frame_count/total_time:.2f}")
    print(f"总眨眼次数: {detector.total_blinks}")
    print(f"总张嘴次数: {detector.total_mouth_opens}")
    
    cap.release()
    cv2.destroyAllWindows()

def create_test_image():
    """创建测试图像"""
    # 创建一个简单的测试图像
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    image.fill(128)  # 灰色背景
    
    # 添加一些文本
    cv2.putText(image, "Test Image for Face Detection", (50, 240), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(image, "Please place your face in front of camera", (50, 280), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imwrite("test_image.jpg", image)
    print("测试图像已创建: test_image.jpg")

def main():
    """主测试函数"""
    print("=== 人脸活体检测测试 ===")
    
    # 创建测试图像
    create_test_image()
    
    # 测试图像检测
    print("\n1. 测试图像检测")
    test_image_detection("test_image.jpg")
    
    # 测试摄像头检测
    print("\n2. 测试摄像头检测 (10秒)")
    try:
        test_camera_detection(10)
    except KeyboardInterrupt:
        print("用户中断测试")
    
    # 如果有视频文件，可以测试视频检测
    # print("\n3. 测试视频检测")
    # test_video_detection("test_video.mp4", 10)
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()