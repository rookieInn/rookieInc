#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频水印工具快速开始脚本
提供交互式界面，方便用户快速上手
"""

import os
import sys
from video_watermark import VideoWatermarkProcessor

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎬 视频水印处理工具 - 快速开始")
    print("=" * 60)
    print()

def check_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
        else:
            print("❌ FFmpeg未安装，请运行: ./install_ffmpeg.sh")
            return False
    except:
        print("❌ FFmpeg未安装，请运行: ./install_ffmpeg.sh")
        return False
    
    # 检查Python依赖
    try:
        from PIL import Image
        import numpy as np
        print("✅ Python依赖已安装")
    except ImportError as e:
        print(f"❌ Python依赖缺失: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def get_video_files():
    """获取可用的视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    video_files = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))
    
    return video_files

def select_video_file():
    """选择视频文件"""
    video_files = get_video_files()
    
    if not video_files:
        print("❌ 当前目录下没有找到视频文件")
        print("请将视频文件放在当前目录下，或指定完整路径")
        return None
    
    print("\n📁 找到以下视频文件:")
    for i, video in enumerate(video_files, 1):
        print(f"   {i}. {video}")
    
    while True:
        try:
            choice = input(f"\n请选择视频文件 (1-{len(video_files)}): ").strip()
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(video_files):
                return video_files[index]
            else:
                print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入有效数字")

def select_watermark_type():
    """选择水印类型"""
    print("\n🎨 选择水印类型:")
    print("   1. 文字水印 - 添加文字到视频")
    print("   2. 图片水印 - 添加图片Logo到视频")
    print("   3. 透明重复水印 - 添加透明重复文字（版权保护）")
    
    while True:
        choice = input("\n请选择水印类型 (1-3): ").strip()
        if choice == '1':
            return 'text'
        elif choice == '2':
            return 'image'
        elif choice == '3':
            return 'transparent'
        elif choice.lower() == 'q':
            return None
        else:
            print("❌ 无效选择，请重新输入")

def get_text_watermark_config():
    """获取文字水印配置"""
    print("\n📝 配置文字水印:")
    
    text = input("水印文字 (默认: WATERMARK): ").strip() or "WATERMARK"
    
    print("\n位置选项:")
    positions = {
        '1': 'top-left',
        '2': 'top-right', 
        '3': 'bottom-left',
        '4': 'bottom-right',
        '5': 'center'
    }
    
    for key, value in positions.items():
        print(f"   {key}. {value}")
    
    while True:
        pos_choice = input("选择位置 (1-5, 默认: 4): ").strip() or "4"
        if pos_choice in positions:
            position = positions[pos_choice]
            break
        else:
            print("❌ 无效选择，请重新输入")
    
    try:
        font_size = int(input("字体大小 (默认: 24): ").strip() or "24")
    except ValueError:
        font_size = 24
    
    font_color = input("字体颜色 (默认: white): ").strip() or "white"
    bg_color = input("背景颜色和透明度 (默认: black@0.5): ").strip() or "black@0.5"
    
    return {
        'type': 'text',
        'text': text,
        'position': position,
        'font_size': font_size,
        'font_color': font_color,
        'background_color': bg_color
    }

def get_image_watermark_config():
    """获取图片水印配置"""
    print("\n🖼️  配置图片水印:")
    
    while True:
        image_path = input("水印图片路径: ").strip()
        if not image_path:
            print("❌ 请提供图片路径")
            continue
        
        if os.path.exists(image_path):
            break
        else:
            print("❌ 图片文件不存在，请重新输入")
    
    print("\n位置选项:")
    positions = {
        '1': 'top-left',
        '2': 'top-right',
        '3': 'bottom-left', 
        '4': 'bottom-right',
        '5': 'center'
    }
    
    for key, value in positions.items():
        print(f"   {key}. {value}")
    
    while True:
        pos_choice = input("选择位置 (1-5, 默认: 4): ").strip() or "4"
        if pos_choice in positions:
            position = positions[pos_choice]
            break
        else:
            print("❌ 无效选择，请重新输入")
    
    try:
        opacity = float(input("透明度 0.0-1.0 (默认: 0.7): ").strip() or "0.7")
        scale = float(input("缩放比例 (默认: 0.2): ").strip() or "0.2")
    except ValueError:
        opacity = 0.7
        scale = 0.2
    
    return {
        'type': 'image',
        'image_path': image_path,
        'position': position,
        'opacity': opacity,
        'scale': scale
    }

def get_transparent_watermark_config():
    """获取透明水印配置"""
    print("\n🔒 配置透明重复水印:")
    
    text = input("水印文字 (默认: COPYRIGHT): ").strip() or "COPYRIGHT"
    
    try:
        font_size = int(input("字体大小 (默认: 48): ").strip() or "48")
        opacity = float(input("透明度 0.0-1.0 (默认: 0.3): ").strip() or "0.3")
        angle = float(input("旋转角度 (默认: -30): ").strip() or "-30")
    except ValueError:
        font_size = 48
        opacity = 0.3
        angle = -30
    
    return {
        'type': 'transparent',
        'text': text,
        'font_size': font_size,
        'opacity': opacity,
        'angle': angle
    }

def process_video(input_video, output_video, config):
    """处理视频"""
    print(f"\n🎬 开始处理视频...")
    print(f"   输入: {input_video}")
    print(f"   输出: {output_video}")
    
    processor = VideoWatermarkProcessor()
    
    try:
        if config['type'] == 'text':
            success = processor.add_text_watermark(
                input_video, output_video,
                config['text'], config['position'],
                config['font_size'], config['font_color'],
                config['background_color']
            )
        elif config['type'] == 'image':
            success = processor.add_image_watermark(
                input_video, output_video,
                config['image_path'], config['position'],
                config['opacity'], config['scale']
            )
        elif config['type'] == 'transparent':
            success = processor.add_transparent_watermark(
                input_video, output_video,
                config['text'], config['font_size'],
                config['opacity'], config['angle']
            )
        
        if success:
            print(f"🎉 处理完成! 输出文件: {output_video}")
            return True
        else:
            print("❌ 处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 处理出错: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查系统要求
    if not check_requirements():
        print("\n❌ 系统要求检查失败，请先安装必要的依赖")
        return
    
    print("✅ 系统要求检查通过\n")
    
    # 选择视频文件
    input_video = select_video_file()
    if not input_video:
        print("👋 再见!")
        return
    
    # 选择水印类型
    watermark_type = select_watermark_type()
    if not watermark_type:
        print("👋 再见!")
        return
    
    # 获取配置
    if watermark_type == 'text':
        config = get_text_watermark_config()
    elif watermark_type == 'image':
        config = get_image_watermark_config()
    elif watermark_type == 'transparent':
        config = get_transparent_watermark_config()
    
    # 生成输出文件名
    base_name = os.path.splitext(input_video)[0]
    output_video = f"{base_name}_watermarked.mp4"
    
    # 确认处理
    print(f"\n📋 处理配置:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    confirm = input(f"\n确认开始处理? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 取消处理")
        return
    
    # 处理视频
    success = process_video(input_video, output_video, config)
    
    if success:
        print(f"\n🎉 视频水印添加成功!")
        print(f"📁 输出文件: {output_video}")
        print(f"📊 文件大小: {os.path.getsize(output_video) / (1024*1024):.1f} MB")
    else:
        print(f"\n❌ 视频水印添加失败")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        sys.exit(1)