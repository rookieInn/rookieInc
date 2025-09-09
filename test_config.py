#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置测试脚本
用于验证OSS和百度云盘的连接配置
"""

import json
import os
import sys
from datetime import datetime, timedelta

def test_oss_connection(config):
    """测试OSS连接"""
    try:
        import oss2
        
        auth = oss2.Auth(
            config['oss']['access_key_id'],
            config['oss']['access_key_secret']
        )
        bucket = oss2.Bucket(
            auth,
            config['oss']['endpoint'],
            config['oss']['bucket_name']
        )
        
        # 尝试列出对象
        result = bucket.list_objects(max_keys=1)
        print("✓ OSS连接成功")
        return True
        
    except Exception as e:
        print(f"✗ OSS连接失败: {e}")
        return False

def test_baidu_connection(config):
    """测试百度云盘连接"""
    try:
        from bypy import ByPy
        
        bypy = ByPy()
        # 尝试获取用户信息
        result = bypy.info()
        print("✓ 百度云盘连接成功")
        return True
        
    except Exception as e:
        print(f"✗ 百度云盘连接失败: {e}")
        return False

def test_date_calculation(config):
    """测试日期计算"""
    try:
        months_threshold = config['archive']['months_threshold']
        cutoff_date = datetime.now() - timedelta(days=30 * months_threshold)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        print(f"✓ 日期计算正确: {months_threshold}个月前的日期是 {cutoff_str}")
        return True
        
    except Exception as e:
        print(f"✗ 日期计算失败: {e}")
        return False

def main():
    """主函数"""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在，请先运行主脚本生成配置文件")
        sys.exit(1)
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        sys.exit(1)
    
    print("开始测试配置...")
    print("=" * 50)
    
    # 测试各项配置
    tests = [
        ("OSS连接", lambda: test_oss_connection(config)),
        ("百度云盘连接", lambda: test_baidu_connection(config)),
        ("日期计算", lambda: test_date_calculation(config))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n测试 {test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过，配置正确！")
        return 0
    else:
        print("✗ 部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())