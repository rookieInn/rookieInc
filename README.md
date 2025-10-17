# 人脸识别和活体检测系统 + 阿里云图像内容检测

这是一个基于Python和GPU的人脸识别和活体检测系统，支持张嘴检测和眨眼检测。同时集成了阿里云图像内容检测服务，支持多种内容安全检测功能。

## 功能特性

### 人脸识别和活体检测
- ✅ **人脸检测**: 使用MediaPipe和dlib双重检测
- ✅ **眨眼检测**: 基于眼睛纵横比(EAR)的实时眨眼检测
- ✅ **张嘴检测**: 基于嘴部纵横比(MAR)的实时张嘴检测
- ✅ **GPU加速**: 支持TensorFlow GPU加速
- ✅ **实时处理**: 支持摄像头实时检测
- ✅ **多模型支持**: MediaPipe + dlib双重保障

### 阿里云图像内容检测
- ✅ **多类型检测**: 支持色情、暴恐、广告、直播、Logo、OCR、人脸、二维码、场景等检测
- ✅ **批量处理**: 支持单张图像和批量图像检测
- ✅ **目录扫描**: 支持扫描整个目录的图像文件
- ✅ **灵活配置**: 支持自定义检测类型和置信度阈值
- ✅ **结果分析**: 提供详细的检测统计和报告生成
- ✅ **异步支持**: 支持同步和异步检测模式

## 技术栈

### 人脸识别和活体检测
- **OpenCV**: 图像处理和摄像头操作
- **MediaPipe**: Google的人脸检测和关键点提取
- **dlib**: 传统计算机视觉库，作为备用检测器
- **TensorFlow**: GPU加速支持
- **NumPy**: 数值计算
- **SciPy**: 距离计算

### 阿里云图像内容检测
- **阿里云SDK**: 官方Python SDK
- **阿里云内容安全**: 图像内容检测API
- **PIL/Pillow**: 图像处理
- **ConfigParser**: 配置文件管理
- **JSON**: 结果数据格式

## 安装依赖

```bash
pip install -r requirements.txt
```

### 阿里云图像内容检测额外依赖

如果只需要使用人脸识别功能，可以跳过阿里云相关依赖的安装。如果需要使用图像内容检测功能，请确保安装以下依赖：

```bash
pip install aliyun-python-sdk-core aliyun-python-sdk-green aliyun-python-sdk-imageaudit aliyun-python-sdk-viapi
```

## 使用方法

### 人脸识别和活体检测

#### 1. 实时摄像头检测

```bash
python face_liveness_detection.py
```

#### 2. 运行测试

```bash
python test_liveness_detection.py
```

#### 3. 在代码中使用

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

### 阿里云图像内容检测

#### 1. 配置阿里云访问密钥

编辑 `config.ini` 文件，填入您的阿里云访问密钥：

```ini
[aliyun_image_detection]
access_key_id = YOUR_ACCESS_KEY_ID
access_key_secret = YOUR_ACCESS_KEY_SECRET
region = cn-shanghai
detection_types = porn,terrorism,ad
confidence_threshold = 0.8
async_detection = false
```

#### 2. 基本使用

```python
from image_content_detection_service import ImageContentDetectionService

# 创建服务实例
service = ImageContentDetectionService()

# 检测单张图像
result = service.detect_single_image("image.jpg")
print(f"风险等级: {result['summary']['risk_level']}")

# 批量检测
results = service.detect_batch_images(["image1.jpg", "image2.jpg"])

# 检测目录
results = service.detect_directory("./images/")
```

#### 3. 运行演示

```bash
# 创建示例图像并演示
python demo_image_detection.py --create-samples

# 检测单张图像
python demo_image_detection.py --image your_image.jpg

# 批量检测目录
python demo_image_detection.py --directory ./images/

# 演示不同检测类型
python demo_image_detection.py --image your_image.jpg --demo-types

# 演示不同置信度阈值
python demo_image_detection.py --image your_image.jpg --demo-threshold

# 保存检测结果
python demo_image_detection.py --image your_image.jpg --save-results
```

#### 4. 运行测试

```bash
python test_image_detection.py
```

#### 5. 支持的检测类型

- **porn**: 色情内容检测
- **terrorism**: 暴恐内容检测
- **ad**: 广告内容检测
- **live**: 直播内容检测
- **logo**: Logo检测
- **ocr**: 文字识别
- **face**: 人脸检测
- **qrcode**: 二维码检测
- **scene**: 场景识别

#### 6. 检测结果说明

```python
{
    "success": True,
    "detections": {
        "porn": {
            "suggestion": "pass",  # pass, review, block
            "confidence": 0.1,     # 置信度 0.0-1.0
            "is_violation": False  # 是否违规
        }
    },
    "summary": {
        "risk_level": "SAFE",     # SAFE, LOW, MEDIUM, HIGH
        "total_scenes": 1,
        "violations": [],         # 违规内容列表
        "confidence_scores": {}   # 各场景置信度
    },
    "metadata": {
        "detection_time": "2024-01-01 12:00:00",
        "detection_types": ["porn"],
        "confidence_threshold": 0.8
    }
}
```

## 检测原理

### 人脸识别和活体检测

#### 眨眼检测 (EAR - Eye Aspect Ratio)

眨眼检测基于眼睛纵横比(EAR)算法：

```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
```

其中p1-p6是眼睛关键点的坐标。当EAR低于阈值时，表示眼睛闭合。

#### 张嘴检测 (MAR - Mouth Aspect Ratio)

张嘴检测基于嘴部纵横比(MAR)算法：

```
MAR = (|p2-p10| + |p4-p8|) / (2 * |p1-p7|)
```

其中p1-p10是嘴部关键点的坐标。当MAR高于阈值时，表示嘴巴张开。

