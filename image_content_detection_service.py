#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像内容检测服务
集成阿里云图像内容检测API，提供多种检测功能
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import configparser

from aliyun_image_detection import AliyunImageDetectionClient, create_client_from_config


class ImageContentDetectionService:
    """图像内容检测服务"""
    
    def __init__(self, config_file: str = "config.ini"):
        """
        初始化图像内容检测服务
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # 初始化阿里云客户端
        self.client = create_client_from_config(config_file)
        if not self.client:
            self.logger.error("阿里云客户端初始化失败")
            raise RuntimeError("无法初始化阿里云客户端")
        
        # 获取配置参数
        self.detection_types = self._parse_detection_types()
        self.confidence_threshold = self.config.getfloat('aliyun_image_detection', 'confidence_threshold', fallback=0.8)
        self.async_detection = self.config.getboolean('aliyun_image_detection', 'async_detection', fallback=False)
        
        self.logger.info("图像内容检测服务初始化成功")
    
    def _setup_logging(self):
        """设置日志"""
        log_level = self.config.get('logging', 'level', fallback='INFO')
        log_file = self.config.get('logging', 'log_file', fallback='image_detection.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _parse_detection_types(self) -> List[str]:
        """解析检测类型配置"""
        types_str = self.config.get('aliyun_image_detection', 'detection_types', fallback='porn,terrorism,ad')
        return [t.strip() for t in types_str.split(',') if t.strip()]
    
    def detect_single_image(self, 
                           image_input: Union[str, bytes], 
                           detection_types: List[str] = None,
                           confidence_threshold: float = None) -> Dict:
        """
        检测单张图像
        
        Args:
            image_input: 图片路径、URL或字节数据
            detection_types: 检测类型列表，None则使用配置的默认类型
            confidence_threshold: 置信度阈值，None则使用配置的默认值
            
        Returns:
            检测结果字典
        """
        if detection_types is None:
            detection_types = self.detection_types
        
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
        
        self.logger.info(f"开始检测图像: {image_input if isinstance(image_input, str) else 'bytes data'}")
        
        try:
            result = self.client.detect_image_content(
                image_input, 
                detection_types, 
                confidence_threshold
            )
            
            # 添加元数据
            result['metadata'] = {
                'detection_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'detection_types': detection_types,
                'confidence_threshold': confidence_threshold,
                'service_version': '1.0.0'
            }
            
            self.logger.info(f"图像检测完成: {result.get('summary', {}).get('risk_level', 'UNKNOWN')}")
            return result
            
        except Exception as e:
            self.logger.error(f"图像检测失败: {e}")
            return {
                "success": False,
                "error": f"检测失败: {e}",
                "metadata": {
                    'detection_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'service_version': '1.0.0'
                }
            }
    
    def detect_batch_images(self, 
                           image_paths: List[str], 
                           detection_types: List[str] = None,
                           confidence_threshold: float = None) -> List[Dict]:
        """
        批量检测图像
        
        Args:
            image_paths: 图片路径列表
            detection_types: 检测类型列表
            confidence_threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        self.logger.info(f"开始批量检测 {len(image_paths)} 张图像")
        
        results = []
        for i, image_path in enumerate(image_paths, 1):
            self.logger.info(f"检测进度: {i}/{len(image_paths)} - {image_path}")
            
            try:
                result = self.detect_single_image(image_path, detection_types, confidence_threshold)
                result['batch_index'] = i
                results.append(result)
            except Exception as e:
                self.logger.error(f"批量检测失败 {image_path}: {e}")
                results.append({
                    "image_path": image_path,
                    "success": False,
                    "error": f"检测失败: {e}",
                    "batch_index": i,
                    "metadata": {
                        'detection_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'service_version': '1.0.0'
                    }
                })
        
        # 生成批量检测摘要
        summary = self._generate_batch_summary(results)
        self.logger.info(f"批量检测完成: {summary}")
        
        return results
    
    def _generate_batch_summary(self, results: List[Dict]) -> Dict:
        """生成批量检测摘要"""
        total_images = len(results)
        successful_detections = sum(1 for r in results if r.get('success', False))
        failed_detections = total_images - successful_detections
        
        # 统计违规情况
        violations_by_type = {}
        risk_levels = {'SAFE': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
        
        for result in results:
            if result.get('success', False) and 'summary' in result:
                summary = result['summary']
                risk_level = summary.get('risk_level', 'UNKNOWN')
                if risk_level in risk_levels:
                    risk_levels[risk_level] += 1
                
                for violation in summary.get('violations', []):
                    scene = violation['scene']
                    if scene not in violations_by_type:
                        violations_by_type[scene] = 0
                    violations_by_type[scene] += 1
        
        return {
            'total_images': total_images,
            'successful_detections': successful_detections,
            'failed_detections': failed_detections,
            'success_rate': successful_detections / total_images if total_images > 0 else 0,
            'risk_level_distribution': risk_levels,
            'violations_by_type': violations_by_type
        }
    
    def detect_directory(self, 
                        directory_path: str, 
                        supported_formats: List[str] = None,
                        detection_types: List[str] = None,
                        confidence_threshold: float = None) -> List[Dict]:
        """
        检测目录中的所有图像
        
        Args:
            directory_path: 目录路径
            supported_formats: 支持的图像格式，默认['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            detection_types: 检测类型列表
            confidence_threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        if supported_formats is None:
            supported_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        
        # 查找所有图像文件
        image_paths = []
        directory = Path(directory_path)
        
        if not directory.exists():
            self.logger.error(f"目录不存在: {directory_path}")
            return []
        
        for format_ext in supported_formats:
            pattern = f"**/*.{format_ext}"
            image_paths.extend(directory.glob(pattern))
            pattern = f"**/*.{format_ext.upper()}"
            image_paths.extend(directory.glob(pattern))
        
        image_paths = [str(p) for p in image_paths]
        
        self.logger.info(f"在目录 {directory_path} 中找到 {len(image_paths)} 个图像文件")
        
        if not image_paths:
            self.logger.warning(f"目录 {directory_path} 中没有找到支持的图像文件")
            return []
        
        return self.detect_batch_images(image_paths, detection_types, confidence_threshold)
    
    def get_detection_statistics(self, results: List[Dict]) -> Dict:
        """
        获取检测统计信息
        
        Args:
            results: 检测结果列表
            
        Returns:
            统计信息字典
        """
        if not results:
            return {}
        
        stats = {
            'total_images': len(results),
            'successful_detections': 0,
            'failed_detections': 0,
            'risk_levels': {'SAFE': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0},
            'violation_types': {},
            'confidence_scores': {},
            'detection_times': []
        }
        
        for result in results:
            if result.get('success', False):
                stats['successful_detections'] += 1
                
                if 'summary' in result:
                    summary = result['summary']
                    risk_level = summary.get('risk_level', 'UNKNOWN')
                    if risk_level in stats['risk_levels']:
                        stats['risk_levels'][risk_level] += 1
                    
                    # 统计违规类型
                    for violation in summary.get('violations', []):
                        scene = violation['scene']
                        if scene not in stats['violation_types']:
                            stats['violation_types'][scene] = 0
                        stats['violation_types'][scene] += 1
                    
                    # 统计置信度分数
                    for scene, confidence in summary.get('confidence_scores', {}).items():
                        if scene not in stats['confidence_scores']:
                            stats['confidence_scores'][scene] = []
                        stats['confidence_scores'][scene].append(confidence)
                
                # 记录检测时间
                if 'metadata' in result and 'detection_time' in result['metadata']:
                    stats['detection_times'].append(result['metadata']['detection_time'])
            else:
                stats['failed_detections'] += 1
        
        # 计算平均置信度
        for scene, scores in stats['confidence_scores'].items():
            if scores:
                stats['confidence_scores'][scene] = {
                    'average': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'count': len(scores)
                }
        
        return stats
    
    def save_results(self, results: List[Dict], output_file: str = None) -> str:
        """
        保存检测结果到文件
        
        Args:
            results: 检测结果列表
            output_file: 输出文件路径，None则自动生成
            
        Returns:
            保存的文件路径
        """
        if output_file is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = f"image_detection_results_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"检测结果已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            raise
    
    def generate_report(self, results: List[Dict], output_file: str = None) -> str:
        """
        生成检测报告
        
        Args:
            results: 检测结果列表
            output_file: 输出文件路径，None则自动生成
            
        Returns:
            报告文件路径
        """
        if output_file is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = f"image_detection_report_{timestamp}.txt"
        
        try:
            stats = self.get_detection_statistics(results)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("图像内容检测报告\n")
                f.write("=" * 60 + "\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"检测图像总数: {stats.get('total_images', 0)}\n")
                f.write(f"成功检测: {stats.get('successful_detections', 0)}\n")
                f.write(f"检测失败: {stats.get('failed_detections', 0)}\n")
                f.write(f"成功率: {stats.get('successful_detections', 0) / stats.get('total_images', 1) * 100:.2f}%\n\n")
                
                f.write("风险等级分布:\n")
                f.write("-" * 30 + "\n")
                for level, count in stats.get('risk_levels', {}).items():
                    f.write(f"{level}: {count}\n")
                
                f.write("\n违规类型统计:\n")
                f.write("-" * 30 + "\n")
                for violation_type, count in stats.get('violation_types', {}).items():
                    f.write(f"{violation_type}: {count}\n")
                
                f.write("\n置信度统计:\n")
                f.write("-" * 30 + "\n")
                for scene, conf_stats in stats.get('confidence_scores', {}).items():
                    f.write(f"{scene}:\n")
                    f.write(f"  平均: {conf_stats['average']:.3f}\n")
                    f.write(f"  最小: {conf_stats['min']:.3f}\n")
                    f.write(f"  最大: {conf_stats['max']:.3f}\n")
                    f.write(f"  数量: {conf_stats['count']}\n")
                
                f.write("\n详细检测结果:\n")
                f.write("=" * 60 + "\n")
                for i, result in enumerate(results, 1):
                    f.write(f"\n{i}. {result.get('image_path', 'Unknown')}\n")
                    f.write("-" * 40 + "\n")
                    if result.get('success', False):
                        summary = result.get('summary', {})
                        f.write(f"风险等级: {summary.get('risk_level', 'UNKNOWN')}\n")
                        f.write(f"检测场景数: {summary.get('total_scenes', 0)}\n")
                        
                        if summary.get('violations'):
                            f.write("违规内容:\n")
                            for violation in summary['violations']:
                                f.write(f"  - {violation['scene']}: {violation['suggestion']} (置信度: {violation['confidence']:.3f})\n")
                        else:
                            f.write("无违规内容\n")
                    else:
                        f.write(f"检测失败: {result.get('error', 'Unknown error')}\n")
            
            self.logger.info(f"检测报告已生成: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise


def main():
    """主函数 - 演示服务使用"""
    try:
        # 创建服务实例
        service = ImageContentDetectionService()
        
        print("图像内容检测服务已启动")
        print("支持的检测类型:", service.detection_types)
        print("置信度阈值:", service.confidence_threshold)
        
        # 示例：检测单张图像（需要提供真实的图片路径）
        # result = service.detect_single_image("test_image.jpg")
        # print("检测结果:", json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"服务启动失败: {e}")


if __name__ == "__main__":
    main()