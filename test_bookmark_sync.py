#!/usr/bin/env python3
"""
测试Chrome书签同步功能
"""

import json
import os
import tempfile
import shutil
from bookmark_sync_manual import *

def create_test_bookmarks():
    """创建测试书签文件"""
    test_bookmarks = {
        "version": 1,
        "checksum": "test_checksum",
        "roots": {
            "bookmark_bar": {
                "children": [
                    {
                        "date_added": "13212345678901234",
                        "id": "1",
                        "name": "Google",
                        "type": "url",
                        "url": "https://www.google.com"
                    },
                    {
                        "date_added": "13212345678901235",
                        "id": "2",
                        "name": "GitHub",
                        "type": "url",
                        "url": "https://github.com"
                    },
                    {
                        "date_added": "13212345678901236",
                        "id": "3",
                        "name": "测试文件夹",
                        "type": "folder",
                        "children": [
                            {
                                "date_added": "13212345678901237",
                                "id": "4",
                                "name": "Python官网",
                                "type": "url",
                                "url": "https://www.python.org"
                            }
                        ]
                    }
                ],
                "date_added": "13212345678901230",
                "date_modified": "13212345678901230",
                "id": "1",
                "name": "书签栏",
                "type": "folder"
            },
            "other": {
                "children": [],
                "date_added": "13212345678901231",
                "date_modified": "13212345678901231",
                "id": "2",
                "name": "其他书签",
                "type": "folder"
            },
            "synced": {
                "children": [],
                "date_added": "13212345678901232",
                "date_modified": "13212345678901232",
                "id": "3",
                "name": "移动设备书签",
                "type": "folder"
            }
        }
    }
    return test_bookmarks

def test_sync_functionality():
    """测试同步功能"""
    print("开始测试书签同步功能...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        chrome_path = os.path.join(temp_dir, "chrome_bookmarks.json")
        edge_path = os.path.join(temp_dir, "edge_bookmarks.json")
        
        # 创建测试Chrome书签
        test_bookmarks = create_test_bookmarks()
        with open(chrome_path, 'w', encoding='utf-8') as f:
            json.dump(test_bookmarks, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 创建测试Chrome书签: {chrome_path}")
        
        # 创建测试Edge书签（空文件）
        with open(edge_path, 'w', encoding='utf-8') as f:
            json.dump({"version": 1, "roots": {}}, f)
        
        print(f"✓ 创建测试Edge书签: {edge_path}")
        
        # 测试读取功能
        chrome_data = read_bookmarks(chrome_path)
        if chrome_data:
            print("✓ Chrome书签读取成功")
        else:
            print("✗ Chrome书签读取失败")
            return False
        
        # 测试备份功能
        if backup_bookmarks(edge_path, "Edge"):
            print("✓ Edge书签备份成功")
        else:
            print("✗ Edge书签备份失败")
            return False
        
        # 测试写入功能
        if write_bookmarks(edge_path, chrome_data):
            print("✓ Edge书签写入成功")
        else:
            print("✗ Edge书签写入失败")
            return False
        
        # 验证同步结果
        with open(edge_path, 'r', encoding='utf-8') as f:
            synced_data = json.load(f)
        
        if synced_data == chrome_data:
            print("✓ 书签同步验证成功")
        else:
            print("✗ 书签同步验证失败")
            return False
        
        print("\n所有测试通过！书签同步功能正常工作。")
        return True

def main():
    """主函数"""
    print("Chrome书签同步功能测试")
    print("=" * 40)
    
    if test_sync_functionality():
        print("\n✓ 测试完成，功能正常")
    else:
        print("\n✗ 测试失败，请检查代码")

if __name__ == "__main__":
    main()