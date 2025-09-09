#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云OSS到百度云盘迁移工具
将指定年份的文件夹从阿里云OSS下载、打包、上传到百度云盘，然后删除原文件夹
"""

import os
import sys
import json
import time
import zipfile
import configparser
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import logging

import oss2
import requests
from tqdm import tqdm
from dateutil import parser as date_parser
from baidu_pan_client import MockBaiduPanClient


class AliyunOSSClient:
    """阿里云OSS客户端"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, bucket_name: str):
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
        self.bucket_name = bucket_name
        
    def list_folders_by_year(self, year: int) -> List[str]:
        """列出指定年份的所有文件夹"""
        folders = []
        prefix = f"{year}/"
        
        try:
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, delimiter='/'):
                if obj.key.endswith('/') and obj.key != prefix:
                    folders.append(obj.key.rstrip('/'))
                    logging.info(f"找到文件夹: {obj.key}")
        except Exception as e:
            logging.error(f"列出文件夹时出错: {e}")
            
        return folders
    
    def download_folder(self, folder_path: str, local_path: str) -> bool:
        """下载整个文件夹到本地"""
        try:
            os.makedirs(local_path, exist_ok=True)
            
            # 列出文件夹中的所有文件
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=folder_path + '/'):
                if not obj.key.endswith('/'):
                    files.append(obj.key)
            
            # 下载文件
            for file_key in tqdm(files, desc=f"下载 {folder_path}"):
                local_file_path = os.path.join(local_path, file_key.replace(folder_path + '/', ''))
                local_file_dir = os.path.dirname(local_file_path)
                
                if local_file_dir:
                    os.makedirs(local_file_dir, exist_ok=True)
                
                self.bucket.get_object_to_file(file_key, local_file_path)
            
            return True
        except Exception as e:
            logging.error(f"下载文件夹 {folder_path} 失败: {e}")
            return False
    
    def delete_folder(self, folder_path: str) -> bool:
        """删除文件夹及其所有内容"""
        try:
            # 列出文件夹中的所有文件
            files_to_delete = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=folder_path + '/'):
                if not obj.key.endswith('/'):
                    files_to_delete.append(obj.key)
            
            # 批量删除文件
            if files_to_delete:
                self.bucket.batch_delete_objects(files_to_delete)
                logging.info(f"已删除 {len(files_to_delete)} 个文件")
            
            return True
        except Exception as e:
            logging.error(f"删除文件夹 {folder_path} 失败: {e}")
            return False


