#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试迁移工具
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baidu_pan_client import MockBaiduPanClient


def create_test_structure():
    """创建测试目录结构"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # 创建2023年的测试文件夹
    folders_2023 = [
        "2023/01/01",
        "2023/01/15", 
        "2023/02/01",
        "2023/03/01",
        "2023/12/31"
    ]
    
    for folder in folders_2023:
        folder_path = test_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # 在每个文件夹中创建一些测试文件
        for i in range(3):
            test_file = folder_path / f"test_file_{i}.txt"
            test_file.write_text(f"测试文件内容 {folder} - {i}")
    
    print(f"创建测试目录结构: {test_dir}")
    return test_dir


def test_baidu_pan_client():
    """测试百度云盘客户端"""
    print("测试百度云盘客户端...")
    
    client = MockBaiduPanClient("test_token")
    
    # 创建测试文件
    test_file = Path("test_upload.txt")
    test_file.write_text("这是一个测试文件")
    
    # 测试上传
    success = client.upload_file(str(test_file), "/test/upload.txt")
    
    if success:
        print("✓ 百度云盘客户端测试通过")
        uploaded_files = client.get_uploaded_files()
        print(f"已上传文件: {len(uploaded_files)} 个")
    else:
        print("✗ 百度云盘客户端测试失败")
    
    # 清理测试文件
    test_file.unlink()
    
    return success


def test_zip_creation():
    """测试ZIP压缩包创建"""
    print("测试ZIP压缩包创建...")
    
    try:
        import zipfile
        
        # 创建测试目录
        test_dir = Path("test_zip_dir")
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        (test_dir / "file1.txt").write_text("文件1内容")
        (test_dir / "file2.txt").write_text("文件2内容")
        
        # 创建ZIP
        zip_path = Path("test.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(test_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, test_dir)
                    zipf.write(file_path, arcname)
        
        # 验证ZIP文件
        if zip_path.exists() and zip_path.stat().st_size > 0:
            print("✓ ZIP压缩包创建测试通过")
            success = True
        else:
            print("✗ ZIP压缩包创建测试失败")
            success = False
        
        # 清理
        shutil.rmtree(test_dir)
        zip_path.unlink()
        
        return success
        
    except Exception as e:
        print(f"✗ ZIP压缩包创建测试失败: {e}")
        return False


def test_config_loading():
    """测试配置文件加载"""
    print("测试配置文件加载...")
    
    try:
        import configparser
        
        config = configparser.ConfigParser()
        config.read("config.ini", encoding='utf-8')
        
        # 检查必要的配置项
        required_sections = ['aliyun_oss', 'baidu_pan', 'general']
        for section in required_sections:
            if not config.has_section(section):
                print(f"✗ 缺少配置节: {section}")
                return False
        
        print("✓ 配置文件加载测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 配置文件加载测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始测试迁移工具...")
    print("=" * 50)
    
    tests = [
        ("配置文件加载", test_config_loading),
        ("百度云盘客户端", test_baidu_pan_client),
        ("ZIP压缩包创建", test_zip_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！")
        return True
    else:
        print("✗ 部分测试失败，请检查配置和依赖")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)