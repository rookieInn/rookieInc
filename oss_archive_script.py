#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS文件归档脚本
功能：将OSS中24个月前的按日创建的文件夹打包上传到百度云盘，然后删除OSS中的文件
"""

import os
import sys
import zipfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
from typing import List, Dict, Any

# 第三方库导入
try:
    import oss2
    from oss2.credentials import EnvironmentVariableCredentialsProvider
except ImportError:
    print("请安装oss2库: pip install oss2")
    sys.exit(1)

try:
    from bypy import ByPy
except ImportError:
    print("请安装bypy库: pip install bypy")
    sys.exit(1)


class OSSArchiveManager:
    """OSS文件归档管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        """初始化管理器"""
        self.config = self._load_config(config_file)
        self.oss_client = self._init_oss_client()
        self.baidu_client = self._init_baidu_client()
        self._setup_logging()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_default_config(self, config_file: str):
        """创建默认配置文件"""
        default_config = {
            "oss": {
                "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
                "bucket_name": "your-bucket-name",
                "access_key_id": "your-access-key-id",
                "access_key_secret": "your-access-key-secret"
            },
            "baidu": {
                "app_id": "your-baidu-app-id",
                "app_key": "your-baidu-app-key",
                "secret_key": "your-baidu-secret-key"
            },
            "archive": {
                "months_threshold": 24,
                "temp_dir": "./temp_archive",
                "baidu_upload_path": "/OSS_Archive",
                "date_format": "%Y-%m-%d",
                "folder_pattern": "*/YYYY-MM-DD/*"
            },
            "logging": {
                "level": "INFO",
                "file": "oss_archive.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "safety": {
                "dry_run": False,
                "backup_before_delete": True,
                "max_file_size_mb": 1000
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        print(f"已创建默认配置文件: {config_file}")
        print("请编辑配置文件填入正确的OSS和百度云盘信息")
        sys.exit(1)
    
    def _init_oss_client(self):
        """初始化OSS客户端"""
        try:
            auth = oss2.Auth(
                self.config['oss']['access_key_id'],
                self.config['oss']['access_key_secret']
            )
            return oss2.Bucket(
                auth,
                self.config['oss']['endpoint'],
                self.config['oss']['bucket_name']
            )
        except Exception as e:
            logging.error(f"OSS客户端初始化失败: {e}")
            raise
    
    def _init_baidu_client(self):
        """初始化百度云盘客户端"""
        try:
            return ByPy()
        except Exception as e:
            logging.error(f"百度云盘客户端初始化失败: {e}")
            raise
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('oss_archive.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def get_old_folders(self) -> List[str]:
        """获取24个月前的文件夹列表"""
        try:
            # 计算24个月前的日期
            cutoff_date = datetime.now() - timedelta(days=30 * self.config['archive']['months_threshold'])
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            logging.info(f"查找 {cutoff_str} 之前的文件夹")
            
            # 获取所有对象
            folders = set()
            for obj in oss2.ObjectIterator(self.oss_client):
                # 假设文件夹结构为: folder_name/YYYY-MM-DD/file_name
                parts = obj.key.split('/')
                if len(parts) >= 2:
                    folder_name = parts[0]
                    date_str = parts[1]
                    
                    try:
                        folder_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if folder_date < cutoff_date:
                            folders.add(folder_name)
                    except ValueError:
                        # 如果日期格式不匹配，跳过
                        continue
            
            logging.info(f"找到 {len(folders)} 个需要归档的文件夹: {list(folders)}")
            return list(folders)
            
        except Exception as e:
            logging.error(f"获取文件夹列表失败: {e}")
            raise
    
    def download_folder_files(self, folder_name: str) -> str:
        """下载文件夹中的所有文件到本地临时目录"""
        try:
            temp_dir = Path(self.config['archive']['temp_dir'])
            temp_dir.mkdir(exist_ok=True)
            
            folder_temp_dir = temp_dir / folder_name
            folder_temp_dir.mkdir(exist_ok=True)
            
            logging.info(f"开始下载文件夹: {folder_name}")
            
            # 下载文件夹中的所有文件
            for obj in oss2.ObjectIterator(self.oss_client, prefix=f"{folder_name}/"):
                if not obj.key.endswith('/'):  # 跳过目录
                    local_file_path = folder_temp_dir / obj.key.split('/')[-1]
                    self.oss_client.get_object_to_file(obj.key, str(local_file_path))
                    logging.info(f"下载文件: {obj.key}")
            
            return str(folder_temp_dir)
            
        except Exception as e:
            logging.error(f"下载文件夹 {folder_name} 失败: {e}")
            raise
    
    def create_zip_archive(self, folder_path: str, folder_name: str) -> str:
        """将文件夹打包成ZIP文件"""
        try:
            zip_path = f"{folder_path}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arcname)
            
            logging.info(f"创建ZIP文件: {zip_path}")
            return zip_path
            
        except Exception as e:
            logging.error(f"创建ZIP文件失败: {e}")
            raise
    
    def upload_to_baidu(self, zip_path: str, folder_name: str) -> bool:
        """上传ZIP文件到百度云盘"""
        try:
            baidu_path = f"{self.config['archive']['baidu_upload_path']}/{folder_name}.zip"
            
            logging.info(f"开始上传到百度云盘: {baidu_path}")
            
            # 使用bypy上传文件
            result = self.baidu_client.upload(zip_path, baidu_path)
            
            if result == 0:
                logging.info(f"成功上传到百度云盘: {baidu_path}")
                return True
            else:
                logging.error(f"上传到百度云盘失败: {baidu_path}")
                return False
                
        except Exception as e:
            logging.error(f"上传到百度云盘失败: {e}")
            return False
    
    def delete_oss_folder(self, folder_name: str) -> bool:
        """删除OSS中的文件夹"""
        try:
            logging.info(f"开始删除OSS文件夹: {folder_name}")
            
            # 删除文件夹中的所有文件
            deleted_count = 0
            for obj in oss2.ObjectIterator(self.oss_client, prefix=f"{folder_name}/"):
                self.oss_client.delete_object(obj.key)
                deleted_count += 1
                logging.info(f"删除文件: {obj.key}")
            
            logging.info(f"成功删除 {deleted_count} 个文件")
            return True
            
        except Exception as e:
            logging.error(f"删除OSS文件夹失败: {e}")
            return False
    
    def cleanup_temp_files(self, temp_paths: List[str]):
        """清理临时文件"""
        try:
            for path in temp_paths:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        import shutil
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    logging.info(f"清理临时文件: {path}")
        except Exception as e:
            logging.error(f"清理临时文件失败: {e}")
    
    def run_archive_process(self):
        """运行完整的归档流程"""
        try:
            logging.info("开始OSS文件归档流程")
            
            # 1. 获取需要归档的文件夹
            old_folders = self.get_old_folders()
            if not old_folders:
                logging.info("没有找到需要归档的文件夹")
                return
            
            temp_paths = []
            
            for folder_name in old_folders:
                try:
                    logging.info(f"处理文件夹: {folder_name}")
                    
                    # 2. 下载文件夹文件
                    folder_path = self.download_folder_files(folder_name)
                    temp_paths.append(folder_path)
                    
                    # 3. 创建ZIP文件
                    zip_path = self.create_zip_archive(folder_path, folder_name)
                    temp_paths.append(zip_path)
                    
                    # 4. 上传到百度云盘
                    upload_success = self.upload_to_baidu(zip_path, folder_name)
                    
                    if upload_success:
                        # 5. 删除OSS中的文件夹
                        delete_success = self.delete_oss_folder(folder_name)
                        
                        if delete_success:
                            logging.info(f"文件夹 {folder_name} 归档完成")
                        else:
                            logging.error(f"文件夹 {folder_name} 删除失败，请手动处理")
                    else:
                        logging.error(f"文件夹 {folder_name} 上传失败，跳过删除")
                    
                    # 添加延迟避免API限制
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"处理文件夹 {folder_name} 时出错: {e}")
                    continue
            
            # 6. 清理临时文件
            self.cleanup_temp_files(temp_paths)
            
            logging.info("OSS文件归档流程完成")
            
        except Exception as e:
            logging.error(f"归档流程执行失败: {e}")
            raise


def main():
    """主函数"""
    try:
        manager = OSSArchiveManager()
        manager.run_archive_process()
    except KeyboardInterrupt:
        logging.info("用户中断操作")
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()