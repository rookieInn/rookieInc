#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全版本的OSS文件归档脚本
支持干运行模式，可以先预览操作而不实际执行
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oss_archive_script import OSSArchiveManager


class SafeArchiveManager(OSSArchiveManager):
    """安全版本的归档管理器，支持干运行模式"""
    
    def __init__(self, config_file: str = "config.json", dry_run: bool = True):
        """初始化安全管理器"""
        super().__init__(config_file)
        self.dry_run = dry_run or self.config.get('safety', {}).get('dry_run', False)
        
        if self.dry_run:
            print("🔍 运行在干运行模式 - 不会实际执行删除和上传操作")
    
    def get_old_folders(self):
        """获取需要归档的文件夹（干运行模式会显示详细信息）"""
        folders = super().get_old_folders()
        
        if self.dry_run and folders:
            print(f"\n📁 找到 {len(folders)} 个需要归档的文件夹:")
            for i, folder in enumerate(folders, 1):
                print(f"  {i}. {folder}")
            
            # 显示每个文件夹的详细信息
            for folder in folders:
                self._show_folder_details(folder)
        
        return folders
    
    def _show_folder_details(self, folder_name: str):
        """显示文件夹的详细信息"""
        try:
            file_count = 0
            total_size = 0
            date_range = []
            
            for obj in oss2.ObjectIterator(self.oss_client, prefix=f"{folder_name}/"):
                if not obj.key.endswith('/'):
                    file_count += 1
                    total_size += obj.size
                    
                    # 提取日期
                    parts = obj.key.split('/')
                    if len(parts) >= 2:
                        date_str = parts[1]
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            date_range.append(date_obj)
                        except ValueError:
                            pass
            
            if date_range:
                min_date = min(date_range).strftime('%Y-%m-%d')
                max_date = max(date_range).strftime('%Y-%m-%d')
                size_mb = total_size / (1024 * 1024)
                
                print(f"    📊 {folder_name}: {file_count} 个文件, {size_mb:.2f} MB")
                print(f"    📅 日期范围: {min_date} 到 {max_date}")
            
        except Exception as e:
            print(f"    ❌ 获取文件夹 {folder_name} 详情失败: {e}")
    
    def download_folder_files(self, folder_name: str):
        """下载文件夹文件（干运行模式跳过）"""
        if self.dry_run:
            print(f"🔍 [干运行] 将下载文件夹: {folder_name}")
            return f"/tmp/dry_run_{folder_name}"
        
        return super().download_folder_files(folder_name)
    
    def create_zip_archive(self, folder_path: str, folder_name: str):
        """创建ZIP文件（干运行模式跳过）"""
        if self.dry_run:
            print(f"🔍 [干运行] 将创建ZIP文件: {folder_name}.zip")
            return f"/tmp/dry_run_{folder_name}.zip"
        
        return super().create_zip_archive(folder_path, folder_name)
    
    def upload_to_baidu(self, zip_path: str, folder_name: str):
        """上传到百度云盘（干运行模式跳过）"""
        if self.dry_run:
            print(f"🔍 [干运行] 将上传到百度云盘: {folder_name}.zip")
            return True
        
        return super().upload_to_baidu(zip_path, folder_name)
    
    def delete_oss_folder(self, folder_name: str):
        """删除OSS文件夹（干运行模式跳过）"""
        if self.dry_run:
            print(f"🔍 [干运行] 将删除OSS文件夹: {folder_name}")
            return True
        
        return super().delete_oss_folder(folder_name)
    
    def run_archive_process(self):
        """运行归档流程（支持干运行）"""
        try:
            if self.dry_run:
                print("🔍 开始干运行模式 - 预览归档操作")
            else:
                print("🚀 开始实际归档操作")
            
            # 获取需要归档的文件夹
            old_folders = self.get_old_folders()
            if not old_folders:
                print("✅ 没有找到需要归档的文件夹")
                return
            
            if self.dry_run:
                print(f"\n📋 干运行总结:")
                print(f"   - 将处理 {len(old_folders)} 个文件夹")
                print(f"   - 将创建 {len(old_folders)} 个ZIP文件")
                print(f"   - 将上传到百度云盘路径: {self.config['archive']['baidu_upload_path']}")
                print(f"   - 将删除OSS中的原始文件")
                print(f"\n💡 要执行实际操作，请运行: python3 oss_archive_script.py")
                return
            
            # 执行实际归档流程
            super().run_archive_process()
            
        except Exception as e:
            print(f"❌ 归档流程执行失败: {e}")
            raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OSS文件归档脚本（安全版本）')
    parser.add_argument('--dry-run', action='store_true', 
                       help='干运行模式，只预览不执行实际操作')
    parser.add_argument('--config', default='config.json',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        manager = SafeArchiveManager(args.config, dry_run=args.dry_run)
        manager.run_archive_process()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()