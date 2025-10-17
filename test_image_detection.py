#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像内容检测测试脚本
测试阿里云图像内容检测服务的各项功能
"""

import os
import sys
import json
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aliyun_image_detection import AliyunImageDetectionClient, create_client_from_config
from image_content_detection_service import ImageContentDetectionService


class TestAliyunImageDetectionClient(unittest.TestCase):
    """测试阿里云图像检测客户端"""
    
    def setUp(self):
        """测试前准备"""
        self.access_key_id = "test_access_key"
        self.access_key_secret = "test_secret"
        self.region = "cn-shanghai"
        
        # 模拟客户端
        with patch('aliyun_image_detection.AcsClient'):
            self.client = AliyunImageDetectionClient(
                self.access_key_id, 
                self.access_key_secret, 
                self.region
            )
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        self.assertEqual(self.client.access_key_id, self.access_key_id)
        self.assertEqual(self.client.access_key_secret, self.access_key_secret)
        self.assertEqual(self.client.region, self.region)
        self.assertIsNotNone(self.client.client)
    
    def test_encode_image(self):
        """测试图像编码"""
        # 创建临时测试图像
        test_image_path = "test_image.jpg"
        with open(test_image_path, 'wb') as f:
            f.write(b"fake_image_data")
        
        try:
            encoded = self.client._encode_image(test_image_path)
            self.assertIsInstance(encoded, str)
            self.assertTrue(len(encoded) > 0)
        finally:
            # 清理测试文件
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
    
    def test_is_url(self):
        """测试URL判断"""
        self.assertTrue(self.client._is_url("https://example.com/image.jpg"))
        self.assertTrue(self.client._is_url("http://example.com/image.jpg"))
        self.assertFalse(self.client._is_url("/path/to/image.jpg"))
        self.assertFalse(self.client._is_url("image.jpg"))
    
    @patch('aliyun_image_detection.time.time')
    def test_detect_image_content(self, mock_time):
        """测试图像内容检测"""
        mock_time.return_value = 1234567890
        
        # 模拟API响应
        mock_response = {
            "data": [{
                "results": [{
                    "scene": "porn",
                    "suggestion": "pass",
                    "confidence": 0.1
                }]
            }]
        }
        
        # 模拟客户端响应
        self.client.client.do_action_with_exception = Mock(return_value=json.dumps(mock_response).encode())
        
        # 测试检测
        result = self.client.detect_image_content("test_image.jpg", ["porn"])
        
        self.assertTrue(result["success"])
        self.assertIn("detections", result)
        self.assertIn("summary", result)
        self.assertEqual(result["summary"]["risk_level"], "SAFE")
    
    def test_detect_porn(self):
        """测试色情内容检测"""
        with patch.object(self.client, 'detect_image_content') as mock_detect:
            mock_detect.return_value = {"success": True, "detections": {}}
            
            result = self.client.detect_porn("test_image.jpg")
            mock_detect.assert_called_once_with("test_image.jpg", ["porn"], 0.8)
            self.assertTrue(result["success"])
    
    def test_detect_terrorism(self):
        """测试暴恐内容检测"""
        with patch.object(self.client, 'detect_image_content') as mock_detect:
            mock_detect.return_value = {"success": True, "detections": {}}
            
            result = self.client.detect_terrorism("test_image.jpg")
            mock_detect.assert_called_once_with("test_image.jpg", ["terrorism"], 0.8)
            self.assertTrue(result["success"])
    
    def test_batch_detect(self):
        """测试批量检测"""
        with patch.object(self.client, 'detect_image_content') as mock_detect:
            mock_detect.return_value = {"success": True, "detections": {}}
            
            image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
            results = self.client.batch_detect(image_paths)
            
            self.assertEqual(len(results), 3)
            self.assertEqual(mock_detect.call_count, 3)
            
            for i, result in enumerate(results):
                self.assertTrue(result["success"])
                self.assertEqual(result["image_path"], image_paths[i])


class TestImageContentDetectionService(unittest.TestCase):
    """测试图像内容检测服务"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试配置文件
        self.test_config = """
[aliyun_image_detection]
access_key_id = test_key
access_key_secret = test_secret
region = cn-shanghai
detection_types = porn,terrorism,ad
confidence_threshold = 0.8
async_detection = false

[logging]
level = INFO
log_file = test.log
"""
        
        with open("test_config.ini", "w", encoding="utf-8") as f:
            f.write(self.test_config)
        
        # 模拟客户端
        with patch('image_content_detection_service.create_client_from_config') as mock_create_client:
            mock_client = Mock()
            mock_create_client.return_value = mock_client
            self.service = ImageContentDetectionService("test_config.ini")
            self.service.client = mock_client
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists("test_config.ini"):
            os.remove("test_config.ini")
        if os.path.exists("test.log"):
            os.remove("test.log")
    
    def test_service_initialization(self):
        """测试服务初始化"""
        self.assertIsNotNone(self.service.client)
        self.assertEqual(self.service.detection_types, ['porn', 'terrorism', 'ad'])
        self.assertEqual(self.service.confidence_threshold, 0.8)
        self.assertFalse(self.service.async_detection)
    
    def test_parse_detection_types(self):
        """测试检测类型解析"""
        types = self.service._parse_detection_types()
        self.assertEqual(types, ['porn', 'terrorism', 'ad'])
    
    def test_detect_single_image(self):
        """测试单张图像检测"""
        # 模拟客户端响应
        mock_result = {
            "success": True,
            "detections": {
                "porn": {"suggestion": "pass", "confidence": 0.1, "is_violation": False}
            },
            "summary": {
                "risk_level": "SAFE",
                "total_scenes": 1,
                "violations": []
            }
        }
        
        self.service.client.detect_image_content = Mock(return_value=mock_result)
        
        result = self.service.detect_single_image("test_image.jpg")
        
        self.assertTrue(result["success"])
        self.assertIn("metadata", result)
        self.assertEqual(result["summary"]["risk_level"], "SAFE")
    
    def test_detect_batch_images(self):
        """测试批量图像检测"""
        # 模拟客户端响应
        mock_result = {
            "success": True,
            "detections": {},
            "summary": {"risk_level": "SAFE", "total_scenes": 0, "violations": []}
        }
        
        self.service.client.detect_image_content = Mock(return_value=mock_result)
        
        image_paths = ["image1.jpg", "image2.jpg"]
        results = self.service.detect_batch_images(image_paths)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["success"] for r in results))
    
    def test_detect_directory(self):
        """测试目录检测"""
        # 创建测试目录和图像
        test_dir = Path("test_images")
        test_dir.mkdir(exist_ok=True)
        
        try:
            # 创建测试图像文件
            (test_dir / "test1.jpg").touch()
            (test_dir / "test2.png").touch()
            (test_dir / "test3.txt").touch()  # 非图像文件
            
            # 模拟客户端响应
            mock_result = {
                "success": True,
                "detections": {},
                "summary": {"risk_level": "SAFE", "total_scenes": 0, "violations": []}
            }
            
            self.service.client.detect_image_content = Mock(return_value=mock_result)
            
            results = self.service.detect_directory(str(test_dir))
            
            # 应该只检测图像文件
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r["success"] for r in results))
            
        finally:
            # 清理测试目录
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def test_get_detection_statistics(self):
        """测试检测统计"""
        results = [
            {
                "success": True,
                "summary": {
                    "risk_level": "SAFE",
                    "violations": [],
                    "confidence_scores": {"porn": 0.1}
                }
            },
            {
                "success": True,
                "summary": {
                    "risk_level": "HIGH",
                    "violations": [{"scene": "porn", "suggestion": "block", "confidence": 0.9}],
                    "confidence_scores": {"porn": 0.9}
                }
            },
            {
                "success": False,
                "error": "Test error"
            }
        ]
        
        stats = self.service.get_detection_statistics(results)
        
        self.assertEqual(stats["total_images"], 3)
        self.assertEqual(stats["successful_detections"], 2)
        self.assertEqual(stats["failed_detections"], 1)
        self.assertEqual(stats["risk_levels"]["SAFE"], 1)
        self.assertEqual(stats["risk_levels"]["HIGH"], 1)
        self.assertEqual(stats["violation_types"]["porn"], 1)
    
    def test_save_results(self):
        """测试保存结果"""
        results = [{"test": "data"}]
        
        output_file = self.service.save_results(results)
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, results)
        
        # 清理测试文件
        os.remove(output_file)
    
    def test_generate_report(self):
        """测试生成报告"""
        results = [
            {
                "success": True,
                "image_path": "test.jpg",
                "summary": {
                    "risk_level": "SAFE",
                    "total_scenes": 1,
                    "violations": []
                }
            }
        ]
        
        report_file = self.service.generate_report(results)
        
        self.assertTrue(os.path.exists(report_file))
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        self.assertIn("图像内容检测报告", report_content)
        self.assertIn("test.jpg", report_content)
        
        # 清理测试文件
        os.remove(report_file)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_create_client_from_config(self):
        """测试从配置文件创建客户端"""
        # 创建测试配置文件
        test_config = """
[aliyun_image_detection]
access_key_id = test_key
access_key_secret = test_secret
region = cn-shanghai
"""
        
        with open("test_config.ini", "w", encoding="utf-8") as f:
            f.write(test_config)
        
        try:
            with patch('aliyun_image_detection.AcsClient'):
                client = create_client_from_config("test_config.ini")
                self.assertIsNotNone(client)
                self.assertEqual(client.access_key_id, "test_key")
                self.assertEqual(client.access_key_secret, "test_secret")
                self.assertEqual(client.region, "cn-shanghai")
        finally:
            if os.path.exists("test_config.ini"):
                os.remove("test_config.ini")
    
    def test_create_client_with_placeholder_config(self):
        """测试使用占位符配置创建客户端"""
        # 创建包含占位符的配置文件
        test_config = """
[aliyun_image_detection]
access_key_id = YOUR_ACCESS_KEY_ID
access_key_secret = YOUR_ACCESS_KEY_SECRET
region = cn-shanghai
"""
        
        with open("test_config.ini", "w", encoding="utf-8") as f:
            f.write(test_config)
        
        try:
            client = create_client_from_config("test_config.ini")
            self.assertIsNone(client)
        finally:
            if os.path.exists("test_config.ini"):
                os.remove("test_config.ini")


