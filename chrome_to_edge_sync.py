#!/usr/bin/env python3
"""
Chrome书签同步到Edge浏览器的工具
支持定期同步和增量更新
"""

import json
import os
import shutil
import sqlite3
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/bookmark_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BookmarkSync:
    def __init__(self, config_file: str = '/workspace/bookmark_sync_config.json'):
        """初始化书签同步器"""
        self.config_file = config_file
        self.config = self.load_config()
        self.chrome_bookmarks_path = self.find_chrome_bookmarks()
        self.edge_bookmarks_path = self.find_edge_bookmarks()
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "sync_interval_minutes": 30,
            "backup_enabled": True,
            "backup_retention_days": 7,
            "chrome_profile": "Default",
            "edge_profile": "Default",
            "exclude_folders": ["书签栏", "其他书签"],
            "log_level": "INFO"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"配置文件读取失败，使用默认配置: {e}")
                return default_config
        else:
            # 创建默认配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            logger.info(f"已创建默认配置文件: {self.config_file}")
            return default_config
    
    def find_chrome_bookmarks(self) -> Optional[str]:
        """查找Chrome书签文件路径"""
        possible_paths = [
            os.path.expanduser("~/.config/google-chrome/Default/Bookmarks"),
            os.path.expanduser("~/.config/google-chrome-beta/Default/Bookmarks"),
            os.path.expanduser("~/.config/google-chrome-unstable/Default/Bookmarks"),
            os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Bookmarks"),
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Bookmarks")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"找到Chrome书签文件: {path}")
                return path
        
        logger.error("未找到Chrome书签文件")
        return None
    
    def find_edge_bookmarks(self) -> Optional[str]:
        """查找Edge书签文件路径"""
        possible_paths = [
            os.path.expanduser("~/.config/microsoft-edge/Default/Bookmarks"),
            os.path.expanduser("~/.config/microsoft-edge-beta/Default/Bookmarks"),
            os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Bookmarks"),
            os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data/Default/Bookmarks")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"找到Edge书签文件: {path}")
                return path
        
        logger.error("未找到Edge书签文件")
        return None
    
    def read_chrome_bookmarks(self) -> Optional[Dict]:
        """读取Chrome书签"""
        if not self.chrome_bookmarks_path or not os.path.exists(self.chrome_bookmarks_path):
            logger.error("Chrome书签文件不存在")
            return None
        
        try:
            with open(self.chrome_bookmarks_path, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
            logger.info("成功读取Chrome书签")
            return bookmarks
        except Exception as e:
            logger.error(f"读取Chrome书签失败: {e}")
            return None
    
    def backup_edge_bookmarks(self) -> bool:
        """备份Edge书签"""
        if not self.edge_bookmarks_path or not os.path.exists(self.edge_bookmarks_path):
            logger.warning("Edge书签文件不存在，跳过备份")
            return True
        
        try:
            backup_dir = Path("/workspace/edge_bookmark_backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"Bookmarks_backup_{timestamp}.json"
            
            shutil.copy2(self.edge_bookmarks_path, backup_file)
            logger.info(f"Edge书签已备份到: {backup_file}")
            
            # 清理旧备份
            self.cleanup_old_backups(backup_dir)
            return True
        except Exception as e:
            logger.error(f"备份Edge书签失败: {e}")
            return False
    
    def cleanup_old_backups(self, backup_dir: Path):
        """清理旧备份文件"""
        try:
            retention_days = self.config.get("backup_retention_days", 7)
            cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
            
            for backup_file in backup_dir.glob("Bookmarks_backup_*.json"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    logger.info(f"已删除旧备份: {backup_file}")
        except Exception as e:
            logger.warning(f"清理旧备份失败: {e}")
    
    def filter_bookmarks(self, bookmarks: Dict, exclude_folders: List[str]) -> Dict:
        """过滤书签，排除指定文件夹"""
        def filter_node(node):
            if node.get("type") == "folder":
                if node.get("name") in exclude_folders:
                    return None
                # 递归过滤子节点
                children = []
                for child in node.get("children", []):
                    filtered_child = filter_node(child)
                    if filtered_child:
                        children.append(filtered_child)
                node["children"] = children
            return node
        
        # 过滤书签栏
        if "roots" in bookmarks:
            for root_name in ["bookmark_bar", "other"]:
                if root_name in bookmarks["roots"]:
                    bookmarks["roots"][root_name] = filter_node(bookmarks["roots"][root_name])
        
        return bookmarks
    
    def write_edge_bookmarks(self, bookmarks: Dict) -> bool:
        """写入Edge书签"""
        if not self.edge_bookmarks_path:
            logger.error("Edge书签路径未找到")
            return False
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.edge_bookmarks_path), exist_ok=True)
            
            # 过滤书签
            exclude_folders = self.config.get("exclude_folders", [])
            filtered_bookmarks = self.filter_bookmarks(bookmarks, exclude_folders)
            
            # 写入文件
            with open(self.edge_bookmarks_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_bookmarks, f, indent=2, ensure_ascii=False)
            
            logger.info("成功写入Edge书签")
            return True
        except Exception as e:
            logger.error(f"写入Edge书签失败: {e}")
            return False
    
    def sync_bookmarks(self) -> bool:
        """同步书签"""
        logger.info("开始同步书签...")
        
        # 读取Chrome书签
        chrome_bookmarks = self.read_chrome_bookmarks()
        if not chrome_bookmarks:
            return False
        
        # 备份Edge书签
        if self.config.get("backup_enabled", True):
            if not self.backup_edge_bookmarks():
                logger.warning("备份失败，但继续同步")
        
        # 写入Edge书签
        if self.write_edge_bookmarks(chrome_bookmarks):
            logger.info("书签同步完成")
            return True
        else:
            logger.error("书签同步失败")
            return False
    
    def start_scheduler(self):
        """启动定期同步调度器"""
        interval = self.config.get("sync_interval_minutes", 30)
        interval_seconds = interval * 60
        
        logger.info(f"书签同步调度器已启动，每{interval}分钟同步一次")
        
        last_sync = 0
        while True:
            current_time = time.time()
            
            # 检查是否到了同步时间
            if current_time - last_sync >= interval_seconds:
                self.sync_bookmarks()
                last_sync = current_time
            
            time.sleep(60)  # 每分钟检查一次
    
    def run_once(self):
        """运行一次同步"""
        return self.sync_bookmarks()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chrome书签同步到Edge浏览器")
    parser.add_argument("--once", action="store_true", help="只运行一次同步")
    parser.add_argument("--config", default="/workspace/bookmark_sync_config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建同步器
    sync = BookmarkSync(args.config)
    
    if args.once:
        # 运行一次同步
        success = sync.run_once()
        exit(0 if success else 1)
    else:
        # 启动定期同步
        try:
            sync.start_scheduler()
        except KeyboardInterrupt:
            logger.info("同步器已停止")

if __name__ == "__main__":
    main()