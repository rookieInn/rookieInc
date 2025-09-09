#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度云盘客户端
简化版本，用于文件上传
"""

import os
import json
import time
import hashlib
import requests
from typing import Optional, Dict, Any
import logging


class BaiduPanClient:
    """百度云盘客户端"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://pan.baidu.com/rest/2.0/xpan"
        self.upload_url = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
        
    def create_directory(self, path: str) -> bool:
        """创建目录"""
        try:
            url = f"{self.base_url}/file"
            params = {
                'method': 'create',
                'access_token': self.access_token
            }
            data = {
                'path': path,
                'isdir': 1
            }
            
            response = requests.post(url, params=params, data=data)
            result = response.json()
            
            if result.get('errno') == 0:
                logging.info(f"目录创建成功: {path}")
                return True
            else:
                logging.warning(f"目录创建失败或已存在: {result.get('errmsg', '未知错误')}")
                return True  # 目录可能已存在，继续执行
                
        except Exception as e:
            logging.error(f"创建目录失败: {e}")
            return False
    
    def upload_file(self, local_file_path: str, remote_path: str) -> bool:
        """上传文件到百度云盘"""
        try:
            if not os.path.exists(local_file_path):
                logging.error(f"本地文件不存在: {local_file_path}")
                return False
            
            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_path)
            if remote_dir and not self.create_directory(remote_dir):
                return False
            
            # 获取文件信息
            file_size = os.path.getsize(local_file_path)
            
            # 预上传
            precreate_result = self._precreate_file(remote_path, file_size)
            if not precreate_result:
                return False
            
            upload_id = precreate_result.get('uploadid')
            block_list = precreate_result.get('block_list', [])
            
            # 分块上传
            if not self._upload_blocks(local_file_path, upload_id, block_list):
                return False
            
            # 合并文件
            return self._merge_blocks(remote_path, upload_id, block_list)
            
        except Exception as e:
            logging.error(f"上传文件失败: {e}")
            return False
    
    def _precreate_file(self, remote_path: str, file_size: int) -> Optional[Dict[str, Any]]:
        """预创建文件"""
        try:
            url = f"{self.base_url}/file"
            params = {
                'method': 'precreate',
                'access_token': self.access_token
            }
            data = {
                'path': remote_path,
                'size': file_size,
                'isdir': 0,
                'autoinit': 1
            }
            
            response = requests.post(url, params=params, data=data)
            result = response.json()
            
            if result.get('errno') == 0:
                return result
            else:
                logging.error(f"预创建文件失败: {result.get('errmsg', '未知错误')}")
                return None
                
        except Exception as e:
            logging.error(f"预创建文件异常: {e}")
            return None
    
    def _upload_blocks(self, local_file_path: str, upload_id: str, block_list: list) -> bool:
        """分块上传文件"""
        try:
            block_size = 4 * 1024 * 1024  # 4MB per block
            
            with open(local_file_path, 'rb') as f:
                for i, block in enumerate(block_list):
                    f.seek(i * block_size)
                    block_data = f.read(block_size)
                    
                    if not self._upload_single_block(upload_id, i, block_data):
                        return False
                    
                    logging.info(f"上传块 {i+1}/{len(block_list)}")
            
            return True
            
        except Exception as e:
            logging.error(f"分块上传失败: {e}")
            return False
    
    def _upload_single_block(self, upload_id: str, part_number: int, block_data: bytes) -> bool:
        """上传单个块"""
        try:
            url = f"{self.upload_url}/upload"
            params = {
                'method': 'upload',
                'access_token': self.access_token,
                'type': 'tmpfile',
                'uploadid': upload_id,
                'partseq': part_number
            }
            
            files = {'file': block_data}
            
            response = requests.post(url, params=params, files=files)
            result = response.json()
            
            if result.get('errno') == 0:
                return True
            else:
                logging.error(f"上传块失败: {result.get('errmsg', '未知错误')}")
                return False
                
        except Exception as e:
            logging.error(f"上传块异常: {e}")
            return False
    
    def _merge_blocks(self, remote_path: str, upload_id: str, block_list: list) -> bool:
        """合并文件块"""
        try:
            url = f"{self.base_url}/file"
            params = {
                'method': 'create',
                'access_token': self.access_token
            }
            data = {
                'path': remote_path,
                'uploadid': upload_id,
                'block_list': json.dumps(block_list)
            }
            
            response = requests.post(url, params=params, data=data)
            result = response.json()
            
            if result.get('errno') == 0:
                logging.info(f"文件上传成功: {remote_path}")
                return True
            else:
                logging.error(f"合并文件失败: {result.get('errmsg', '未知错误')}")
                return False
                
        except Exception as e:
            logging.error(f"合并文件异常: {e}")
            return False


# 简化版本，使用模拟上传
class MockBaiduPanClient:
    """模拟百度云盘客户端，用于测试"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.uploaded_files = []
    
    def upload_file(self, local_file_path: str, remote_path: str) -> bool:
        """模拟上传文件"""
        try:
            if not os.path.exists(local_file_path):
                logging.error(f"本地文件不存在: {local_file_path}")
                return False
            
            file_size = os.path.getsize(local_file_path)
            self.uploaded_files.append({
                'local_path': local_file_path,
                'remote_path': remote_path,
                'size': file_size,
                'upload_time': time.time()
            })
            
            logging.info(f"模拟上传成功: {local_file_path} -> {remote_path} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logging.error(f"模拟上传失败: {e}")
            return False
    
    def get_uploaded_files(self) -> list:
        """获取已上传的文件列表"""
        return self.uploaded_files