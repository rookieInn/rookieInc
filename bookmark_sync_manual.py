#!/usr/bin/env python3
"""
Chrome书签同步到Edge浏览器的简化版本
用于手动运行和测试
"""

import json
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_browser_bookmarks(browser_name):
    """查找浏览器书签文件"""
    if browser_name.lower() == "chrome":
        paths = [
            os.path.expanduser("~/.config/google-chrome/Default/Bookmarks"),
            os.path.expanduser("~/.config/google-chrome-beta/Default/Bookmarks"),
            os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Bookmarks"),
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Bookmarks")
        ]
    elif browser_name.lower() == "edge":
        paths = [
            os.path.expanduser("~/.config/microsoft-edge/Default/Bookmarks"),
            os.path.expanduser("~/.config/microsoft-edge-beta/Default/Bookmarks"),
            os.path.expanduser("~/Library/Application Support/Microsoft Edge/Default/Bookmarks"),
            os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data/Default/Bookmarks")
        ]
    else:
        return None
    
    for path in paths:
        if os.path.exists(path):
            logger.info(f"找到{browser_name}书签文件: {path}")
            return path
    
    logger.error(f"未找到{browser_name}书签文件")
    return None

def read_bookmarks(bookmark_path):
    """读取书签文件"""
    try:
        with open(bookmark_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取书签失败: {e}")
        return None

def backup_bookmarks(bookmark_path, browser_name):
    """备份书签文件"""
    try:
        backup_dir = Path("/workspace/bookmark_backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{browser_name}_Bookmarks_backup_{timestamp}.json"
        
        shutil.copy2(bookmark_path, backup_file)
        logger.info(f"{browser_name}书签已备份到: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"备份{browser_name}书签失败: {e}")
        return False

def write_bookmarks(bookmark_path, bookmarks):
    """写入书签文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(bookmark_path), exist_ok=True)
        
        with open(bookmark_path, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        
        logger.info("成功写入书签文件")
        return True
    except Exception as e:
        logger.error(f"写入书签失败: {e}")
        return False

def sync_chrome_to_edge():
    """同步Chrome书签到Edge"""
    logger.info("开始同步Chrome书签到Edge...")
    
    # 查找书签文件
    chrome_path = find_browser_bookmarks("chrome")
    edge_path = find_browser_bookmarks("edge")
    
    if not chrome_path:
        logger.error("未找到Chrome书签文件")
        return False
    
    if not edge_path:
        logger.error("未找到Edge书签文件")
        return False
    
    # 读取Chrome书签
    chrome_bookmarks = read_bookmarks(chrome_path)
    if not chrome_bookmarks:
        return False
    
    # 备份Edge书签
    if not backup_bookmarks(edge_path, "Edge"):
        logger.warning("备份失败，但继续同步")
    
    # 写入Edge书签
    if write_bookmarks(edge_path, chrome_bookmarks):
        logger.info("书签同步完成！")
        return True
    else:
        logger.error("书签同步失败")
        return False

def main():
    """主函数"""
    print("Chrome书签同步到Edge浏览器工具")
    print("=" * 40)
    
    # 检查Chrome和Edge书签文件
    chrome_path = find_browser_bookmarks("chrome")
    edge_path = find_browser_bookmarks("edge")
    
    print(f"Chrome书签: {'✓' if chrome_path else '✗'} {chrome_path or '未找到'}")
    print(f"Edge书签: {'✓' if edge_path else '✗'} {edge_path or '未找到'}")
    print()
    
    if not chrome_path or not edge_path:
        print("请确保Chrome和Edge浏览器都已安装并至少运行过一次")
        return
    
    # 执行同步
    if sync_chrome_to_edge():
        print("✓ 同步成功！")
    else:
        print("✗ 同步失败，请查看日志")

if __name__ == "__main__":
    main()