# 文本转GIF生成器

一个功能强大的Python工具，可以根据输入的文本随机生成动态GIF图像。

## 功能特点

- 🎨 **多种动画效果**: 弹跳、淡入淡出、旋转、缩放、波浪、螺旋、彩虹等
- 🌈 **随机颜色主题**: 5种预定义的美观颜色主题
- 🎯 **随机装饰元素**: 自动添加星星、圆形、方形等装饰
- 📱 **多种尺寸支持**: 可自定义GIF的宽度和高度
- ⚡ **批量生成**: 支持一次生成多个GIF
- 🖥️ **交互模式**: 提供命令行交互界面

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 命令行使用

#### 基本用法
```bash
python text_to_gif_generator.py "Hello World!"
```

#### 自定义参数
```bash
python text_to_gif_generator.py "你好世界！" -o my_gif.gif -w 600 -h 400 -f 30
```

#### 交互模式
```bash
python text_to_gif_generator.py --interactive
```

### 2. Python代码使用

```python
from text_to_gif_generator import TextToGifGenerator

# 创建生成器
generator = TextToGifGenerator(width=400, height=300, duration=100)

# 生成单个GIF
generator.generate_gif("Hello World!", "output.gif", num_frames=20)

# 批量生成
texts = ["文本1", "文本2", "文本3"]
generator.generate_multiple_gifs(texts, "output_folder")
```

### 3. 运行示例

```bash
python gif_example.py
```

## 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--width` | `-w` | 400 | GIF宽度(像素) |
| `--height` | `-h` | 300 | GIF高度(像素) |
| `--frames` | `-f` | 20 | 动画帧数 |
| `--duration` | `-d` | 100 | 每帧持续时间(毫秒) |
| `--output` | `-o` | output.gif | 输出文件路径 |
| `--interactive` | | | 启用交互模式 |

## 动画效果类型

1. **bounce** - 弹跳效果
2. **fade** - 淡入淡出效果
3. **rotate** - 旋转效果
4. **scale** - 缩放效果
5. **wave** - 波浪效果
6. **spiral** - 螺旋效果
7. **rainbow** - 彩虹文字效果

## 颜色主题

程序内置5种精心设计的颜色主题，每次生成时会随机选择：

- 主题1: 红粉蓝绿黄
- 主题2: 薄荷绿橙粉红
- 主题3: 紫粉红黄橙
- 主题4: 绿青紫粉红
- 主题5: 灰蓝紫粉红

## 示例输出

运行示例程序会生成以下文件：
- `welcome.gif` - 欢迎GIF
- `sample_gifs/` 文件夹 - 包含多个示例GIF
- `small.gif`, `medium.gif`, `large.gif` - 不同尺寸的GIF

## 技术实现

- **图像处理**: 使用PIL (Pillow) 库
- **数学计算**: 使用NumPy进行数值计算
- **动画算法**: 基于数学函数的动画效果
- **颜色处理**: HSV到RGB的颜色转换
- **文件格式**: 支持标准GIF格式输出

## 注意事项

1. 确保系统安装了中文字体（如DejaVu Sans）以正确显示中文
2. 生成的GIF文件大小取决于帧数和图像尺寸
3. 建议帧数在10-50之间以获得最佳效果
4. 支持Unicode字符，包括emoji表情

## 故障排除

### 字体问题
如果中文显示异常，可以安装中文字体：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu-core

# 或者手动指定字体路径
```

### 内存问题
如果生成大尺寸或高帧数GIF时出现内存不足，可以：
- 减少帧数
- 降低图像尺寸
- 分批生成

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！