### 阿里云图像内容检测

#### 检测流程

1. **图像预处理**: 将图像编码为base64格式或直接使用URL
2. **API调用**: 调用阿里云内容安全API进行检测
3. **结果解析**: 解析API返回的检测结果
4. **风险评估**: 根据置信度和建议生成风险等级

#### 检测类型说明

- **色情检测**: 识别图像中的色情内容，包括裸露、性行为等
- **暴恐检测**: 识别图像中的暴力、恐怖主义相关内容
- **广告检测**: 识别图像中的广告内容
- **直播检测**: 识别图像是否为直播内容
- **Logo检测**: 识别图像中的品牌Logo
- **OCR检测**: 识别图像中的文字内容
- **人脸检测**: 检测图像中的人脸
- **二维码检测**: 识别图像中的二维码
- **场景识别**: 识别图像的场景类型

## 参数调优

### 人脸识别和活体检测

可以在`FaceLivenessDetector`类中调整以下参数：

```python
# 眨眼检测参数
self.EAR_THRESHOLD = 0.25  # 眼睛纵横比阈值
self.EAR_CONSECUTIVE_FRAMES = 3  # 连续帧数

# 张嘴检测参数
self.MAR_THRESHOLD = 0.5  # 嘴部纵横比阈值
self.MAR_CONSECUTIVE_FRAMES = 3  # 连续帧数
```

### 阿里云图像内容检测

可以在`config.ini`中调整以下参数：

```ini
[aliyun_image_detection]
# 检测类型，多个用逗号分隔
detection_types = porn,terrorism,ad

# 置信度阈值 (0.0-1.0)
confidence_threshold = 0.8

# 是否启用异步检测
async_detection = false
```

#### 置信度阈值说明

- **0.5-0.6**: 宽松模式，减少误报但可能漏检
- **0.7-0.8**: 平衡模式，推荐设置
- **0.9-1.0**: 严格模式，减少漏检但可能误报

## 性能优化

### 人脸识别和活体检测

1. **GPU加速**: 系统自动检测并使用GPU加速
2. **多模型支持**: MediaPipe作为主要检测器，dlib作为备用
3. **实时处理**: 优化的算法确保实时性能

### 阿里云图像内容检测

1. **批量处理**: 使用批量检测API提高效率
2. **异步检测**: 对于大量图像可使用异步模式
3. **缓存机制**: 避免重复检测相同图像
4. **并发控制**: 合理控制并发请求数量

## 系统要求

### 人脸识别和活体检测

- Python 3.7+
- OpenCV 4.x
- CUDA支持的GPU (可选)
- 摄像头设备

### 阿里云图像内容检测

- Python 3.7+
- 阿里云账号和访问密钥
- 网络连接（访问阿里云API）
- 支持的图像格式：JPG, JPEG, PNG, GIF, BMP, WEBP

## 注意事项

### 人脸识别和活体检测

1. 首次运行会自动下载dlib预训练模型
2. 确保摄像头权限已开启
3. 在光线充足的环境下效果更佳
4. 建议人脸距离摄像头30-60cm

### 阿里云图像内容检测

1. 需要有效的阿里云账号和访问密钥
2. 确保网络连接正常，能够访问阿里云API
3. 图像文件大小建议不超过10MB
4. 支持的图像格式：JPG, JPEG, PNG, GIF, BMP, WEBP
5. 检测结果基于阿里云的内容安全算法，可能存在误判
6. 建议根据实际需求调整置信度阈值

## 故障排除

### 人脸识别和活体检测

#### 常见问题

1. **GPU不可用**: 系统会自动回退到CPU模式
2. **摄像头无法打开**: 检查摄像头权限和设备连接
3. **检测精度低**: 调整阈值参数或改善光线条件

#### 调试模式

在代码中设置调试模式：

```python
detector = FaceLivenessDetector(use_gpu=True)
# 启用详细日志输出
```

### 阿里云图像内容检测

#### 常见问题

1. **认证失败**: 检查access_key_id和access_key_secret是否正确
2. **网络连接失败**: 检查网络连接和防火墙设置
3. **图像格式不支持**: 确保图像格式在支持列表中
4. **API调用频率限制**: 降低并发请求数量
5. **检测结果不准确**: 调整置信度阈值或检测类型

#### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 错误代码说明

- **InvalidParameter**: 参数错误，检查输入参数
- **Forbidden**: 权限不足，检查访问密钥
- **InternalError**: 内部错误，稍后重试
- **ServiceUnavailable**: 服务不可用，检查网络连接

## 文件说明

### 核心文件

- `face_liveness_detection.py`: 人脸识别和活体检测核心模块
- `aliyun_image_detection.py`: 阿里云图像内容检测客户端
- `image_content_detection_service.py`: 图像内容检测服务封装
- `demo_image_detection.py`: 图像内容检测演示脚本
- `test_image_detection.py`: 图像内容检测测试脚本

### 配置文件

- `config.ini`: 主配置文件，包含阿里云访问密钥等配置
- `requirements.txt`: Python依赖包列表

### 使用示例

```bash
# 人脸识别和活体检测
python face_liveness_detection.py
python test_liveness_detection.py

# 阿里云图像内容检测
python demo_image_detection.py --create-samples
python demo_image_detection.py --image your_image.jpg
python test_image_detection.py
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v2.0.0 (2024-01-01)
- 新增阿里云图像内容检测功能
- 支持多种检测类型：色情、暴恐、广告等
- 新增批量检测和目录扫描功能
- 新增检测结果统计和报告生成
- 完善测试覆盖和文档

### v1.0.0 (2023-12-01)
- 初始版本发布
- 支持人脸识别和活体检测
- 支持眨眼和张嘴检测
- 支持GPU加速