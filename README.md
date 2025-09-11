# 人脸识别和活体检测系统

这是一个基于Python和GPU的人脸识别和活体检测系统，支持张嘴检测和眨眼检测。

## 功能特性

- ✅ **人脸检测**: 使用MediaPipe和dlib双重检测
- ✅ **眨眼检测**: 基于眼睛纵横比(EAR)的实时眨眼检测
- ✅ **张嘴检测**: 基于嘴部纵横比(MAR)的实时张嘴检测
- ✅ **GPU加速**: 支持TensorFlow GPU加速
- ✅ **实时处理**: 支持摄像头实时检测
- ✅ **多模型支持**: MediaPipe + dlib双重保障

## 技术栈

- **OpenCV**: 图像处理和摄像头操作
- **MediaPipe**: Google的人脸检测和关键点提取
- **dlib**: 传统计算机视觉库，作为备用检测器
- **TensorFlow**: GPU加速支持
- **NumPy**: 数值计算
- **SciPy**: 距离计算

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 实时摄像头检测

```bash
python face_liveness_detection.py
```

### 2. 运行测试

```bash
python test_liveness_detection.py
```

### 3. 在代码中使用

```python
from face_liveness_detection import FaceLivenessDetector

# 创建检测器
detector = FaceLivenessDetector(use_gpu=True)

# 检测单张图像
import cv2
image = cv2.imread("your_image.jpg")
results = detector.detect_liveness(image)

print(f"人脸检测: {results['face_detected']}")
print(f"眨眼检测: {results['blink_detected']}")
print(f"张嘴检测: {results['mouth_open_detected']}")
```

## 检测原理

### 眨眼检测 (EAR - Eye Aspect Ratio)

眨眼检测基于眼睛纵横比(EAR)算法：

```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
```

其中p1-p6是眼睛关键点的坐标。当EAR低于阈值时，表示眼睛闭合。

### 张嘴检测 (MAR - Mouth Aspect Ratio)

张嘴检测基于嘴部纵横比(MAR)算法：

```
MAR = (|p2-p10| + |p4-p8|) / (2 * |p1-p7|)
```

其中p1-p10是嘴部关键点的坐标。当MAR高于阈值时，表示嘴巴张开。

## 参数调优

可以在`FaceLivenessDetector`类中调整以下参数：

```python
# 眨眼检测参数
self.EAR_THRESHOLD = 0.25  # 眼睛纵横比阈值
self.EAR_CONSECUTIVE_FRAMES = 3  # 连续帧数

# 张嘴检测参数
self.MAR_THRESHOLD = 0.5  # 嘴部纵横比阈值
self.MAR_CONSECUTIVE_FRAMES = 3  # 连续帧数
```

## 性能优化

1. **GPU加速**: 系统自动检测并使用GPU加速
2. **多模型支持**: MediaPipe作为主要检测器，dlib作为备用
3. **实时处理**: 优化的算法确保实时性能

## 系统要求

- Python 3.7+
- OpenCV 4.x
- CUDA支持的GPU (可选)
- 摄像头设备

## 注意事项

1. 首次运行会自动下载dlib预训练模型
2. 确保摄像头权限已开启
3. 在光线充足的环境下效果更佳
4. 建议人脸距离摄像头30-60cm

## 故障排除

### 常见问题

1. **GPU不可用**: 系统会自动回退到CPU模式
2. **摄像头无法打开**: 检查摄像头权限和设备连接
3. **检测精度低**: 调整阈值参数或改善光线条件

### 调试模式

在代码中设置调试模式：

```python
detector = FaceLivenessDetector(use_gpu=True)
# 启用详细日志输出
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。