#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像内容检测演示脚本
展示如何使用阿里云图像内容检测服务
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_content_detection_service import ImageContentDetectionService


def demo_single_image_detection(service, image_path: str):
    """演示单张图像检测"""
    print("\n" + "="*60)
    print("单张图像检测演示")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return
    
    print(f"检测图像: {image_path}")
    print("检测类型:", service.detection_types)
    print("置信度阈值:", service.confidence_threshold)
    print("\n开始检测...")
    
    start_time = time.time()
    result = service.detect_single_image(image_path)
    end_time = time.time()
    
    print(f"检测耗时: {end_time - start_time:.2f} 秒")
    print("\n检测结果:")
    print("-" * 40)
    
    if result.get('success', False):
        summary = result.get('summary', {})
        print(f"风险等级: {summary.get('risk_level', 'UNKNOWN')}")
        print(f"检测场景数: {summary.get('total_scenes', 0)}")
        
        if summary.get('violations'):
            print("\n违规内容:")
            for violation in summary['violations']:
                print(f"  - {violation['scene']}: {violation['suggestion']} (置信度: {violation['confidence']:.3f})")
        else:
            print("无违规内容")
        
        print("\n详细检测结果:")
        for scene, detection in result.get('detections', {}).items():
            print(f"  {scene}: {detection['suggestion']} (置信度: {detection['confidence']:.3f})")
    else:
        print(f"检测失败: {result.get('error', 'Unknown error')}")
    
    return result


def demo_batch_detection(service, image_directory: str):
    """演示批量图像检测"""
    print("\n" + "="*60)
    print("批量图像检测演示")
    print("="*60)
    
    if not os.path.exists(image_directory):
        print(f"错误: 目录不存在: {image_directory}")
        return
    
    print(f"检测目录: {image_directory}")
    print("支持的格式: jpg, jpeg, png, gif, bmp, webp")
    print("\n开始批量检测...")
    
    start_time = time.time()
    results = service.detect_directory(image_directory)
    end_time = time.time()
    
    print(f"批量检测耗时: {end_time - start_time:.2f} 秒")
    print(f"检测图像数量: {len(results)}")
    
    if not results:
        print("没有找到支持的图像文件")
        return
    
    # 生成统计信息
    stats = service.get_detection_statistics(results)
    print("\n检测统计:")
    print("-" * 40)
    print(f"总图像数: {stats.get('total_images', 0)}")
    print(f"成功检测: {stats.get('successful_detections', 0)}")
    print(f"检测失败: {stats.get('failed_detections', 0)}")
    print(f"成功率: {stats.get('successful_detections', 0) / stats.get('total_images', 1) * 100:.2f}%")
    
    print("\n风险等级分布:")
    for level, count in stats.get('risk_levels', {}).items():
        print(f"  {level}: {count}")
    
    if stats.get('violation_types'):
        print("\n违规类型统计:")
        for violation_type, count in stats.get('violation_types', {}).items():
            print(f"  {violation_type}: {count}")
    
    # 显示高风险图像
    high_risk_images = []
    for result in results:
        if result.get('success', False):
            summary = result.get('summary', {})
            if summary.get('risk_level') in ['HIGH', 'MEDIUM']:
                high_risk_images.append(result)
    
    if high_risk_images:
        print(f"\n发现 {len(high_risk_images)} 个中高风险图像:")
        for result in high_risk_images:
            print(f"  - {result.get('image_path', 'Unknown')}: {result.get('summary', {}).get('risk_level', 'UNKNOWN')}")
    
    return results


def demo_specific_detection_types(service, image_path: str):
    """演示特定检测类型"""
    print("\n" + "="*60)
    print("特定检测类型演示")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return
    
    # 测试不同的检测类型
    detection_types = [
        ['porn'],
        ['terrorism'],
        ['ad'],
        ['porn', 'terrorism'],
        ['porn', 'terrorism', 'ad']
    ]
    
    for types in detection_types:
        print(f"\n检测类型: {', '.join(types)}")
        print("-" * 30)
        
        result = service.detect_single_image(image_path, types)
        
        if result.get('success', False):
            summary = result.get('summary', {})
            print(f"风险等级: {summary.get('risk_level', 'UNKNOWN')}")
            
            if summary.get('violations'):
                for violation in summary['violations']:
                    print(f"  违规: {violation['scene']} - {violation['suggestion']} (置信度: {violation['confidence']:.3f})")
            else:
                print("  无违规内容")
        else:
            print(f"  检测失败: {result.get('error', 'Unknown error')}")


