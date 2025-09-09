#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频水印工具演示脚本
展示各种水印效果的使用方法
"""

import os
import sys
import subprocess
from simple_video_watermark import SimpleVideoWatermarkProcessor

def print_demo_banner():
    """打印演示横幅"""
    print("=" * 60)
    print("🎬 视频水印工具演示")
    print("=" * 60)
    print()

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            return True
        else:
            print("❌ FFmpeg未安装")
            return False
    except:
        print("❌ FFmpeg未安装")
        return False

def create_sample_video():
    """创建示例视频（如果不存在）"""
    sample_video = "sample_video.mp4"
    
    if os.path.exists(sample_video):
        print(f"✅ 示例视频已存在: {sample_video}")
        return sample_video
    
    print("🎬 创建示例视频...")
    
    # 使用FFmpeg创建一个简单的测试视频
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=10:size=640x480:rate=30',
        '-f', 'lavfi', 
        '-i', 'sine=frequency=1000:duration=10',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-y',
        sample_video
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ 示例视频创建成功: {sample_video}")
            return sample_video
        else:
            print(f"❌ 示例视频创建失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ 创建示例视频出错: {e}")
        return None

def demo_text_watermark(processor, input_video):
    """演示文字水印"""
    print("\n📝 演示文字水印...")
    
    # 不同位置的文字水印
    positions = [
        ("top-left", "左上角水印"),
        ("top-right", "右上角水印"), 
        ("bottom-left", "左下角水印"),
        ("bottom-right", "右下角水印"),
        ("center", "居中水印")
    ]
    
    for position, description in positions:
        output_file = f"demo_text_{position.replace('-', '_')}.mp4"
        print(f"   创建 {description}: {output_file}")
        
        success = processor.add_text_watermark(
            input_video, output_file,
            text=description,
            position=position,
            font_size=24,
            font_color="white",
            background_color="black@0.7"
        )
        
        if success:
            print(f"   ✅ 成功: {output_file}")
        else:
            print(f"   ❌ 失败: {output_file}")

def demo_watermark_styles(processor, input_video):
    """演示不同水印样式"""
    print("\n🎨 演示不同水印样式...")
    
    styles = [
        {
            "name": "红色警告水印",
            "text": "⚠️ 警告",
            "font_color": "red",
            "background_color": "yellow@0.8",
            "font_size": 28
        },
        {
            "name": "蓝色信息水印", 
            "text": "ℹ️ 信息",
            "font_color": "blue",
            "background_color": "white@0.9",
            "font_size": 24
        },
        {
            "name": "绿色成功水印",
            "text": "✅ 完成",
            "font_color": "green", 
            "background_color": "black@0.6",
            "font_size": 26
        },
        {
            "name": "版权保护水印",
            "text": "© 2024 My Company",
            "font_color": "white",
            "background_color": "black@0.8",
            "font_size": 20
        }
    ]
    
    for i, style in enumerate(styles, 1):
        output_file = f"demo_style_{i}.mp4"
        print(f"   创建 {style['name']}: {output_file}")
        
        success = processor.add_text_watermark(
            input_video, output_file,
            text=style["text"],
            position="bottom-right",
            font_size=style["font_size"],
            font_color=style["font_color"],
            background_color=style["background_color"]
        )
        
        if success:
            print(f"   ✅ 成功: {output_file}")
        else:
            print(f"   ❌ 失败: {output_file}")

def demo_transparent_watermark(processor, input_video):
    """演示透明水印"""
    print("\n🔒 演示透明水印...")
    
    output_file = "demo_transparent.mp4"
    print(f"   创建透明水印: {output_file}")
    
    success = processor.add_transparent_watermark(
        input_video, output_file,
        text="CONFIDENTIAL",
        font_size=48,
        opacity=0.3,
        angle=-30
    )
    
    if success:
        print(f"   ✅ 成功: {output_file}")
    else:
        print(f"   ❌ 失败: {output_file}")

def show_file_info():
    """显示生成的文件信息"""
    print("\n📁 生成的文件列表:")
    
    demo_files = [
        "demo_text_top_left.mp4",
        "demo_text_top_right.mp4", 
        "demo_text_bottom_left.mp4",
        "demo_text_bottom_right.mp4",
        "demo_text_center.mp4",
        "demo_style_1.mp4",
        "demo_style_2.mp4",
        "demo_style_3.mp4", 
        "demo_style_4.mp4",
        "demo_transparent.mp4"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"   ✅ {file} ({size:.1f} MB)")
        else:
            print(f"   ❌ {file} (未生成)")

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("1. 为视频添加文字水印:")
    print("   python3 simple_video_watermark.py video.mp4 -t text --text '我的水印'")
    print()
    print("2. 添加图片水印:")
    print("   python3 simple_video_watermark.py video.mp4 -t image --image logo.png")
    print()
    print("3. 批量处理:")
    print("   python3 simple_video_watermark.py videos/ -o output/ --batch -t text --text '批量水印'")
    print()
    print("4. 查看帮助:")
    print("   python3 simple_video_watermark.py --help")

def main():
    """主函数"""
    print_demo_banner()
    
    # 检查FFmpeg
    if not check_ffmpeg():
        print("\n❌ 请先安装FFmpeg: ./install_ffmpeg.sh")
        return
    
    # 创建示例视频
    input_video = create_sample_video()
    if not input_video:
        print("\n❌ 无法创建示例视频，演示终止")
        return
    
    # 创建处理器
    processor = SimpleVideoWatermarkProcessor()
    
    # 运行演示
    demo_text_watermark(processor, input_video)
    demo_watermark_styles(processor, input_video)
    demo_transparent_watermark(processor, input_video)
    
    # 显示结果
    show_file_info()
    show_usage_examples()
    
    print("\n🎉 演示完成!")
    print("💡 提示: 使用视频播放器查看生成的水印效果")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消演示")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        sys.exit(1)