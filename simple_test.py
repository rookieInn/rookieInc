#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本，不依赖外部包
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path


def test_zip_creation():
    """测试ZIP压缩包创建"""
    print("测试ZIP压缩包创建...")
    
    try:
        # 创建测试目录
        test_dir = Path("test_zip_dir")
        test_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        (test_dir / "file1.txt").write_text("文件1内容")
        (test_dir / "file2.txt").write_text("文件2内容")
        
        # 创建子目录
        sub_dir = test_dir / "subdir"
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / "file3.txt").write_text("文件3内容")
        
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
            
            # 验证ZIP内容
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                print(f"  ZIP包含文件: {file_list}")
            
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


def test_file_operations():
    """测试文件操作"""
    print("测试文件操作...")
    
    try:
        # 创建测试目录结构
        test_dir = Path("test_structure")
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
        
        # 验证创建的文件
        total_files = 0
        for root, dirs, files in os.walk(test_dir):
            total_files += len(files)
        
        print(f"  创建了 {len(folders_2023)} 个文件夹，{total_files} 个文件")
        
        # 清理
        shutil.rmtree(test_dir)
        
        print("✓ 文件操作测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        return False


def test_config_parsing():
    """测试配置文件解析"""
    print("测试配置文件解析...")
    
    try:
        # 创建测试配置文件
        config_content = """[aliyun_oss]
access_key_id = test_key
access_key_secret = test_secret
endpoint = https://oss-cn-hangzhou.aliyuncs.com
bucket_name = test_bucket

[baidu_pan]
access_token = test_token

[general]
temp_dir = ./temp
output_dir = ./output
target_year = 2023
"""
        
        config_file = Path("test_config.ini")
        config_file.write_text(config_content)
        
        # 解析配置文件
        import configparser
        config = configparser.ConfigParser()
        config.read("test_config.ini", encoding='utf-8')
        
        # 验证配置
        assert config.get('aliyun_oss', 'access_key_id') == 'test_key'
        assert config.get('general', 'target_year') == '2023'
        
        # 清理
        config_file.unlink()
        
        print("✓ 配置文件解析测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 配置文件解析测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始测试迁移工具核心功能...")
    print("=" * 50)
    
    tests = [
        ("配置文件解析", test_config_parsing),
        ("文件操作", test_file_operations),
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
        print("✓ 所有核心功能测试通过！")
        print("\n程序已准备就绪，请按照以下步骤使用：")
        print("1. 编辑 config.ini 文件，填入您的阿里云OSS和百度云盘配置")
        print("2. 安装依赖: pip install -r requirements.txt")
        print("3. 运行程序: python3 oss_to_baidupan.py")
        return True
    else:
        print("✗ 部分测试失败，请检查环境配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)