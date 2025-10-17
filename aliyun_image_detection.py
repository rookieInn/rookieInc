#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云图像内容检测客户端
支持多种内容检测类型：色情、暴恐、广告、直播、Logo、OCR、人脸、二维码、场景等
"""

import os
import base64
import json
import logging
import time
from typing import Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
    from aliyunsdkgreen.request.v20180509 import ImageSyncScanRequest
    from aliyunsdkgreen.request.v20180509 import ImageAsyncScanRequest
    from aliyunsdkimageaudit.request.v20191230 import ScanImageRequest
    from aliyunsdkviapi.request.v20230117 import RecognizeImageColorRequest
except ImportError as e:
    print(f"警告: 阿里云SDK未安装，请运行: pip install aliyun-python-sdk-core aliyun-python-sdk-green aliyun-python-sdk-imageaudit aliyun-python-sdk-viapi")
    print(f"错误详情: {e}")


class AliyunImageDetectionClient:
    """阿里云图像内容检测客户端"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, region: str = "cn-shanghai"):
        """
        初始化阿里云图像检测客户端
        
        Args:
            access_key_id: 阿里云访问密钥ID
            access_key_secret: 阿里云访问密钥Secret
            region: 地域，默认为cn-shanghai
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        
        # 初始化客户端
        try:
            self.client = AcsClient(access_key_id, access_key_secret, region)
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"初始化阿里云客户端失败: {e}")
            raise
    
    def _encode_image(self, image_path: str) -> str:
        """
        将图片文件编码为base64字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片字符串
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            self.logger.error(f"图片编码失败: {e}")
            raise
    
    def _is_url(self, image_input: str) -> bool:
        """
        判断输入是否为URL
        
        Args:
            image_input: 图片输入（路径或URL）
            
        Returns:
            是否为URL
        """
        try:
            result = urlparse(image_input)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def detect_image_content(self, 
                           image_input: Union[str, bytes], 
                           detection_types: List[str] = None,
                           confidence_threshold: float = 0.8) -> Dict:
        """
        检测图像内容
        
        Args:
            image_input: 图片路径、URL或字节数据
            detection_types: 检测类型列表，如['porn', 'terrorism', 'ad']
            confidence_threshold: 置信度阈值
            
        Returns:
            检测结果字典
        """
        if detection_types is None:
            detection_types = ['porn', 'terrorism', 'ad']
        
        try:
            # 处理不同类型的输入
            if isinstance(image_input, bytes):
                image_data = base64.b64encode(image_input).decode('utf-8')
            elif self._is_url(image_input):
                # 对于URL，直接使用URL
                image_data = image_input
            else:
                # 对于文件路径，编码为base64
                image_data = self._encode_image(image_input)
            
            # 构建请求
            request = ImageSyncScanRequest.ImageSyncScanRequest()
            request.set_accept_format('json')
            
            # 设置检测任务
            tasks = []
            for detection_type in detection_types:
                task = {
                    "dataId": f"img_{detection_type}_{hash(image_data) % 100000}",
                    "url": image_data if self._is_url(image_input) else None,
                    "image": image_data if not self._is_url(image_input) else None,
                    "time": int(time.time() * 1000)
                }
                tasks.append(task)
            
            request.set_content(json.dumps({
                "scenes": detection_types,
                "tasks": tasks
            }))
            
            # 发送请求
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))
            
            # 处理结果
            return self._process_detection_result(result, confidence_threshold)
            
        except ClientException as e:
            self.logger.error(f"客户端错误: {e}")
            return {"error": f"客户端错误: {e.message}", "success": False}
        except ServerException as e:
            self.logger.error(f"服务端错误: {e}")
            return {"error": f"服务端错误: {e.message}", "success": False}
        except Exception as e:
            self.logger.error(f"检测失败: {e}")
            return {"error": f"检测失败: {e}", "success": False}
    
    def _process_detection_result(self, result: Dict, confidence_threshold: float) -> Dict:
        """
        处理检测结果
        
        Args:
            result: 原始检测结果
            confidence_threshold: 置信度阈值
            
        Returns:
            处理后的结果
        """
        processed_result = {
            "success": True,
            "detections": {},
            "summary": {
                "total_scenes": 0,
                "violations": [],
                "confidence_scores": {}
            }
        }
        
        try:
            if "data" in result:
                for item in result["data"]:
                    if "results" in item:
                        for scene_result in item["results"]:
                            scene = scene_result.get("scene", "")
                            suggestion = scene_result.get("suggestion", "")
                            confidence = scene_result.get("confidence", 0.0)
                            
                            processed_result["detections"][scene] = {
                                "suggestion": suggestion,
                                "confidence": confidence,
                                "is_violation": suggestion in ["block", "review"] and confidence >= confidence_threshold
                            }
                            
                            processed_result["summary"]["total_scenes"] += 1
                            processed_result["summary"]["confidence_scores"][scene] = confidence
                            
                            if suggestion in ["block", "review"] and confidence >= confidence_threshold:
                                processed_result["summary"]["violations"].append({
                                    "scene": scene,
                                    "suggestion": suggestion,
                                    "confidence": confidence
                                })
            
            # 计算总体风险等级
            if processed_result["summary"]["violations"]:
                max_confidence = max([v["confidence"] for v in processed_result["summary"]["violations"]])
                if max_confidence >= 0.9:
                    processed_result["summary"]["risk_level"] = "HIGH"
                elif max_confidence >= 0.7:
                    processed_result["summary"]["risk_level"] = "MEDIUM"
                else:
                    processed_result["summary"]["risk_level"] = "LOW"
            else:
                processed_result["summary"]["risk_level"] = "SAFE"
                
        except Exception as e:
            self.logger.error(f"处理检测结果失败: {e}")
            processed_result["error"] = f"处理结果失败: {e}"
            processed_result["success"] = False
        
        return processed_result
    
    def detect_porn(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测色情内容"""
        return self.detect_image_content(image_input, ['porn'], confidence_threshold)
    
    def detect_terrorism(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测暴恐内容"""
        return self.detect_image_content(image_input, ['terrorism'], confidence_threshold)
    
    def detect_ad(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测广告内容"""
        return self.detect_image_content(image_input, ['ad'], confidence_threshold)
    
    def detect_live(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测直播内容"""
        return self.detect_image_content(image_input, ['live'], confidence_threshold)
    
    def detect_logo(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测Logo内容"""
        return self.detect_image_content(image_input, ['logo'], confidence_threshold)
    
    def detect_ocr(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测OCR内容"""
        return self.detect_image_content(image_input, ['ocr'], confidence_threshold)
    
    def detect_face(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测人脸内容"""
        return self.detect_image_content(image_input, ['face'], confidence_threshold)
    
    def detect_qrcode(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测二维码内容"""
        return self.detect_image_content(image_input, ['qrcode'], confidence_threshold)
    
    def detect_scene(self, image_input: Union[str, bytes], confidence_threshold: float = 0.8) -> Dict:
        """检测场景内容"""
        return self.detect_image_content(image_input, ['scene'], confidence_threshold)
    
    def batch_detect(self, 
                    image_paths: List[str], 
                    detection_types: List[str] = None,
                    confidence_threshold: float = 0.8) -> List[Dict]:
        """
        批量检测图像内容
        
        Args:
            image_paths: 图片路径列表
            detection_types: 检测类型列表
            confidence_threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.detect_image_content(image_path, detection_types, confidence_threshold)
                result["image_path"] = image_path
                results.append(result)
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "success": False,
                    "error": f"检测失败: {e}"
                })
        return results


def create_client_from_config(config_file: str = "config.ini") -> Optional[AliyunImageDetectionClient]:
    """
    从配置文件创建客户端
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        客户端实例或None
    """
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        access_key_id = config.get('aliyun_image_detection', 'access_key_id')
        access_key_secret = config.get('aliyun_image_detection', 'access_key_secret')
        region = config.get('aliyun_image_detection', 'region', fallback='cn-shanghai')
        
        if access_key_id == 'YOUR_ACCESS_KEY_ID' or access_key_secret == 'YOUR_ACCESS_KEY_SECRET':
            print("请先在config.ini中配置阿里云访问密钥")
            return None
        
        return AliyunImageDetectionClient(access_key_id, access_key_secret, region)
        
    except Exception as e:
        print(f"创建客户端失败: {e}")
        return None


if __name__ == "__main__":
    # 测试代码
    import time
    
    # 创建客户端
    client = create_client_from_config()
    if client:
        print("阿里云图像内容检测客户端初始化成功")
        
        # 测试检测（需要提供真实的图片路径）
        # result = client.detect_image_content("test_image.jpg", ['porn', 'terrorism'])
        # print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("客户端初始化失败")