class BaiduPanClient:
    """百度云盘客户端"""
    
    def __init__(self, access_token: str, app_key: str, app_secret: str):
        self.access_token = access_token
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://pan.baidu.com/rest/2.0/xpan"
        
    def upload_file(self, local_file_path: str, remote_path: str) -> bool:
        """上传文件到百度云盘"""
        try:
            # 获取上传URL
            upload_url = self._get_upload_url()
            if not upload_url:
                return False
            
            # 上传文件
            with open(local_file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'path': remote_path,
                    'ondup': 'overwrite'
                }
                
                response = requests.post(upload_url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('errno') == 0:
                        logging.info(f"文件上传成功: {remote_path}")
                        return True
                    else:
                        logging.error(f"上传失败: {result.get('errmsg', '未知错误')}")
                else:
                    logging.error(f"上传请求失败: {response.status_code}")
                    
        except Exception as e:
            logging.error(f"上传文件 {local_file_path} 失败: {e}")
            
        return False
    
    def _get_upload_url(self) -> str:
        """获取上传URL"""
        try:
            url = f"{self.base_url}/file"
            params = {
                'method': 'precreate',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                if result.get('errno') == 0:
                    return result.get('uploadid')
            
        except Exception as e:
            logging.error(f"获取上传URL失败: {e}")
            
        return None


class OSSToBaiduPanMigrator:
    """OSS到百度云盘迁移器"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 初始化客户端
        self.oss_client = AliyunOSSClient(
            access_key_id=self.config.get('aliyun_oss', 'access_key_id'),
            access_key_secret=self.config.get('aliyun_oss', 'access_key_secret'),
            endpoint=self.config.get('aliyun_oss', 'endpoint'),
            bucket_name=self.config.get('aliyun_oss', 'bucket_name')
        )
        
        # 使用模拟客户端进行测试，实际使用时可以替换为真实的百度云盘客户端
        self.baidu_client = MockBaiduPanClient(
            access_token=self.config.get('baidu_pan', 'access_token')
        )
        
        # 创建必要的目录
        self.temp_dir = Path(self.config.get('general', 'temp_dir'))
        self.output_dir = Path(self.config.get('general', 'output_dir'))
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def create_zip_archive(self, folder_path: str, zip_path: str) -> bool:
        """创建ZIP压缩包"""
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
            
            logging.info(f"ZIP压缩包创建成功: {zip_path}")
            return True
        except Exception as e:
            logging.error(f"创建ZIP压缩包失败: {e}")
            return False
    
    def migrate_year_folders(self, year: int) -> bool:
        """迁移指定年份的所有文件夹"""
        logging.info(f"开始迁移 {year} 年的文件夹...")
        
        # 1. 列出所有文件夹
        folders = self.oss_client.list_folders_by_year(year)
        if not folders:
            logging.warning(f"未找到 {year} 年的文件夹")
            return True
        
        logging.info(f"找到 {len(folders)} 个文件夹需要迁移")
        
        success_count = 0
        failed_folders = []
        
        for folder in tqdm(folders, desc="迁移文件夹"):
            try:
                # 2. 下载文件夹
                local_folder_path = self.temp_dir / folder.replace('/', '_')
                if not self.oss_client.download_folder(folder, str(local_folder_path)):
                    failed_folders.append(folder)
                    continue
                
                # 3. 创建ZIP压缩包
                zip_filename = f"{folder.replace('/', '_')}.zip"
                zip_path = self.output_dir / zip_filename
                
                if not self.create_zip_archive(str(local_folder_path), str(zip_path)):
                    failed_folders.append(folder)
                    continue
                
                # 4. 上传到百度云盘
                remote_path = f"/{year}_backup/{zip_filename}"
                if not self.baidu_client.upload_file(str(zip_path), remote_path):
                    failed_folders.append(folder)
                    continue
                
                # 5. 删除本地临时文件
                self._cleanup_local_files(local_folder_path, zip_path)
                
                # 6. 删除OSS中的文件夹
                if self.oss_client.delete_folder(folder):
                    success_count += 1
                    logging.info(f"文件夹 {folder} 迁移成功")
                else:
                    failed_folders.append(folder)
                
            except Exception as e:
                logging.error(f"迁移文件夹 {folder} 时出错: {e}")
                failed_folders.append(folder)
        
        # 输出结果
        logging.info(f"迁移完成！成功: {success_count}, 失败: {len(failed_folders)}")
        if failed_folders:
            logging.warning(f"失败的文件夹: {failed_folders}")
        
        return len(failed_folders) == 0
    
    def _cleanup_local_files(self, folder_path: Path, zip_path: Path):
        """清理本地临时文件"""
        try:
            import shutil
            if folder_path.exists():
                shutil.rmtree(folder_path)
            if zip_path.exists():
                zip_path.unlink()
        except Exception as e:
            logging.warning(f"清理本地文件失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.ini"
    
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在，请先配置")
        return
    
    try:
        migrator = OSSToBaiduPanMigrator(config_file)
        target_year = migrator.config.getint('general', 'target_year')
        
        print(f"开始迁移 {target_year} 年的文件夹...")
        success = migrator.migrate_year_folders(target_year)
        
        if success:
            print("所有文件夹迁移成功！")
        else:
            print("部分文件夹迁移失败，请查看日志文件")
            
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        print(f"程序执行失败: {e}")


if __name__ == "__main__":
    main()