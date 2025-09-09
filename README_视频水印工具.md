# 视频水印处理工具

一个功能强大的视频水印处理工具，支持为视频添加文字水印、图片水印和透明重复水印。

## 功能特性

- 🎬 **多种水印类型**：支持文字水印、图片水印、透明重复水印
- 📁 **批量处理**：支持批量处理整个目录的视频文件
- 🎨 **灵活配置**：支持自定义位置、大小、颜色、透明度等参数
- 🔧 **易于使用**：提供命令行接口和Python API
- ⚡ **高效处理**：基于FFmpeg，处理速度快

## 安装依赖

### 1. 安装FFmpeg

```bash
# 运行自动安装脚本
./install_ffmpeg.sh

# 或手动安装
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# CentOS/RHEL:
sudo yum install epel-release
sudo yum install ffmpeg

# macOS:
brew install ffmpeg
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

#### 基本语法

```bash
python video_watermark.py <输入文件/目录> [选项]
```

#### 添加文字水印

```bash
# 基本文字水印
python video_watermark.py input.mp4 -o output.mp4 -t text --text "我的水印"

# 自定义位置和样式
python video_watermark.py input.mp4 -o output.mp4 -t text \
    --text "版权保护" \
    --position bottom-right \
    --font-size 32 \
    --font-color red \
    --background-color "black@0.8" \
    --margin 30
```

#### 添加图片水印

```bash
# 图片水印
python video_watermark.py input.mp4 -o output.mp4 -t image \
    --image watermark.png \
    --position top-left \
    --opacity 0.7 \
    --scale 0.3
```

#### 添加透明重复水印

```bash
# 透明重复水印（版权保护）
python video_watermark.py input.mp4 -o output.mp4 -t transparent \
    --text "COPYRIGHT" \
    --font-size 48 \
    --opacity 0.3 \
    --angle -30
```

#### 批量处理

```bash
# 批量处理目录中的所有视频
python video_watermark.py /path/to/videos/ -o /path/to/output/ --batch -t text --text "批量水印"
```

#### 查看视频信息

```bash
# 显示视频详细信息
python video_watermark.py input.mp4 --info
```

### Python API使用

```python
from video_watermark import VideoWatermarkProcessor

# 创建处理器
processor = VideoWatermarkProcessor()

# 添加文字水印
processor.add_text_watermark(
    input_video="input.mp4",
    output_video="output.mp4",
    text="我的水印",
    position="bottom-right",
    font_size=24,
    font_color="white",
    background_color="black@0.5"
)

# 添加图片水印
processor.add_image_watermark(
    input_video="input.mp4",
    output_video="output.mp4",
    watermark_image="logo.png",
    position="top-left",
    opacity=0.7,
    scale=0.2
)

# 批量处理
watermark_config = {
    'type': 'text',
    'text': '批量水印',
    'position': 'bottom-right',
    'font_size': 24
}
successful_files = processor.batch_process(
    input_dir="videos/",
    output_dir="watermarked_videos/",
    watermark_config=watermark_config
)
```

## 参数说明

### 水印位置 (position)
- `top-left`: 左上角
- `top-right`: 右上角
- `bottom-left`: 左下角
- `bottom-right`: 右下角
- `center`: 居中

### 水印类型 (type)
- `text`: 文字水印
- `image`: 图片水印
- `transparent`: 透明重复水印

### 常用参数
- `--text`: 水印文字内容
- `--image`: 水印图片路径
- `--position`: 水印位置
- `--font-size`: 字体大小
- `--font-color`: 字体颜色
- `--background-color`: 背景颜色和透明度
- `--opacity`: 透明度 (0.0-1.0)
- `--scale`: 缩放比例
- `--margin`: 边距
- `--angle`: 旋转角度
- `--batch`: 批量处理模式

## 使用示例

### 示例1：为单个视频添加版权水印

```bash
python video_watermark.py my_video.mp4 -o my_video_watermarked.mp4 \
    -t text --text "© 2024 My Company" \
    --position bottom-right --font-size 20 \
    --font-color white --background-color "black@0.7"
```

### 示例2：批量添加Logo水印

```bash
python video_watermark.py videos/ -o watermarked_videos/ --batch \
    -t image --image company_logo.png \
    --position top-right --opacity 0.8 --scale 0.15
```

### 示例3：添加透明重复水印保护

```bash
python video_watermark.py sensitive_video.mp4 -o protected_video.mp4 \
    -t transparent --text "CONFIDENTIAL" \
    --font-size 60 --opacity 0.2 --angle -45
```

## 支持的视频格式

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)

## 注意事项

1. **FFmpeg依赖**：确保系统已安装FFmpeg
2. **文件权限**：确保对输入和输出目录有读写权限
3. **处理时间**：视频处理时间取决于文件大小和系统性能
4. **输出质量**：默认保持原视频质量，音频不变
5. **临时文件**：处理过程中会创建临时文件，处理完成后自动清理

## 故障排除

### 常见问题

1. **FFmpeg未找到**
   ```bash
   # 检查FFmpeg是否安装
   ffmpeg -version
   
   # 如果未安装，运行安装脚本
   ./install_ffmpeg.sh
   ```

2. **权限不足**
   ```bash
   # 确保有执行权限
   chmod +x video_watermark.py
   chmod +x install_ffmpeg.sh
   ```

3. **内存不足**
   - 处理大视频文件时可能需要更多内存
   - 可以尝试降低视频分辨率或分段处理

4. **编码不支持**
   - 某些视频编码可能不被支持
   - 可以先用FFmpeg转换编码格式

## 高级用法

### 自定义水印样式

```python
# 创建自定义水印图片
from PIL import Image, ImageDraw, ImageFont

def create_custom_watermark(text, output_path):
    img = Image.new('RGBA', (400, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 36)
    draw.text((10, 30), text, fill=(255, 255, 255, 180), font=font)
    img.save(output_path)

# 使用自定义水印
create_custom_watermark("Custom Watermark", "custom_watermark.png")
```

### 批量处理配置

```python
# 创建批量处理配置文件
config = {
    'type': 'text',
    'text': '© 2024 My Company',
    'position': 'bottom-right',
    'font_size': 24,
    'font_color': 'white',
    'background_color': 'black@0.7',
    'margin': 20
}

# 保存配置
import json
with open('watermark_config.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持文字水印、图片水印、透明重复水印
- 支持批量处理
- 提供命令行接口和Python API