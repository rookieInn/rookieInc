#!/bin/bash

# 人脸活体检测系统依赖安装脚本

echo "开始安装人脸活体检测系统依赖..."

# 更新包管理器
echo "更新包管理器..."
sudo apt-get update

# 安装Python3和pip
echo "安装Python3和pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# 安装系统依赖
echo "安装系统依赖..."
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv face_detection_env
source face_detection_env/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查GPU支持
echo "检查GPU支持..."
python3 -c "
import tensorflow as tf
print('TensorFlow版本:', tf.__version__)
print('GPU可用:', tf.config.list_physical_devices('GPU'))
"

# 测试OpenCV
echo "测试OpenCV..."
python3 -c "
import cv2
print('OpenCV版本:', cv2.__version__)
print('摄像头测试:', cv2.VideoCapture(0).isOpened())
"

echo "依赖安装完成！"
echo "使用方法："
echo "1. 激活虚拟环境: source face_detection_env/bin/activate"
echo "2. 运行基础检测: python face_liveness_detection.py"
echo "3. 运行高级检测: python advanced_liveness_detection.py"
echo "4. 运行测试: python test_liveness_detection.py"