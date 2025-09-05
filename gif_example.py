#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转GIF生成器使用示例
"""

from text_to_gif_generator import TextToGifGenerator
import os

def main():
    """示例：生成多个GIF"""
    print("=== 文本转GIF生成器示例 ===\n")
    
    # 创建生成器实例
    generator = TextToGifGenerator(width=500, height=300, duration=150)
    
    # 示例文本列表
    sample_texts = [
        "Hello World!",
        "你好世界！",
        "Python GIF Generator",
        "🎉 生日快乐！",
        "Amazing Animation",
        "动态文字效果",
        "Random GIF Creator",
        "✨ 魔法文字 ✨"
    ]
    
    print("正在生成示例GIF...")
    
    # 生成单个GIF
    print("\n1. 生成单个GIF:")
    try:
        output_file = generator.generate_gif("Welcome to GIF Generator!", "welcome.gif")
        print(f"✅ 成功生成: {output_file}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
    
    # 批量生成多个GIF
    print("\n2. 批量生成多个GIF:")
    try:
        generated_files = generator.generate_multiple_gifs(sample_texts, "sample_gifs")
        print(f"✅ 成功生成 {len(generated_files)} 个GIF文件:")
        for file_path in generated_files:
            print(f"   - {file_path}")
    except Exception as e:
        print(f"❌ 批量生成失败: {e}")
    
    # 生成不同尺寸的GIF
    print("\n3. 生成不同尺寸的GIF:")
    sizes = [
        (200, 100, "small.gif"),
        (400, 200, "medium.gif"),
        (800, 400, "large.gif")
    ]
    
    for width, height, filename in sizes:
        try:
            small_generator = TextToGifGenerator(width, height, 100)
            small_generator.generate_gif(f"Size: {width}x{height}", filename)
            print(f"✅ 生成 {filename} ({width}x{height})")
        except Exception as e:
            print(f"❌ 生成 {filename} 失败: {e}")
    
    print("\n=== 示例完成 ===")
    print("您可以使用以下命令来使用生成器:")
    print("python text_to_gif_generator.py '您的文本'")
    print("python text_to_gif_generator.py --interactive  # 交互模式")

if __name__ == "__main__":
    main()