#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频水印工具测试脚本
"""

import os
import sys
import subprocess
from video_watermark import VideoWatermarkProcessor

def test_ffmpeg_installation():
    """测试FFmpeg是否安装"""
    print("🔍 检查FFmpeg安装状态...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            version_line = result.stdout.split('\n')[0]
            print(f"   版本: {version_line}")
            return True
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ FFmpeg检查失败: {e}")
        return False

def test_processor_initialization():
    """测试处理器初始化"""
    print("\n🔧 测试视频水印处理器初始化...")
    try:
        processor = VideoWatermarkProcessor()
        print("✅ 处理器初始化成功")
        return True
    except Exception as e:
        print(f"❌ 处理器初始化失败: {e}")
        return False

def test_video_info():
    """测试视频信息获取"""
    print("\n📹 测试视频信息获取...")
    
    # 查找测试视频文件
    test_videos = []
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith(ext):
                    test_videos.append(os.path.join(root, file))
                    break
            if test_videos:
                break
        if test_videos:
            break
    
    if not test_videos:
        print("⚠️  未找到测试视频文件，跳过视频信息测试")
        return True
    
    processor = VideoWatermarkProcessor()
    video_path = test_videos[0]
    print(f"   测试文件: {video_path}")
    
    try:
        info = processor.get_video_info(video_path)
        if info:
            print("✅ 视频信息获取成功")
            for key, value in info.items():
                print(f"   {key}: {value}")
            return True
        else:
            print("❌ 无法获取视频信息")
            return False
    except Exception as e:
        print(f"❌ 视频信息获取失败: {e}")
        return False

def test_watermark_creation():
    """测试水印图片创建"""
    print("\n🎨 测试水印图片创建...")
    
    processor = VideoWatermarkProcessor()
    temp_dir = processor._create_temp_dir()
    watermark_path = os.path.join(temp_dir, "test_watermark.png")
    
    try:
        processor._create_watermark_image(
            "TEST WATERMARK", watermark_path, 48, 0.5, -30
        )
        
        if os.path.exists(watermark_path):
            print("✅ 水印图片创建成功")
            print(f"   文件路径: {watermark_path}")
            return True
        else:
            print("❌ 水印图片创建失败")
            return False
    except Exception as e:
        print(f"❌ 水印图片创建失败: {e}")
        return False
    finally:
        processor._cleanup_temp_dir()

def run_basic_tests():
    """运行基本测试"""
    print("🧪 开始运行视频水印工具测试...\n")
    
    tests = [
        ("FFmpeg安装检查", test_ffmpeg_installation),
        ("处理器初始化", test_processor_initialization),
        ("视频信息获取", test_video_info),
        ("水印图片创建", test_watermark_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！视频水印工具可以正常使用。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("1. 为单个视频添加文字水印:")
    print("   python video_watermark.py input.mp4 -o output.mp4 -t text --text '我的水印'")
    print()
    print("2. 批量处理目录中的视频:")
    print("   python video_watermark.py videos/ -o watermarked/ --batch -t text --text '批量水印'")
    print()
    print("3. 添加图片水印:")
    print("   python video_watermark.py input.mp4 -o output.mp4 -t image --image logo.png")
    print()
    print("4. 查看视频信息:")
    print("   python video_watermark.py input.mp4 --info")
    print()
    print("5. 获取帮助:")
    print("   python video_watermark.py --help")

if __name__ == "__main__":
    success = run_basic_tests()
    show_usage_examples()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)