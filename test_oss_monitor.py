#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS存储监控系统测试脚本
用于验证系统各个组件的功能
"""

import os
import sys
import json
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oss_storage_monitor import OSSStorageMonitor


class OSSMonitorTester:
    """OSS监控系统测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.test_dir = Path(tempfile.mkdtemp(prefix="oss_monitor_test_"))
        self.test_config_file = self.test_dir / "test_config.json"
        self.test_db_file = self.test_dir / "test_monitor.db"
        
        print(f"测试目录: {self.test_dir}")
        
    def create_test_config(self):
        """创建测试配置文件"""
        test_config = {
            "buckets": [
                {
                    "name": "test-bucket-1",
                    "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
                    "access_key_id": "test-access-key-id",
                    "access_key_secret": "test-access-key-secret",
                    "description": "测试桶1"
                },
                {
                    "name": "test-bucket-2",
                    "endpoint": "https://oss-cn-beijing.aliyuncs.com",
                    "access_key_id": "test-access-key-id-2",
                    "access_key_secret": "test-access-key-secret-2",
                    "description": "测试桶2"
                }
            ],
            "monitoring": {
                "check_interval_hours": 24,
                "retention_days": 30,
                "alert_threshold_gb": 100,
                "enable_daily_reports": True
            },
            "database": {
                "path": str(self.test_db_file),
                "backup_interval_days": 7
            },
            "reports": {
                "output_dir": str(self.test_dir / "reports"),
                "generate_charts": True,
                "chart_format": "png"
            },
            "logging": {
                "level": "INFO",
                "file": str(self.test_dir / "test_monitor.log"),
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=4, ensure_ascii=False)
        
        print("✓ 测试配置文件已创建")
    
    def test_database_initialization(self):
        """测试数据库初始化"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 检查数据库文件是否存在
            if not self.test_db_file.exists():
                raise Exception("数据库文件未创建")
            
            # 检查表结构
            conn = sqlite3.connect(self.test_db_file)
            cursor = conn.cursor()
            
            # 检查storage_stats表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='storage_stats'")
            if not cursor.fetchone():
                raise Exception("storage_stats表未创建")
            
            # 检查bucket_info表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bucket_info'")
            if not cursor.fetchone():
                raise Exception("bucket_info表未创建")
            
            conn.close()
            print("✓ 数据库初始化测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 数据库初始化测试失败: {e}")
            return False
    
    def test_config_loading(self):
        """测试配置文件加载"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 检查配置是否正确加载
            if not monitor.config.get('buckets'):
                raise Exception("桶配置未加载")
            
            if len(monitor.config['buckets']) != 2:
                raise Exception(f"桶数量不正确: {len(monitor.config['buckets'])}")
            
            print("✓ 配置文件加载测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 配置文件加载测试失败: {e}")
            return False
    
    def test_database_operations(self):
        """测试数据库操作"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 模拟存储统计数据
            test_stats = {
                'bucket_name': 'test-bucket-1',
                'total_size_bytes': 1024 * 1024 * 1024,  # 1GB
                'object_count': 1000,
                'check_time': datetime.now()
            }
            
            # 保存统计数据
            monitor.save_storage_stats(test_stats)
            
            # 验证数据是否保存
            conn = sqlite3.connect(self.test_db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM storage_stats WHERE bucket_name = ?", 
                         ('test-bucket-1',))
            count = cursor.fetchone()[0]
            
            if count == 0:
                raise Exception("统计数据未保存")
            
            conn.close()
            print("✓ 数据库操作测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 数据库操作测试失败: {e}")
            return False
    
    def test_daily_increase_calculation(self):
        """测试每日新增存储量计算"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 添加昨天的数据
            yesterday_stats = {
                'bucket_name': 'test-bucket-1',
                'total_size_bytes': 500 * 1024 * 1024,  # 500MB
                'object_count': 500,
                'check_time': datetime.now() - timedelta(days=1)
            }
            monitor.save_storage_stats(yesterday_stats)
            
            # 添加今天的数据
            today_stats = {
                'bucket_name': 'test-bucket-1',
                'total_size_bytes': 1024 * 1024 * 1024,  # 1GB
                'object_count': 1000,
                'check_time': datetime.now()
            }
            monitor.save_storage_stats(today_stats)
            
            # 计算每日新增
            daily_increase = monitor.calculate_daily_increase('test-bucket-1', 1024 * 1024 * 1024)
            expected_increase = 1024 * 1024 * 1024 - 500 * 1024 * 1024  # 524MB
            
            if daily_increase != expected_increase:
                raise Exception(f"每日新增计算错误: 期望 {expected_increase}, 实际 {daily_increase}")
            
            print("✓ 每日新增存储量计算测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 每日新增存储量计算测试失败: {e}")
            return False
    
    def test_history_data_retrieval(self):
        """测试历史数据获取"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 添加一些测试数据
            for i in range(5):
                stats = {
                    'bucket_name': 'test-bucket-1',
                    'total_size_bytes': (i + 1) * 100 * 1024 * 1024,  # 100MB, 200MB, ...
                    'object_count': (i + 1) * 100,
                    'check_time': datetime.now() - timedelta(days=i)
                }
                monitor.save_storage_stats(stats)
            
            # 获取历史数据
            df = monitor.get_storage_history('test-bucket-1', days=7)
            
            if df.empty:
                raise Exception("未获取到历史数据")
            
            if len(df) != 5:
                raise Exception(f"历史数据数量不正确: 期望 5, 实际 {len(df)}")
            
            # 检查数据转换
            if 'total_size_gb' not in df.columns:
                raise Exception("数据转换失败: 缺少 total_size_gb 列")
            
            print("✓ 历史数据获取测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 历史数据获取测试失败: {e}")
            return False
    
    def test_report_generation(self):
        """测试报告生成"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 添加测试数据
            for i in range(10):
                stats = {
                    'bucket_name': 'test-bucket-1',
                    'total_size_bytes': (i + 1) * 50 * 1024 * 1024,  # 50MB, 100MB, ...
                    'object_count': (i + 1) * 50,
                    'check_time': datetime.now() - timedelta(days=i)
                }
                monitor.save_storage_stats(stats)
            
            # 生成报告
            monitor.generate_storage_report('test-bucket-1', days=10)
            
            # 检查报告文件是否生成
            reports_dir = self.test_dir / "reports"
            if not reports_dir.exists():
                raise Exception("报告目录未创建")
            
            report_files = list(reports_dir.glob("*.txt"))
            if not report_files:
                raise Exception("报告文件未生成")
            
            print("✓ 报告生成测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 报告生成测试失败: {e}")
            return False
    
    def test_cleanup_functionality(self):
        """测试数据清理功能"""
        try:
            monitor = OSSStorageMonitor(str(self.test_config_file))
            
            # 添加一些旧数据
            old_stats = {
                'bucket_name': 'test-bucket-1',
                'total_size_bytes': 100 * 1024 * 1024,
                'object_count': 100,
                'check_time': datetime.now() - timedelta(days=40)  # 超过30天保留期
            }
            monitor.save_storage_stats(old_stats)
            
            # 添加新数据
            new_stats = {
                'bucket_name': 'test-bucket-1',
                'total_size_bytes': 200 * 1024 * 1024,
                'object_count': 200,
                'check_time': datetime.now()
            }
            monitor.save_storage_stats(new_stats)
            
            # 执行清理
            monitor.cleanup_old_data()
            
            # 检查旧数据是否被清理
            conn = sqlite3.connect(self.test_db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM storage_stats WHERE check_time < ?", 
                         (datetime.now() - timedelta(days=30),))
            old_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM storage_stats")
            total_count = cursor.fetchone()[0]
            
            conn.close()
            
            if old_count != 0:
                raise Exception(f"旧数据未被清理: {old_count} 条记录")
            
            if total_count != 1:
                raise Exception(f"清理后数据数量不正确: 期望 1, 实际 {total_count}")
            
            print("✓ 数据清理功能测试通过")
            return True
            
        except Exception as e:
            print(f"✗ 数据清理功能测试失败: {e}")
            return False
    
    def cleanup(self):
        """清理测试文件"""
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            print("✓ 测试文件已清理")
        except Exception as e:
            print(f"✗ 清理测试文件失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始运行OSS监控系统测试...")
        print("=" * 50)
        
        tests = [
            ("配置文件加载", self.test_config_loading),
            ("数据库初始化", self.test_database_initialization),
            ("数据库操作", self.test_database_operations),
            ("每日新增计算", self.test_daily_increase_calculation),
            ("历史数据获取", self.test_history_data_retrieval),
            ("报告生成", self.test_report_generation),
            ("数据清理", self.test_cleanup_functionality),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n运行测试: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"✗ 测试异常: {e}")
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"测试结果: 通过 {passed}, 失败 {failed}")
        
        if failed == 0:
            print("🎉 所有测试通过！系统功能正常")
        else:
            print("❌ 部分测试失败，请检查系统配置")
        
        return failed == 0


def main():
    """主函数"""
    tester = OSSMonitorTester()
    
    try:
        # 创建测试配置
        tester.create_test_config()
        
        # 运行测试
        success = tester.run_all_tests()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
        return 1
    except Exception as e:
        print(f"\n测试执行失败: {e}")
        return 1
    finally:
        # 清理测试文件
        tester.cleanup()


if __name__ == "__main__":
    sys.exit(main())