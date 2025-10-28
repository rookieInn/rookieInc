#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS图片清理器
功能：
1. 连接OSS并删除指定的图片文件
2. 批量删除多个图片文件
3. 记录删除操作日志
4. 支持重试机制
"""

import os
import sys
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from configparser import ConfigParser
import json

# 第三方库导入
try:
    import oss2
    from oss2.credentials import EnvironmentVariableCredentialsProvider
    OSS2_AVAILABLE = True
except ImportError:
    OSS2_AVAILABLE = False
    print("⚠️ oss2库未安装，OSS功能将不可用")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSSImageCleaner:
    """OSS图片清理器"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """
        初始化OSS清理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        self._init_oss_client()
        self.max_retries = self.config.getint('oss_cleaner', 'max_retries', fallback=3)
        self.retry_delay = self.config.getint('oss_cleaner', 'retry_delay', fallback=1)
    
    def _init_oss_client(self):
        """初始化OSS客户端"""
        if not OSS2_AVAILABLE:
            logger.warning("oss2库未安装，OSS功能不可用")
            self.bucket = None
            self.bucket_name = "test-bucket"
            return
            
        try:
            # 从配置文件读取OSS配置
            access_key_id = self.config.get('aliyun_oss', 'access_key_id')
            access_key_secret = self.config.get('aliyun_oss', 'access_key_secret')
            endpoint = self.config.get('aliyun_oss', 'endpoint')
            bucket_name = self.config.get('aliyun_oss', 'bucket_name')
            
            if not all([access_key_id, access_key_secret, endpoint, bucket_name]):
                raise ValueError("OSS配置信息不完整，请检查config.ini文件")
            
            # 创建认证对象
            auth = oss2.Auth(access_key_id, access_key_secret)
            
            # 创建Bucket对象
            self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
            self.bucket_name = bucket_name
            
            # 测试连接
            self._test_connection()
            
            logger.info(f"✅ OSS客户端初始化成功: {bucket_name}")
            
        except Exception as e:
            logger.error(f"❌ OSS客户端初始化失败: {e}")
            raise
    
    def _test_connection(self):
        """测试OSS连接"""
        try:
            # 尝试获取bucket信息
            bucket_info = self.bucket.get_bucket_info()
            logger.info(f"OSS连接测试成功，桶信息: {bucket_info.name}")
        except Exception as e:
            logger.error(f"OSS连接测试失败: {e}")
            raise
    
    def delete_single_image(self, oss_key: str) -> bool:
        """
        删除单个图片文件
        
        Args:
            oss_key: OSS中的文件键名/路径
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查文件是否存在
            if not self._file_exists(oss_key):
                logger.warning(f"文件不存在，跳过删除: {oss_key}")
                return True
            
            # 执行删除操作
            self.bucket.delete_object(oss_key)
            logger.info(f"✅ 成功删除OSS文件: {oss_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 删除OSS文件失败 {oss_key}: {e}")
            return False
    
    def delete_multiple_images(self, oss_keys: List[str]) -> Dict[str, Any]:
        """
        批量删除多个图片文件
        
        Args:
            oss_keys: OSS文件键名列表
            
        Returns:
            Dict[str, Any]: 删除结果统计
        """
        if not oss_keys:
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'failed_keys': []
            }
        
        logger.info(f"开始批量删除 {len(oss_keys)} 个OSS文件")
        
        success_count = 0
        failed_count = 0
        failed_keys = []
        
        for i, oss_key in enumerate(oss_keys, 1):
            logger.info(f"删除进度: {i}/{len(oss_keys)} - {oss_key}")
            
            if self.delete_single_image(oss_key):
                success_count += 1
            else:
                failed_count += 1
                failed_keys.append(oss_key)
            
            # 添加延迟避免请求过于频繁
            if i < len(oss_keys):
                time.sleep(0.1)
        
        result = {
            'total': len(oss_keys),
            'success': success_count,
            'failed': failed_count,
            'failed_keys': failed_keys
        }
        
        logger.info(f"批量删除完成: 成功 {success_count}, 失败 {failed_count}")
        return result
    
    def delete_with_retry(self, oss_key: str) -> bool:
        """
        带重试机制的删除操作
        
        Args:
            oss_key: OSS文件键名
            
        Returns:
            bool: 删除是否成功
        """
        for attempt in range(self.max_retries):
            try:
                if self.delete_single_image(oss_key):
                    return True
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"删除失败，{self.retry_delay}秒后重试 (尝试 {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                
            except Exception as e:
                logger.error(f"删除重试失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ 文件删除最终失败: {oss_key}")
        return False
    
    def _file_exists(self, oss_key: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            oss_key: OSS文件键名
            
        Returns:
            bool: 文件是否存在
        """
        try:
            self.bucket.head_object(oss_key)
            return True
        except oss2.exceptions.NoSuchKey:
            return False
        except Exception as e:
            logger.warning(f"检查文件存在性时出错 {oss_key}: {e}")
            return False
    
    def get_file_info(self, oss_key: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            oss_key: OSS文件键名
            
        Returns:
            Optional[Dict[str, Any]]: 文件信息，如果文件不存在则返回None
        """
        try:
            result = self.bucket.head_object(oss_key)
            return {
                'key': oss_key,
                'size': result.content_length,
                'last_modified': result.last_modified,
                'content_type': result.content_type,
                'etag': result.etag
            }
        except oss2.exceptions.NoSuchKey:
            return None
        except Exception as e:
            logger.error(f"获取文件信息失败 {oss_key}: {e}")
            return None
    
    def list_files_with_prefix(self, prefix: str, max_keys: int = 1000) -> List[str]:
        """
        列出指定前缀的文件
        
        Args:
            prefix: 文件前缀
            max_keys: 最大返回数量
            
        Returns:
            List[str]: 文件键名列表
        """
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=max_keys):
                files.append(obj.key)
            
            logger.info(f"找到 {len(files)} 个以 '{prefix}' 开头的文件")
            return files
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    def cleanup_orphaned_files(self, valid_oss_keys: List[str], prefix: str = "") -> Dict[str, Any]:
        """
        清理孤立的文件（不在有效列表中的文件）
        
        Args:
            valid_oss_keys: 有效的OSS键名列表
            prefix: 文件前缀过滤
            
        Returns:
            Dict[str, Any]: 清理结果统计
        """
        try:
            logger.info("开始清理孤立文件...")
            
            # 获取所有文件
            all_files = self.list_files_with_prefix(prefix)
            
            # 找出孤立的文件
            valid_set = set(valid_oss_keys)
            orphaned_files = [f for f in all_files if f not in valid_set]
            
            if not orphaned_files:
                logger.info("没有发现孤立文件")
                return {
                    'total_files': len(all_files),
                    'valid_files': len(valid_oss_keys),
                    'orphaned_files': 0,
                    'deleted_files': 0,
                    'failed_deletions': 0
                }
            
            logger.info(f"发现 {len(orphaned_files)} 个孤立文件")
            
            # 删除孤立文件
            result = self.delete_multiple_images(orphaned_files)
            
            return {
                'total_files': len(all_files),
                'valid_files': len(valid_oss_keys),
                'orphaned_files': len(orphaned_files),
                'deleted_files': result['success'],
                'failed_deletions': result['failed']
            }
            
        except Exception as e:
            logger.error(f"清理孤立文件失败: {e}")
            return {}
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            Dict[str, Any]: 存储统计信息
        """
        try:
            bucket_info = self.bucket.get_bucket_info()
            
            return {
                'bucket_name': self.bucket_name,
                'total_size_bytes': bucket_info.storage_size_in_bytes,
                'total_size_gb': bucket_info.storage_size_in_bytes / (1024**3),
                'object_count': bucket_info.object_count,
                'last_modified': bucket_info.creation_date
            }
            
        except Exception as e:
            logger.error(f"获取存储统计失败: {e}")
            return {}
    
    def create_cleanup_report(self, cleanup_results: List[Dict[str, Any]], output_file: str = None) -> str:
        """
        创建清理报告
        
        Args:
            cleanup_results: 清理结果列表
            output_file: 输出文件路径
            
        Returns:
            str: 报告内容
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            report = f"""
OSS图片清理报告
================
生成时间: {timestamp}
桶名称: {self.bucket_name}

清理统计:
"""
            
            total_deleted = 0
            total_failed = 0
            
            for i, result in enumerate(cleanup_results, 1):
                report += f"""
批次 {i}:
  总文件数: {result.get('total', 0)}
  成功删除: {result.get('success', 0)}
  删除失败: {result.get('failed', 0)}
"""
                
                if result.get('failed_keys'):
                    report += f"  失败文件:\n"
                    for key in result['failed_keys']:
                        report += f"    - {key}\n"
                
                total_deleted += result.get('success', 0)
                total_failed += result.get('failed', 0)
            
            report += f"""
总计:
  成功删除: {total_deleted} 个文件
  删除失败: {total_failed} 个文件
  成功率: {(total_deleted / (total_deleted + total_failed) * 100):.1f}% (如果总数>0)
"""
            
            # 保存到文件
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                logger.info(f"清理报告已保存到: {output_file}")
            
            return report
            
        except Exception as e:
            logger.error(f"创建清理报告失败: {e}")
            return ""