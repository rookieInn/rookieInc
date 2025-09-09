#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版视频水印处理工具
仅依赖FFmpeg，无需Python图像处理库
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

class SimpleVideoWatermarkProcessor:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化视频水印处理器
        
        Args:
            ffmpeg_path: FFmpeg可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """检查FFmpeg是否安装并可用"""
        try:
            result = subprocess.run([self.ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("FFmpeg不可用")
            print("✓ FFmpeg已就绪")
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            print(f"❌ FFmpeg检查失败: {e}")
            print("请安装FFmpeg: sudo apt-get install ffmpeg")
            sys.exit(1)
    
    def add_text_watermark(self, input_video: str, output_video: str, 
                          text: str, position: str = "bottom-right",
                          font_size: int = 24, font_color: str = "white",
                          background_color: str = "black@0.5", 
                          margin: int = 20) -> bool:
        """
        添加文字水印
        
        Args:
            input_video: 输入视频路径
            output_video: 输出视频路径
            text: 水印文字
            position: 水印位置 (top-left, top-right, bottom-left, bottom-right, center)
            font_size: 字体大小
            font_color: 字体颜色
            background_color: 背景颜色和透明度
            margin: 边距
            
        Returns:
            是否成功
        """
        if not os.path.exists(input_video):
            print(f"❌ 输入视频文件不存在: {input_video}")
            return False
        
        # 位置映射
        position_map = {
            "top-left": f"x={margin}:y={margin}",
            "top-right": f"x=w-tw-{margin}:y={margin}",
            "bottom-left": f"x={margin}:y=h-th-{margin}",
            "bottom-right": f"x=w-tw-{margin}:y=h-th-{margin}",
            "center": "x=(w-tw)/2:y=(h-th)/2"
        }
        
        if position not in position_map:
            print(f"❌ 不支持的位置: {position}")
            return False
        
        pos = position_map[position]
        
        # 构建FFmpeg命令
        cmd = [
            self.ffmpeg_path,
            "-i", input_video,
            "-vf", f"drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:box=1:boxcolor={background_color}:boxborderw=5:{pos}",
            "-c:a", "copy",  # 保持音频不变
            "-y",  # 覆盖输出文件
            output_video
        ]
        
        print(f"🎬 正在为视频添加文字水印...")
        print(f"   输入: {input_video}")
        print(f"   输出: {output_video}")
        print(f"   文字: {text}")
        print(f"   位置: {position}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ 文字水印添加成功!")
                return True
            else:
                print(f"❌ 文字水印添加失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 处理超时")
            return False
        except Exception as e:
            print(f"❌ 处理出错: {e}")
            return False
    
    def add_image_watermark(self, input_video: str, output_video: str,
                           watermark_image: str, position: str = "bottom-right",
                           opacity: float = 0.7, scale: float = 0.2,
                           margin: int = 20) -> bool:
        """
        添加图片水印
        
        Args:
            input_video: 输入视频路径
            output_video: 输出视频路径
            watermark_image: 水印图片路径
            position: 水印位置
            opacity: 透明度 (0.0-1.0)
            scale: 缩放比例
            margin: 边距
            
        Returns:
            是否成功
        """
        if not os.path.exists(input_video):
            print(f"❌ 输入视频文件不存在: {input_video}")
            return False
        
        if not os.path.exists(watermark_image):
            print(f"❌ 水印图片文件不存在: {watermark_image}")
            return False
        
        # 位置映射
        position_map = {
            "top-left": f"x={margin}:y={margin}",
            "top-right": f"x=W-w-{margin}:y={margin}",
            "bottom-left": f"x={margin}:y=H-h-{margin}",
            "bottom-right": f"x=W-w-{margin}:y=H-h-{margin}",
            "center": "x=(W-w)/2:y=(H-h)/2"
        }
        
        if position not in position_map:
            print(f"❌ 不支持的位置: {position}")
            return False
        
        pos = position_map[position]
        
        # 构建FFmpeg命令
        cmd = [
            self.ffmpeg_path,
            "-i", input_video,
            "-i", watermark_image,
            "-filter_complex", f"[1:v]scale=iw*{scale}:ih*{scale},format=rgba,colorchannelmixer=aa={opacity}[watermark];[0:v][watermark]overlay={pos}[v]",
            "-map", "[v]",
            "-map", "0:a",  # 保持原音频
            "-c:a", "copy",
            "-y",
            output_video
        ]
        
        print(f"🎬 正在为视频添加图片水印...")
        print(f"   输入: {input_video}")
        print(f"   输出: {output_video}")
        print(f"   水印图片: {watermark_image}")
        print(f"   位置: {position}")
        print(f"   透明度: {opacity}")
        print(f"   缩放: {scale}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ 图片水印添加成功!")
                return True
            else:
                print(f"❌ 图片水印添加失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 处理超时")
            return False
        except Exception as e:
            print(f"❌ 处理出错: {e}")
            return False
    
    def add_transparent_watermark(self, input_video: str, output_video: str,
                                 text: str, font_size: int = 48,
                                 opacity: float = 0.3, angle: float = -30) -> bool:
        """
        添加透明重复水印（类似版权保护）
        
        Args:
            input_video: 输入视频路径
            output_video: 输出视频路径
            text: 水印文字
            font_size: 字体大小
            opacity: 透明度
            angle: 旋转角度
            
        Returns:
            是否成功
        """
        if not os.path.exists(input_video):
            print(f"❌ 输入视频文件不存在: {input_video}")
            return False
        
        # 构建FFmpeg命令 - 使用重复文字效果
        cmd = [
            self.ffmpeg_path,
            "-i", input_video,
            "-vf", f"drawtext=text='{text}':fontsize={font_size}:fontcolor=white@{opacity}:x=(w-tw)/2:y=(h-th)/2:repeat=1",
            "-c:a", "copy",
            "-y",
            output_video
        ]
        
        print(f"🎬 正在为视频添加透明水印...")
        print(f"   输入: {input_video}")
        print(f"   输出: {output_video}")
        print(f"   文字: {text}")
        print(f"   透明度: {opacity}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ 透明水印添加成功!")
                return True
            else:
                print(f"❌ 透明水印添加失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 处理超时")
            return False
        except Exception as e:
            print(f"❌ 处理出错: {e}")
            return False
    
    def batch_process(self, input_dir: str, output_dir: str, 
                     watermark_config: Dict[str, Any]) -> List[str]:
        """
        批量处理视频文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            watermark_config: 水印配置
            
        Returns:
            处理成功的文件列表
        """
        if not os.path.exists(input_dir):
            print(f"❌ 输入目录不存在: {input_dir}")
            return []
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 支持的视频格式
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        
        # 查找所有视频文件
        video_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    video_files.append(os.path.join(root, file))
        
        if not video_files:
            print(f"❌ 在目录 {input_dir} 中未找到视频文件")
            return []
        
        print(f"📁 找到 {len(video_files)} 个视频文件")
        
        successful_files = []
        for i, video_file in enumerate(video_files, 1):
            print(f"\n🎬 处理第 {i}/{len(video_files)} 个文件: {os.path.basename(video_file)}")
            
            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(video_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}_watermarked.mp4")
            
            # 根据配置添加水印
            success = False
            watermark_type = watermark_config.get('type', 'text')
            
            if watermark_type == 'text':
                success = self.add_text_watermark(
                    video_file, output_file,
                    watermark_config.get('text', 'WATERMARK'),
                    watermark_config.get('position', 'bottom-right'),
                    watermark_config.get('font_size', 24),
                    watermark_config.get('font_color', 'white'),
                    watermark_config.get('background_color', 'black@0.5'),
                    watermark_config.get('margin', 20)
                )
            elif watermark_type == 'image':
                success = self.add_image_watermark(
                    video_file, output_file,
                    watermark_config.get('image_path', ''),
                    watermark_config.get('position', 'bottom-right'),
                    watermark_config.get('opacity', 0.7),
                    watermark_config.get('scale', 0.2),
                    watermark_config.get('margin', 20)
                )
            elif watermark_type == 'transparent':
                success = self.add_transparent_watermark(
                    video_file, output_file,
                    watermark_config.get('text', 'WATERMARK'),
                    watermark_config.get('font_size', 48),
                    watermark_config.get('opacity', 0.3),
                    watermark_config.get('angle', -30)
                )
            
            if success:
                successful_files.append(output_file)
                print(f"✅ 完成: {output_file}")
            else:
                print(f"❌ 失败: {video_file}")
        
        print(f"\n📊 批量处理完成: {len(successful_files)}/{len(video_files)} 个文件成功")
        return successful_files
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        if not os.path.exists(video_path):
            return {}
        
        cmd = [
            self.ffmpeg_path, "-i", video_path,
            "-f", "null", "-"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # 解析FFmpeg输出获取视频信息
            info = {}
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    duration = line.split('Duration:')[1].split(',')[0].strip()
                    info['duration'] = duration
                elif 'Video:' in line:
                    video_info = line.split('Video:')[1].split(',')[0].strip()
                    info['video_codec'] = video_info
                elif 'Audio:' in line:
                    audio_info = line.split('Audio:')[1].split(',')[0].strip()
                    info['audio_codec'] = audio_info
            return info
        except Exception as e:
            print(f"❌ 获取视频信息失败: {e}")
            return {}

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='简化版视频水印处理工具')
    parser.add_argument('input', help='输入视频文件或目录')
    parser.add_argument('-o', '--output', help='输出文件或目录')
    parser.add_argument('-t', '--type', choices=['text', 'image', 'transparent'], 
                       default='text', help='水印类型')
    parser.add_argument('--text', default='WATERMARK', help='水印文字')
    parser.add_argument('--image', help='水印图片路径')
    parser.add_argument('--position', choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                       default='bottom-right', help='水印位置')
    parser.add_argument('--font-size', type=int, default=24, help='字体大小')
    parser.add_argument('--font-color', default='white', help='字体颜色')
    parser.add_argument('--background-color', default='black@0.5', help='背景颜色和透明度')
    parser.add_argument('--opacity', type=float, default=0.7, help='透明度 (0.0-1.0)')
    parser.add_argument('--scale', type=float, default=0.2, help='缩放比例')
    parser.add_argument('--margin', type=int, default=20, help='边距')
    parser.add_argument('--angle', type=float, default=-30, help='旋转角度')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    parser.add_argument('--ffmpeg-path', default='ffmpeg', help='FFmpeg可执行文件路径')
    parser.add_argument('--info', action='store_true', help='显示视频信息')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = SimpleVideoWatermarkProcessor(args.ffmpeg_path)
    
    # 显示视频信息
    if args.info:
        if os.path.isfile(args.input):
            info = processor.get_video_info(args.input)
            if info:
                print("📹 视频信息:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ 无法获取视频信息")
        else:
            print("❌ 请指定视频文件")
        return
    
    # 确定输出路径
    if not args.output:
        if os.path.isfile(args.input):
            base, ext = os.path.splitext(args.input)
            args.output = f"{base}_watermarked{ext}"
        else:
            args.output = f"{args.input}_watermarked"
    
    # 批量处理模式
    if args.batch or os.path.isdir(args.input):
        watermark_config = {
            'type': args.type,
            'text': args.text,
            'image_path': args.image,
            'position': args.position,
            'font_size': args.font_size,
            'font_color': args.font_color,
            'background_color': args.background_color,
            'opacity': args.opacity,
            'scale': args.scale,
            'margin': args.margin,
            'angle': args.angle
        }
        
        successful_files = processor.batch_process(args.input, args.output, watermark_config)
        print(f"\n🎉 批量处理完成! 成功处理 {len(successful_files)} 个文件")
        
    else:
        # 单文件处理
        if args.type == 'text':
            success = processor.add_text_watermark(
                args.input, args.output, args.text, args.position,
                args.font_size, args.font_color, args.background_color, args.margin
            )
        elif args.type == 'image':
            if not args.image:
                print("❌ 图片水印需要指定 --image 参数")
                return
            success = processor.add_image_watermark(
                args.input, args.output, args.image, args.position,
                args.opacity, args.scale, args.margin
            )
        elif args.type == 'transparent':
            success = processor.add_transparent_watermark(
                args.input, args.output, args.text, args.font_size,
                args.opacity, args.angle
            )
        
        if success:
            print(f"🎉 水印添加成功! 输出文件: {args.output}")
        else:
            print("❌ 水印添加失败")

if __name__ == "__main__":
    main()