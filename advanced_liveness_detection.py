#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级人脸活体检测系统
包含更多检测算法和优化功能
"""

import cv2
import numpy as np
import dlib
import mediapipe as mp
from scipy.spatial import distance as dist
import tensorflow as tf
from typing import Tuple, List, Optional, Dict
import time
import os
import json
from dataclasses import dataclass
from enum import Enum

class DetectionMethod(Enum):
    """检测方法枚举"""
    MEDIAPIPE = "mediapipe"
    DLIB = "dlib"
    HYBRID = "hybrid"

@dataclass
class DetectionConfig:
    """检测配置"""
    # 眨眼检测参数
    ear_threshold: float = 0.25
    ear_consecutive_frames: int = 3
    ear_smoothing_factor: float = 0.1
    
    # 张嘴检测参数
    mar_threshold: float = 0.5
    mar_consecutive_frames: int = 3
    mar_smoothing_factor: float = 0.1
    
    # 头部姿态检测参数
    head_pose_threshold: float = 15.0  # 度
    
    # 检测方法
    detection_method: DetectionMethod = DetectionMethod.HYBRID
    
    # 性能参数
    skip_frames: int = 1  # 跳帧处理
    confidence_threshold: float = 0.5

class AdvancedFaceLivenessDetector:
    """高级人脸活体检测器"""
    
    def __init__(self, config: DetectionConfig = None, use_gpu: bool = True):
        """
        初始化检测器
        
        Args:
            config: 检测配置
            use_gpu: 是否使用GPU加速
        """
        self.config = config or DetectionConfig()
        self.use_gpu = use_gpu
        self.setup_gpu()
        self.setup_models()
        
        # 状态跟踪
        self.ear_history = []
        self.mar_history = []
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.total_mouth_opens = 0
        self.frame_count = 0
        
        # 性能统计
        self.performance_stats = {
            'total_frames': 0,
            'detection_time': 0,
            'fps': 0
        }
        
    def setup_gpu(self):
        """设置GPU配置"""
        if self.use_gpu:
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
        # MediaPipe模型
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=self.config.confidence_threshold
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=self.config.confidence_threshold,
            min_tracking_confidence=self.config.confidence_threshold
        )
        
        # dlib模型
        predictor_path = self.download_dlib_predictor()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        
        print("高级模型初始化完成")
    
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
    
    def calculate_ear_smoothed(self, eye_landmarks: np.ndarray) -> float:
        """计算平滑的眼睛纵横比"""
        # 计算垂直距离
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        
        # 计算水平距离
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        
        # 计算EAR
        ear = (A + B) / (2.0 * C)
        
        # 平滑处理
        self.ear_history.append(ear)
        if len(self.ear_history) > 10:  # 保持最近10帧的历史
            self.ear_history.pop(0)
        
        # 使用指数移动平均
        if len(self.ear_history) > 1:
            smoothed_ear = self.ear_history[-1] * (1 - self.config.ear_smoothing_factor) + \
                          np.mean(self.ear_history[:-1]) * self.config.ear_smoothing_factor
        else:
            smoothed_ear = ear
        
        return smoothed_ear
    
    def calculate_mar_smoothed(self, mouth_landmarks: np.ndarray) -> float:
        """计算平滑的嘴部纵横比"""
        # 计算垂直距离
        A = dist.euclidean(mouth_landmarks[2], mouth_landmarks[10])
        B = dist.euclidean(mouth_landmarks[4], mouth_landmarks[8])
        
        # 计算水平距离
        C = dist.euclidean(mouth_landmarks[0], mouth_landmarks[6])
        
        # 计算MAR
        mar = (A + B) / (2.0 * C)
        
        # 平滑处理
        self.mar_history.append(mar)
        if len(self.mar_history) > 10:  # 保持最近10帧的历史
            self.mar_history.pop(0)
        
        # 使用指数移动平均
        if len(self.mar_history) > 1:
            smoothed_mar = self.mar_history[-1] * (1 - self.config.mar_smoothing_factor) + \
                          np.mean(self.mar_history[:-1]) * self.config.mar_smoothing_factor
        else:
            smoothed_mar = mar
        
        return smoothed_mar
    
    def calculate_head_pose(self, landmarks: np.ndarray) -> Dict[str, float]:
        """计算头部姿态角度"""
        # 使用关键点计算头部姿态
        # 这里使用简化的方法，实际应用中可以使用更精确的3D姿态估计
        
        # 获取关键点
        nose_tip = landmarks[30]  # 鼻尖
        left_eye = landmarks[36]  # 左眼
        right_eye = landmarks[45]  # 右眼
        mouth_left = landmarks[48]  # 嘴角左
        mouth_right = landmarks[54]  # 嘴角右
        
        # 计算水平角度
        eye_center = (left_eye + right_eye) / 2
        mouth_center = (mouth_left + mouth_right) / 2
        
        # 简化的角度计算
        horizontal_angle = np.arctan2(nose_tip[0] - eye_center[0], 
                                    nose_tip[1] - eye_center[1]) * 180 / np.pi
        
        vertical_angle = np.arctan2(nose_tip[1] - mouth_center[1], 
                                  nose_tip[0] - mouth_center[0]) * 180 / np.pi
        
        return {
            'horizontal': abs(horizontal_angle),
            'vertical': abs(vertical_angle),
            'total': np.sqrt(horizontal_angle**2 + vertical_angle**2)
        }
    
    def get_face_landmarks_mediapipe(self, image: np.ndarray) -> Optional[dict]:
        """使用MediaPipe获取人脸关键点"""
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
        
        # 定义关键点索引
        left_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        right_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        mouth_indices = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        
        return {
            'left_eye': landmarks[left_eye_indices],
            'right_eye': landmarks[right_eye_indices],
            'mouth': landmarks[mouth_indices],
            'all_landmarks': landmarks
        }
    
    def get_face_landmarks_dlib(self, image: np.ndarray) -> Optional[dict]:
        """使用dlib获取人脸关键点"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return None
        
        face = faces[0]
        landmarks = self.predictor(gray, face)
        
        # 转换为numpy数组
        points = np.array([[p.x, p.y] for p in landmarks.parts()])
        
        # 定义关键点索引
        left_eye_indices = list(range(36, 42))
        right_eye_indices = list(range(42, 48))
        mouth_indices = list(range(48, 68))
        
        return {
            'left_eye': points[left_eye_indices],
            'right_eye': points[right_eye_indices],
            'mouth': points[mouth_indices],
            'all_landmarks': points
        }
    
    def detect_liveness_advanced(self, image: np.ndarray) -> dict:
        """高级活体检测"""
        start_time = time.time()
        
        # 跳帧处理
        if self.frame_count % (self.config.skip_frames + 1) != 0:
            self.frame_count += 1
            return self.get_last_result()
        
        # 选择检测方法
        landmarks = None
        if self.config.detection_method == DetectionMethod.MEDIAPIPE:
            landmarks = self.get_face_landmarks_mediapipe(image)
        elif self.config.detection_method == DetectionMethod.DLIB:
            landmarks = self.get_face_landmarks_dlib(image)
        else:  # HYBRID
            landmarks = self.get_face_landmarks_mediapipe(image)
            if landmarks is None:
                landmarks = self.get_face_landmarks_dlib(image)
        
        if landmarks is None:
            result = {
                'face_detected': False,
                'blink_detected': False,
                'mouth_open_detected': False,
                'head_pose_valid': False,
                'total_blinks': self.total_blinks,
                'total_mouth_opens': self.total_mouth_opens,
                'performance_stats': self.performance_stats
            }
            self.last_result = result
            return result
        
        # 检测眨眼
        left_ear = self.calculate_ear_smoothed(landmarks['left_eye'])
        right_ear = self.calculate_ear_smoothed(landmarks['right_eye'])
        ear = (left_ear + right_ear) / 2.0
        
        blink_detected = False
        if ear < self.config.ear_threshold:
            self.ear_counter += 1
        else:
            if self.ear_counter >= self.config.ear_consecutive_frames:
                self.total_blinks += 1
                self.ear_counter = 0
                blink_detected = True
            self.ear_counter = 0
        
        # 检测张嘴
        mar = self.calculate_mar_smoothed(landmarks['mouth'])
        mouth_open_detected = False
        if mar > self.config.mar_threshold:
            self.mar_counter += 1
        else:
            if self.mar_counter >= self.config.mar_consecutive_frames:
                self.total_mouth_opens += 1
                self.mar_counter = 0
                mouth_open_detected = True
            self.mar_counter = 0
        
        # 检测头部姿态
        head_pose = self.calculate_head_pose(landmarks['all_landmarks'])
        head_pose_valid = head_pose['total'] < self.config.head_pose_threshold
        
        # 更新性能统计
        detection_time = time.time() - start_time
        self.performance_stats['total_frames'] += 1
        self.performance_stats['detection_time'] += detection_time
        self.performance_stats['fps'] = self.performance_stats['total_frames'] / \
                                      self.performance_stats['detection_time']
        
        result = {
            'face_detected': True,
            'blink_detected': blink_detected,
            'mouth_open_detected': mouth_open_detected,
            'head_pose_valid': head_pose_valid,
            'head_pose': head_pose,
            'ear': ear,
            'mar': mar,
            'total_blinks': self.total_blinks,
            'total_mouth_opens': self.total_mouth_opens,
            'landmarks': landmarks,
            'performance_stats': self.performance_stats.copy()
        }
        
        self.last_result = result
        self.frame_count += 1
        return result
    
    def get_last_result(self) -> dict:
        """获取上一次检测结果"""
        if hasattr(self, 'last_result'):
            return self.last_result
        return {
            'face_detected': False,
            'blink_detected': False,
            'mouth_open_detected': False,
            'head_pose_valid': False,
            'total_blinks': self.total_blinks,
            'total_mouth_opens': self.total_mouth_opens,
            'performance_stats': self.performance_stats
        }
    
    def save_config(self, filepath: str):
        """保存配置到文件"""
        config_dict = {
            'ear_threshold': self.config.ear_threshold,
            'ear_consecutive_frames': self.config.ear_consecutive_frames,
            'ear_smoothing_factor': self.config.ear_smoothing_factor,
            'mar_threshold': self.config.mar_threshold,
            'mar_consecutive_frames': self.config.mar_consecutive_frames,
            'mar_smoothing_factor': self.config.mar_smoothing_factor,
            'head_pose_threshold': self.config.head_pose_threshold,
            'detection_method': self.config.detection_method.value,
            'skip_frames': self.config.skip_frames,
            'confidence_threshold': self.config.confidence_threshold
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def load_config(self, filepath: str):
        """从文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        self.config.ear_threshold = config_dict.get('ear_threshold', 0.25)
        self.config.ear_consecutive_frames = config_dict.get('ear_consecutive_frames', 3)
        self.config.ear_smoothing_factor = config_dict.get('ear_smoothing_factor', 0.1)
        self.config.mar_threshold = config_dict.get('mar_threshold', 0.5)
        self.config.mar_consecutive_frames = config_dict.get('mar_consecutive_frames', 3)
        self.config.mar_smoothing_factor = config_dict.get('mar_smoothing_factor', 0.1)
        self.config.head_pose_threshold = config_dict.get('head_pose_threshold', 15.0)
        self.config.detection_method = DetectionMethod(config_dict.get('detection_method', 'hybrid'))
        self.config.skip_frames = config_dict.get('skip_frames', 1)
        self.config.confidence_threshold = config_dict.get('confidence_threshold', 0.5)
    
    def reset_counters(self):
        """重置所有计数器"""
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.total_mouth_opens = 0
        self.frame_count = 0
        self.ear_history.clear()
        self.mar_history.clear()
        self.performance_stats = {
            'total_frames': 0,
            'detection_time': 0,
            'fps': 0
        }


def main():
    """主函数 - 高级检测示例"""
    # 创建高级配置
    config = DetectionConfig(
        ear_threshold=0.25,
        mar_threshold=0.5,
        detection_method=DetectionMethod.HYBRID,
        skip_frames=1
    )
    
    # 创建高级检测器
    detector = AdvancedFaceLivenessDetector(config=config, use_gpu=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("高级人脸活体检测系统启动")
    print("按 'q' 键退出")
    print("按 'r' 键重置计数器")
    print("按 's' 键保存配置")
    print("按 'l' 键加载配置")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 水平翻转图像
        frame = cv2.flip(frame, 1)
        
        # 高级活体检测
        results = detector.detect_liveness_advanced(frame)
        
        # 在图像上显示结果
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
        
        # 显示图像
        cv2.imshow('Advanced Face Liveness Detection', frame)
        
        # 处理按键
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            detector.reset_counters()
            print("计数器已重置")
        elif key == ord('s'):
            detector.save_config('detection_config.json')
            print("配置已保存")
        elif key == ord('l'):
            try:
                detector.load_config('detection_config.json')
                print("配置已加载")
            except FileNotFoundError:
                print("配置文件不存在")
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    print("检测完成")


if __name__ == "__main__":
    main()