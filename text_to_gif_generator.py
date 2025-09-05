#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转GIF生成器
根据输入的文本随机生成动态GIF图像
"""

import random
import math
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from typing import List, Tuple, Optional
import os
import sys

class TextToGifGenerator:
    def __init__(self, width: int = 400, height: int = 300, duration: int = 1000):
        """
        初始化GIF生成器
        
        Args:
            width: GIF宽度
            height: GIF高度
            duration: 每帧持续时间(毫秒)
        """
        self.width = width
        self.height = height
        self.duration = duration
        self.frames = []
        
        # 预定义的颜色主题
        self.color_themes = [
            ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            ['#A8E6CF', '#FFD3A5', '#FFAAA5', '#FF8B94', '#D4A5A5'],
            ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#E17055'],
            ['#00B894', '#00CEC9', '#6C5CE7', '#A29BFE', '#FD79A8'],
            ['#2D3436', '#636E72', '#74B9FF', '#0984E3', '#6C5CE7']
        ]
        
        # 动画效果类型
        self.animation_types = [
            'bounce', 'fade', 'rotate', 'scale', 'wave', 'spiral', 'rainbow'
        ]
    
    def get_random_theme(self) -> List[str]:
        """获取随机颜色主题"""
        return random.choice(self.color_themes)
    
    def get_random_animation(self) -> str:
        """获取随机动画类型"""
        return random.choice(self.animation_types)
    
    def create_gradient_background(self, colors: List[str]) -> Image.Image:
        """创建渐变背景"""
        img = Image.new('RGB', (self.width, self.height), colors[0])
        draw = ImageDraw.Draw(img)
        
        # 创建径向渐变效果
        center_x, center_y = self.width // 2, self.height // 2
        max_radius = max(self.width, self.height) // 2
        
        for i in range(max_radius, 0, -2):
            color_index = int((max_radius - i) / max_radius * (len(colors) - 1))
            color = colors[min(color_index, len(colors) - 1)]
            draw.ellipse([center_x - i, center_y - i, center_x + i, center_y + i], 
                        fill=color, outline=None)
        
        return img
    
    def create_text_frame(self, text: str, frame_num: int, total_frames: int, 
                         animation_type: str, colors: List[str]) -> Image.Image:
        """创建文本帧"""
        # 创建背景
        bg = self.create_gradient_background(colors)
        draw = ImageDraw.Draw(bg)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font_size = min(self.width, self.height) // 8
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # 计算文本位置
        text_bbox = draw.textbbox((0, 0), text, font=font) if font else (0, 0, len(text) * 10, 20)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 根据动画类型计算位置和效果
        progress = frame_num / total_frames
        
        if animation_type == 'bounce':
            # 弹跳效果
            bounce_offset = int(20 * math.sin(progress * 4 * math.pi))
            x = center_x - text_width // 2
            y = center_y - text_height // 2 + bounce_offset
            
        elif animation_type == 'fade':
            # 淡入淡出效果
            alpha = int(255 * (1 - abs(progress - 0.5) * 2))
            x = center_x - text_width // 2
            y = center_y - text_height // 2
            
        elif animation_type == 'rotate':
            # 旋转效果
            angle = progress * 360
            x = center_x - text_width // 2
            y = center_y - text_height // 2
            
        elif animation_type == 'scale':
            # 缩放效果
            scale = 0.5 + 0.5 * math.sin(progress * 2 * math.pi)
            x = center_x - int(text_width * scale) // 2
            y = center_y - int(text_height * scale) // 2
            
        elif animation_type == 'wave':
            # 波浪效果
            wave_offset = int(30 * math.sin(progress * 4 * math.pi))
            x = center_x - text_width // 2
            y = center_y - text_height // 2 + wave_offset
            
        elif animation_type == 'spiral':
            # 螺旋效果
            radius = 50 + 30 * progress
            angle = progress * 4 * math.pi
            x = center_x + int(radius * math.cos(angle)) - text_width // 2
            y = center_y + int(radius * math.sin(angle)) - text_height // 2
            
        else:  # rainbow
            # 彩虹效果
            x = center_x - text_width // 2
            y = center_y - text_height // 2
        
        # 绘制文本
        if animation_type == 'rainbow':
            # 彩虹文字效果
            for i, char in enumerate(text):
                char_x = x + i * (text_width // len(text))
                hue = (i * 360 // len(text) + frame_num * 10) % 360
                color = self.hsv_to_rgb(hue, 1.0, 1.0)
                draw.text((char_x, y), char, fill=color, font=font)
        else:
            # 普通文字效果
            text_color = colors[1] if len(colors) > 1 else '#FFFFFF'
            if animation_type == 'fade':
                # 添加透明度效果
                text_color = text_color + f"{alpha:02x}"
            
            draw.text((x, y), text, fill=text_color, font=font)
        
        # 添加一些装饰元素
        self.add_decorations(draw, frame_num, colors)
        
        return bg
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> str:
        """HSV转RGB"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def add_decorations(self, draw: ImageDraw.Draw, frame_num: int, colors: List[str]):
        """添加装饰元素"""
        # 添加一些随机的小图形
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(5, 20)
            color = random.choice(colors)
            
            shape_type = random.choice(['circle', 'star', 'square'])
            
            if shape_type == 'circle':
                draw.ellipse([x-size, y-size, x+size, y+size], fill=color, outline=None)
            elif shape_type == 'star':
                self.draw_star(draw, x, y, size, color)
            else:  # square
                draw.rectangle([x-size, y-size, x+size, y+size], fill=color, outline=None)
    
    def draw_star(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: str):
        """绘制星星"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size // 2
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, fill=color, outline=None)
    
    def generate_gif(self, text: str, output_path: str = "output.gif", 
                    num_frames: int = 20) -> str:
        """
        生成GIF
        
        Args:
            text: 输入文本
            output_path: 输出文件路径
            num_frames: 帧数
            
        Returns:
            生成的GIF文件路径
        """
        # 随机选择颜色主题和动画类型
        colors = self.get_random_theme()
        animation_type = self.get_random_animation()
        
        print(f"生成GIF: '{text}'")
        print(f"动画类型: {animation_type}")
        print(f"颜色主题: {colors}")
        print(f"帧数: {num_frames}")
        
        # 生成所有帧
        frames = []
        for i in range(num_frames):
            frame = self.create_text_frame(text, i, num_frames, animation_type, colors)
            frames.append(frame)
        
        # 保存为GIF
        if frames:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=self.duration,
                loop=0,
                optimize=True
            )
            print(f"GIF已保存到: {output_path}")
            return output_path
        else:
            raise ValueError("无法生成帧")
    
    def generate_multiple_gifs(self, texts: List[str], output_dir: str = "gifs") -> List[str]:
        """批量生成多个GIF"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        generated_files = []
        for i, text in enumerate(texts):
            output_path = os.path.join(output_dir, f"gif_{i+1}_{text[:10]}.gif")
            try:
                file_path = self.generate_gif(text, output_path)
                generated_files.append(file_path)
            except Exception as e:
                print(f"生成GIF失败 '{text}': {e}")
        
        return generated_files

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='文本转GIF生成器')
    parser.add_argument('text', nargs='?', help='要转换为GIF的文本')
    parser.add_argument('-o', '--output', default='output.gif', help='输出文件路径')
    parser.add_argument('-w', '--width', type=int, default=400, help='GIF宽度')
    parser.add_argument('--height', type=int, default=300, help='GIF高度')
    parser.add_argument('-f', '--frames', type=int, default=20, help='帧数')
    parser.add_argument('-d', '--duration', type=int, default=100, help='每帧持续时间(毫秒)')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = TextToGifGenerator(args.width, args.height, args.duration)
    
    if args.interactive:
        # 交互模式
        print("=== 文本转GIF生成器 ===")
        print("输入 'quit' 退出")
        
        while True:
            text = input("\n请输入要转换为GIF的文本: ").strip()
            if text.lower() == 'quit':
                break
            
            if text:
                try:
                    output_path = f"gif_{hash(text) % 10000}.gif"
                    generator.generate_gif(text, output_path, args.frames)
                except Exception as e:
                    print(f"生成失败: {e}")
    else:
        # 单次生成模式
        if not args.text:
            print("请提供要转换的文本，或使用 --interactive 进入交互模式")
            sys.exit(1)
        
        try:
            generator.generate_gif(args.text, args.output, args.frames)
        except Exception as e:
            print(f"生成失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()