def run_performance_test():
    """运行性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    # 创建测试图像
    test_images = []
    for i in range(5):
        img_path = f"perf_test_{i}.jpg"
        with open(img_path, 'wb') as f:
            f.write(b"fake_image_data" * 1000)  # 创建较大的测试文件
        test_images.append(img_path)
    
    try:
        # 测试批量检测性能
        with patch('image_content_detection_service.create_client_from_config') as mock_create_client:
            mock_client = Mock()
            mock_client.detect_image_content = Mock(return_value={
                "success": True,
                "detections": {},
                "summary": {"risk_level": "SAFE", "total_scenes": 0, "violations": []}
            })
            mock_create_client.return_value = mock_client
            
            service = ImageContentDetectionService("test_config.ini")
            service.client = mock_client
            
            start_time = time.time()
            results = service.detect_batch_images(test_images)
            end_time = time.time()
            
            print(f"批量检测 {len(test_images)} 张图像耗时: {end_time - start_time:.2f} 秒")
            print(f"平均每张图像: {(end_time - start_time) / len(test_images):.3f} 秒")
            print(f"检测成功率: {sum(1 for r in results if r['success']) / len(results) * 100:.1f}%")
    
    finally:
        # 清理测试文件
        for img_path in test_images:
            if os.path.exists(img_path):
                os.remove(img_path)


def main():
    """主函数"""
    print("开始图像内容检测测试...")
    
    # 运行单元测试
    print("\n运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    run_performance_test()
    
    print("\n测试完成!")


if __name__ == "__main__":
    main()