def demo_confidence_threshold(service, image_path: str):
    """演示不同置信度阈值的影响"""
    print("\n" + "="*60)
    print("置信度阈值演示")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"错误: 图像文件不存在: {image_path}")
        return
    
    thresholds = [0.5, 0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        print(f"\n置信度阈值: {threshold}")
        print("-" * 30)
        
        result = service.detect_single_image(image_path, confidence_threshold=threshold)
        
        if result.get('success', False):
            summary = result.get('summary', {})
            print(f"风险等级: {summary.get('risk_level', 'UNKNOWN')}")
            print(f"违规数量: {len(summary.get('violations', []))}")
            
            for violation in summary.get('violations', []):
                print(f"  {violation['scene']}: {violation['suggestion']} (置信度: {violation['confidence']:.3f})")
        else:
            print(f"检测失败: {result.get('error', 'Unknown error')}")


def create_sample_images():
    """创建示例图像（用于演示）"""
    print("\n" + "="*60)
    print("创建示例图像")
    print("="*60)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # 创建示例目录
        sample_dir = Path("sample_images")
        sample_dir.mkdir(exist_ok=True)
        
        # 创建一些示例图像
        images = [
            {
                "name": "safe_image.jpg",
                "text": "Safe Content",
                "color": (0, 255, 0)
            },
            {
                "name": "test_image.jpg", 
                "text": "Test Image",
                "color": (255, 0, 0)
            },
            {
                "name": "sample.png",
                "text": "Sample",
                "color": (0, 0, 255)
            }
        ]
        
        for img_info in images:
            # 创建图像
            img = Image.new('RGB', (400, 300), color=img_info['color'])
            draw = ImageDraw.Draw(img)
            
            # 添加文字
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            text = img_info['text']
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (400 - text_width) // 2
            y = (300 - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            # 保存图像
            img_path = sample_dir / img_info['name']
            img.save(img_path)
            print(f"创建示例图像: {img_path}")
        
        print(f"\n示例图像已创建在: {sample_dir.absolute()}")
        return str(sample_dir.absolute())
        
    except ImportError:
        print("PIL未安装，无法创建示例图像")
        return None
    except Exception as e:
        print(f"创建示例图像失败: {e}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='阿里云图像内容检测演示')
    parser.add_argument('--image', '-i', help='单张图像路径')
    parser.add_argument('--directory', '-d', help='图像目录路径')
    parser.add_argument('--create-samples', action='store_true', help='创建示例图像')
    parser.add_argument('--demo-types', action='store_true', help='演示不同检测类型')
    parser.add_argument('--demo-threshold', action='store_true', help='演示不同置信度阈值')
    parser.add_argument('--save-results', action='store_true', help='保存检测结果')
    
    args = parser.parse_args()
    
    try:
        # 初始化服务
        print("初始化图像内容检测服务...")
        service = ImageContentDetectionService()
        print("服务初始化成功!")
        
        # 创建示例图像
        if args.create_samples:
            sample_dir = create_sample_images()
            if sample_dir:
                print(f"\n使用示例图像进行演示...")
                demo_batch_detection(service, sample_dir)
                return
        
        # 单张图像检测
        if args.image:
            result = demo_single_image_detection(service, args.image)
            
            if args.demo_types:
                demo_specific_detection_types(service, args.image)
            
            if args.demo_threshold:
                demo_confidence_threshold(service, args.image)
            
            if args.save_results and result:
                # 保存结果
                results_file = service.save_results([result])
                report_file = service.generate_report([result])
                print(f"\n结果已保存:")
                print(f"  详细结果: {results_file}")
                print(f"  检测报告: {report_file}")
        
        # 批量检测
        elif args.directory:
            results = demo_batch_detection(service, args.directory)
            
            if args.save_results and results:
                # 保存结果
                results_file = service.save_results(results)
                report_file = service.generate_report(results)
                print(f"\n结果已保存:")
                print(f"  详细结果: {results_file}")
                print(f"  检测报告: {report_file}")
        
        # 默认演示
        else:
            print("\n使用方法:")
            print("  python demo_image_detection.py --create-samples  # 创建示例图像并演示")
            print("  python demo_image_detection.py --image <图片路径>  # 检测单张图像")
            print("  python demo_image_detection.py --directory <目录路径>  # 批量检测")
            print("  python demo_image_detection.py --image <图片路径> --demo-types  # 演示不同检测类型")
            print("  python demo_image_detection.py --image <图片路径> --demo-threshold  # 演示不同置信度")
            print("  python demo_image_detection.py --image <图片路径> --save-results  # 保存检测结果")
    
    except Exception as e:
        print(f"演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()