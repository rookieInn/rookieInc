#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸识别和活体检测系统
支持张嘴检测、眨眼检测，使用GPU加速
"""

import cv2
import numpy as np
import dlib
import mediapipe as mp
from scipy.spatial import distance as dist
import tensorflow as tf
from typing import Tuple, List, Optional
import time
import os

class FaceLivenessDetector:
    """人脸活体检测器"""
    
    def __init__(self, use_gpu: bool = True):
        """
        初始化检测器
        
        Args:
            use_gpu: 是否使用GPU加速
        """
        self.use_gpu = use_gpu
        self.setup_gpu()
        self.setup_models()
        
        # 眨眼检测参数
        self.EAR_THRESHOLD = 0.25  # 眼睛纵横比阈值
        self.EAR_CONSECUTIVE_FRAMES = 3  # 连续帧数
        
        # 张嘴检测参数
        self.MAR_THRESHOLD = 0.5  # 嘴部纵横比阈值
        self.MAR_CONSECUTIVE_FRAMES = 3  # 连续帧数
        
        # 状态跟踪
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.total_mouth_opens = 0
        
    def setup_gpu(self):
        """设置GPU配置"""
        if self.use_gpu:
            # 配置TensorFlow使用GPU
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    print(f"GPU配置成功: 检测到 {len(gpus)} 个GPU")
                except RuntimeError as e:
                    print(f"GPU配置失败: {e}")
                    self.use_gpu = False
            else:
                print("未检测到GPU，使用CPU模式")
                self.use_gpu = False
    
    def setup_models(self):
        """初始化所有模型"""
        # 初始化MediaPipe人脸检测
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 创建检测器实例
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 初始化dlib人脸检测器（备用）
        predictor_path = self.download_dlib_predictor()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        
        print("所有模型初始化完成")
    
    def download_dlib_predictor(self) -> str:
        """下载dlib预训练模型"""
        predictor_path = "/workspace/shape_predictor_68_face_landmarks.dat"
        if not os.path.exists(predictor_path):
            print("正在下载dlib预训练模型...")
            import urllib.request
            url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
            compressed_path = predictor_path + ".bz2"
            urllib.request.urlretrieve(url, compressed_path)
            
            import bz2
            with bz2.BZ2File(compressed_path, 'rb') as source_file:
                with open(predictor_path, 'wb') as target_file:
                    target_file.write(source_file.read())
            
            os.remove(compressed_path)
            print("dlib模型下载完成")
        
        return predictor_path
    
    def calculate_ear(self, eye_landmarks: np.ndarray) -> float:
        """
        计算眼睛纵横比 (Eye Aspect Ratio)
        
        Args:
            eye_landmarks: 眼睛关键点坐标
            
        Returns:
            眼睛纵横比
        """
        # 计算垂直距离
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        
        # 计算水平距离
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        
        # 计算EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_mar(self, mouth_landmarks: np.ndarray) -> float:
        """
        计算嘴部纵横比 (Mouth Aspect Ratio)
        
        Args:
            mouth_landmarks: 嘴部关键点坐标
            
        Returns:
            嘴部纵横比
        """
        # 计算垂直距离
        A = dist.euclidean(mouth_landmarks[2], mouth_landmarks[10])
        B = dist.euclidean(mouth_landmarks[4], mouth_landmarks[8])
        
        # 计算水平距离
        C = dist.euclidean(mouth_landmarks[0], mouth_landmarks[6])
        
        # 计算MAR
        mar = (A + B) / (2.0 * C)
        return mar
    
    def get_face_landmarks_mediapipe(self, image: np.ndarray) -> Optional[dict]:
        """
        使用MediaPipe获取人脸关键点
        
        Args:
            image: 输入图像
            
        Returns:
            包含关键点的字典
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return None
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # 提取关键点坐标
        h, w = image.shape[:2]
        landmarks = []
        for landmark in face_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            landmarks.append([x, y])
        
        landmarks = np.array(landmarks)
        
        # 定义关键点索引（MediaPipe 468个点）
        # 左眼关键点
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        # 右眼关键点
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        # 嘴部关键点
        mouth_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        
        return {
            'left_eye': landmarks[left_eye_indices],
            'right_eye': landmarks[right_eye_indices],
            'mouth': landmarks[mouth_indices],
            'all_landmarks': landmarks
        }
    
    def get_face_landmarks_dlib(self, image: np.ndarray) -> Optional[dict]:
        """
        使用dlib获取人脸关键点
        
        Args:
            image: 输入图像
            
        Returns:
            包含关键点的字典
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return None
        
        face = faces[0]
        landmarks = self.predictor(gray, face)
        
        # 转换为numpy数组
        points = np.array([[p.x, p.y] for p in landmarks.parts()])
        
        # 定义关键点索引（dlib 68个点）
        # 左眼关键点 (36-41)
        left_eye_indices = list(range(36, 42))
        # 右眼关键点 (42-47)
        right_eye_indices = list(range(42, 48))
        # 嘴部关键点 (48-67)
        mouth_indices = list(range(48, 68))
        
        return {
            'left_eye': points[left_eye_indices],
            'right_eye': points[right_eye_indices],
            'mouth': points[mouth_indices],
            'all_landmarks': points
        }
    
    def detect_blink(self, landmarks: dict) -> bool:
        """
        检测眨眼
        
        Args:
            landmarks: 人脸关键点
            
        Returns:
            是否检测到眨眼
        """
        left_ear = self.calculate_ear(landmarks['left_eye'])
        right_ear = self.calculate_ear(landmarks['right_eye'])
        
        # 使用双眼平均EAR
        ear = (left_ear + right_ear) / 2.0
        
        # 检测眨眼
        if ear < self.EAR_THRESHOLD:
            self.ear_counter += 1
        else:
            if self.ear_counter >= self.EAR_CONSECUTIVE_FRAMES:
                self.total_blinks += 1
                self.ear_counter = 0
                return True
            self.ear_counter = 0
        
        return False
    
    def detect_mouth_open(self, landmarks: dict) -> bool:
        """
        检测张嘴
        
        Args:
            landmarks: 人脸关键点
            
        Returns:
            是否检测到张嘴
        """
        mar = self.calculate_mar(landmarks['mouth'])
        
        # 检测张嘴
        if mar > self.MAR_THRESHOLD:
            self.mar_counter += 1
        else:
            if self.mar_counter >= self.MAR_CONSECUTIVE_FRAMES:
                self.total_mouth_opens += 1
                self.mar_counter = 0
                return True
            self.mar_counter = 0
        
        return False
    
    def detect_liveness(self, image: np.ndarray) -> dict:
        """
        检测活体特征
        
        Args:
            image: 输入图像
            
        Returns:
            检测结果字典
        """
        # 优先使用MediaPipe，如果失败则使用dlib
        landmarks = self.get_face_landmarks_mediapipe(image)
        if landmarks is None:
            landmarks = self.get_face_landmarks_dlib(image)
        
        if landmarks is None:
            return {
                'face_detected': False,
                'blink_detected': False,
                'mouth_open_detected': False,
                'total_blinks': self.total_blinks,
                'total_mouth_opens': self.total_mouth_opens
            }
        
        # 检测眨眼和张嘴
        blink_detected = self.detect_blink(landmarks)
        mouth_open_detected = self.detect_mouth_open(landmarks)
        
        return {
            'face_detected': True,
            'blink_detected': blink_detected,
            'mouth_open_detected': mouth_open_detected,
            'total_blinks': self.total_blinks,
            'total_mouth_opens': self.total_mouth_opens,
            'landmarks': landmarks
        }
    
    def draw_landmarks(self, image: np.ndarray, landmarks: dict) -> np.ndarray:
        """
        在图像上绘制关键点
        
        Args:
            image: 输入图像
            landmarks: 人脸关键点
            
        Returns:
            绘制了关键点的图像
        """
        result_image = image.copy()
        
        # 绘制眼睛关键点
        for point in landmarks['left_eye']:
            cv2.circle(result_image, tuple(point), 2, (0, 255, 0), -1)
        for point in landmarks['right_eye']:
            cv2.circle(result_image, tuple(point), 2, (0, 255, 0), -1)
        
        # 绘制嘴部关键点
        for point in landmarks['mouth']:
            cv2.circle(result_image, tuple(point), 2, (255, 0, 0), -1)
        
        return result_image
    
    def reset_counters(self):
        """重置计数器"""
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.total_mouth_opens = 0


def main():
    """主函数 - 实时检测示例"""
    # 创建检测器
    detector = FaceLivenessDetector(use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("人脸活体检测系统启动")
    print("按 'q' 键退出")
    print("按 'r' 键重置计数器")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 水平翻转图像（镜像效果）
        frame = cv2.flip(frame, 1)
        
        # 检测活体特征
        results = detector.detect_liveness(frame)
        
        # 在图像上显示结果
        if results['face_detected']:
            # 绘制关键点
            frame = detector.draw_landmarks(frame, results['landmarks'])
            
            # 显示状态信息
            cv2.putText(frame, f"Blinks: {results['total_blinks']}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Mouth Opens: {results['total_mouth_opens']}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示检测状态
            if results['blink_detected']:
                cv2.putText(frame, "BLINK DETECTED!", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if results['mouth_open_detected']:
                cv2.putText(frame, "MOUTH OPEN DETECTED!", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No Face Detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示图像
        cv2.imshow('Face Liveness Detection', frame)
        
        # 处理按键
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            detector.reset_counters()
            print("计数器已重置")
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    print("检测完成")


if __name__ == "__main__":
    main()