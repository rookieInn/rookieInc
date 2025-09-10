#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS桶每日新增存储监控系统
功能：
1. 监控OSS桶的存储使用情况
2. 计算每日新增存储量
3. 生成存储趋势报告
4. 支持多桶监控
5. 数据持久化存储
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import argparse

# 第三方库导入
try:
    import oss2
    from oss2.credentials import EnvironmentVariableCredentialsProvider
except ImportError:
    print("请安装oss2库: pip install oss2")
    sys.exit(1)

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib import font_manager
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except ImportError:
    print("请安装数据可视化库: pip install pandas matplotlib")
    sys.exit(1)


class OSSStorageMonitor:
    """OSS存储监控器"""
    
    def __init__(self, config_file: str = "oss_monitor_config.json"):
        """初始化监控器"""
        self.config = self._load_config(config_file)
        self.db_path = self.config.get('database', {}).get('path', 'oss_monitor.db')
        self._init_database()
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
            "buckets": [
                {
                    "name": "your-bucket-1",
                    "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
                    "access_key_id": "your-access-key-id",
                    "access_key_secret": "your-access-key-secret",
                    "description": "主存储桶"
                }
            ],
            "monitoring": {
                "check_interval_hours": 24,
                "retention_days": 365,
                "alert_threshold_gb": 1000,
                "enable_daily_reports": True
            },
            "database": {
                "path": "oss_monitor.db",
                "backup_interval_days": 7
            },
            "reports": {
                "output_dir": "./reports",
                "generate_charts": True,
                "chart_format": "png"
            },
            "logging": {
                "level": "INFO",
                "file": "oss_monitor.log",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        print(f"已创建默认配置文件: {config_file}")
        print("请编辑配置文件填入正确的OSS桶信息")
        sys.exit(1)
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建存储统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bucket_name TEXT NOT NULL,
                    check_time TIMESTAMP NOT NULL,
                    total_size_bytes INTEGER NOT NULL,
                    object_count INTEGER NOT NULL,
                    daily_increase_bytes INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建桶信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bucket_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bucket_name TEXT UNIQUE NOT NULL,
                    endpoint TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_storage_stats_bucket_time 
                ON storage_stats(bucket_name, check_time)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
            raise
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'oss_monitor.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _get_oss_client(self, bucket_config: Dict[str, str]):
        """获取OSS客户端"""
        try:
            auth = oss2.Auth(
                bucket_config['access_key_id'],
                bucket_config['access_key_secret']
            )
            return oss2.Bucket(
                auth,
                bucket_config['endpoint'],
                bucket_config['name']
            )
        except Exception as e:
            logging.error(f"创建OSS客户端失败: {e}")
            raise
    
    def get_bucket_storage_info(self, bucket_config: Dict[str, str]) -> Dict[str, Any]:
        """获取桶的存储信息"""
        try:
            bucket_client = self._get_oss_client(bucket_config)
            bucket_name = bucket_config['name']
            
            logging.info(f"开始检查桶: {bucket_name}")
            
            # 获取桶的基本信息
            bucket_info = bucket_client.get_bucket_info()
            total_size = bucket_info.storage_size_in_bytes
            object_count = bucket_info.object_count
            
            logging.info(f"桶 {bucket_name} 存储信息: {total_size} bytes, {object_count} 个对象")
            
            return {
                'bucket_name': bucket_name,
                'total_size_bytes': total_size,
                'object_count': object_count,
                'check_time': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"获取桶 {bucket_config['name']} 存储信息失败: {e}")
            raise
    
    def calculate_daily_increase(self, bucket_name: str, current_size: int) -> int:
        """计算每日新增存储量"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取昨天的记录
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute('''
                SELECT total_size_bytes FROM storage_stats 
                WHERE bucket_name = ? AND check_time < ?
                ORDER BY check_time DESC LIMIT 1
            ''', (bucket_name, yesterday))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                previous_size = result[0]
                daily_increase = current_size - previous_size
                return max(0, daily_increase)  # 确保不为负数
            else:
                logging.info(f"桶 {bucket_name} 没有历史记录，新增存储量设为0")
                return 0
                
        except Exception as e:
            logging.error(f"计算每日新增存储量失败: {e}")
            return 0
    
    def save_storage_stats(self, stats: Dict[str, Any]):
        """保存存储统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 计算每日新增存储量
            daily_increase = self.calculate_daily_increase(
                stats['bucket_name'], 
                stats['total_size_bytes']
            )
            
            # 插入新记录
            cursor.execute('''
                INSERT INTO storage_stats 
                (bucket_name, check_time, total_size_bytes, object_count, daily_increase_bytes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                stats['bucket_name'],
                stats['check_time'],
                stats['total_size_bytes'],
                stats['object_count'],
                daily_increase
            ))
            
            conn.commit()
            conn.close()
            
            logging.info(f"已保存桶 {stats['bucket_name']} 的存储统计信息")
            
        except Exception as e:
            logging.error(f"保存存储统计信息失败: {e}")
            raise
    
    def get_storage_history(self, bucket_name: str = None, days: int = 30) -> pd.DataFrame:
        """获取存储历史数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if bucket_name:
                query = '''
                    SELECT * FROM storage_stats 
                    WHERE bucket_name = ? AND check_time >= ?
                    ORDER BY check_time ASC
                '''
                cutoff_date = datetime.now() - timedelta(days=days)
                df = pd.read_sql_query(query, conn, params=(bucket_name, cutoff_date))
            else:
                query = '''
                    SELECT * FROM storage_stats 
                    WHERE check_time >= ?
                    ORDER BY check_time ASC
                '''
                cutoff_date = datetime.now() - timedelta(days=days)
                df = pd.read_sql_query(query, conn, params=(cutoff_date,))
            
            conn.close()
            
            # 转换数据类型
            df['check_time'] = pd.to_datetime(df['check_time'])
            df['total_size_gb'] = df['total_size_bytes'] / (1024**3)
            df['daily_increase_gb'] = df['daily_increase_bytes'] / (1024**3)
            
            return df
            
        except Exception as e:
            logging.error(f"获取存储历史数据失败: {e}")
            return pd.DataFrame()
    
    def generate_storage_report(self, bucket_name: str = None, days: int = 30):
        """生成存储报告"""
        try:
            # 获取历史数据
            df = self.get_storage_history(bucket_name, days)
            
            if df.empty:
                logging.warning("没有找到历史数据，无法生成报告")
                return
            
            # 创建报告目录
            report_dir = Path(self.config.get('reports', {}).get('output_dir', './reports'))
            report_dir.mkdir(exist_ok=True)
            
            # 生成文本报告
            self._generate_text_report(df, report_dir, bucket_name, days)
            
            # 生成图表
            if self.config.get('reports', {}).get('generate_charts', True):
                self._generate_charts(df, report_dir, bucket_name, days)
            
            logging.info(f"存储报告已生成到: {report_dir}")
            
        except Exception as e:
            logging.error(f"生成存储报告失败: {e}")
            raise
    
    def _generate_text_report(self, df: pd.DataFrame, report_dir: Path, bucket_name: str, days: int):
        """生成文本报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bucket_suffix = f"_{bucket_name}" if bucket_name else "_all_buckets"
            report_file = report_dir / f"storage_report{bucket_suffix}_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("OSS存储监控报告\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"监控周期: 最近 {days} 天\n")
                if bucket_name:
                    f.write(f"监控桶: {bucket_name}\n")
                else:
                    f.write("监控范围: 所有桶\n")
                f.write("\n")
                
                # 总体统计
                if bucket_name:
                    bucket_df = df[df['bucket_name'] == bucket_name]
                else:
                    bucket_df = df
                
                if not bucket_df.empty:
                    latest = bucket_df.iloc[-1]
                    f.write("当前状态:\n")
                    f.write(f"  总存储量: {latest['total_size_gb']:.2f} GB\n")
                    f.write(f"  对象数量: {latest['object_count']:,}\n")
                    f.write(f"  今日新增: {latest['daily_increase_gb']:.2f} GB\n\n")
                    
                    # 统计信息
                    f.write("统计信息:\n")
                    f.write(f"  平均每日新增: {bucket_df['daily_increase_gb'].mean():.2f} GB\n")
                    f.write(f"  最大每日新增: {bucket_df['daily_increase_gb'].max():.2f} GB\n")
                    f.write(f"  最小每日新增: {bucket_df['daily_increase_gb'].min():.2f} GB\n")
                    f.write(f"  总新增存储: {bucket_df['daily_increase_gb'].sum():.2f} GB\n\n")
                    
                    # 按桶统计（如果监控多个桶）
                    if not bucket_name:
                        f.write("各桶统计:\n")
                        bucket_stats = df.groupby('bucket_name').agg({
                            'total_size_gb': 'last',
                            'daily_increase_gb': ['mean', 'sum'],
                            'object_count': 'last'
                        }).round(2)
                        
                        for bucket in bucket_stats.index:
                            f.write(f"  {bucket}:\n")
                            f.write(f"    当前存储: {bucket_stats.loc[bucket, ('total_size_gb', 'last')]:.2f} GB\n")
                            f.write(f"    平均新增: {bucket_stats.loc[bucket, ('daily_increase_gb', 'mean')]:.2f} GB/天\n")
                            f.write(f"    总新增: {bucket_stats.loc[bucket, ('daily_increase_gb', 'sum')]:.2f} GB\n")
                            f.write(f"    对象数: {bucket_stats.loc[bucket, ('object_count', 'last')]:,}\n\n")
            
            logging.info(f"文本报告已生成: {report_file}")
            
        except Exception as e:
            logging.error(f"生成文本报告失败: {e}")
            raise
    
    def _generate_charts(self, df: pd.DataFrame, report_dir: Path, bucket_name: str, days: int):
        """生成图表"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bucket_suffix = f"_{bucket_name}" if bucket_name else "_all_buckets"
            chart_format = self.config.get('reports', {}).get('chart_format', 'png')
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            if bucket_name:
                # 单桶图表
                bucket_df = df[df['bucket_name'] == bucket_name]
                self._create_single_bucket_charts(bucket_df, report_dir, bucket_name, timestamp, chart_format)
            else:
                # 多桶图表
                self._create_multi_bucket_charts(df, report_dir, timestamp, chart_format)
            
        except Exception as e:
            logging.error(f"生成图表失败: {e}")
            raise
    
    def _create_single_bucket_charts(self, df: pd.DataFrame, report_dir: Path, bucket_name: str, timestamp: str, chart_format: str):
        """创建单桶图表"""
        try:
            # 存储量趋势图
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 总存储量趋势
            ax1.plot(df['check_time'], df['total_size_gb'], marker='o', linewidth=2, markersize=4)
            ax1.set_title(f'{bucket_name} - 存储量趋势', fontsize=14, fontweight='bold')
            ax1.set_ylabel('存储量 (GB)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df)//10)))
            
            # 每日新增存储量
            ax2.bar(df['check_time'], df['daily_increase_gb'], alpha=0.7, color='orange')
            ax2.set_title(f'{bucket_name} - 每日新增存储量', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('新增存储量 (GB)', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df)//10)))
            
            plt.tight_layout()
            chart_file = report_dir / f"storage_trend_{bucket_name}_{timestamp}.{chart_format}"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logging.info(f"单桶图表已生成: {chart_file}")
            
        except Exception as e:
            logging.error(f"创建单桶图表失败: {e}")
            raise
    
    def _create_multi_bucket_charts(self, df: pd.DataFrame, report_dir: Path, timestamp: str, chart_format: str):
        """创建多桶图表"""
        try:
            # 按桶分组的存储量趋势
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # 各桶存储量对比
            for bucket in df['bucket_name'].unique():
                bucket_df = df[df['bucket_name'] == bucket]
                ax1.plot(bucket_df['check_time'], bucket_df['total_size_gb'], 
                        marker='o', linewidth=2, markersize=4, label=bucket)
            
            ax1.set_title('各桶存储量趋势对比', fontsize=14, fontweight='bold')
            ax1.set_ylabel('存储量 (GB)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            # 各桶每日新增存储量对比
            bucket_names = df['bucket_name'].unique()
            x = range(len(df['check_time'].unique()))
            width = 0.8 / len(bucket_names)
            
            for i, bucket in enumerate(bucket_names):
                bucket_df = df[df['bucket_name'] == bucket]
                ax2.bar([j + i * width for j in x], bucket_df['daily_increase_gb'], 
                       width, label=bucket, alpha=0.7)
            
            ax2.set_title('各桶每日新增存储量对比', fontsize=14, fontweight='bold')
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('新增存储量 (GB)', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_file = report_dir / f"multi_bucket_comparison_{timestamp}.{chart_format}"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logging.info(f"多桶对比图表已生成: {chart_file}")
            
        except Exception as e:
            logging.error(f"创建多桶图表失败: {e}")
            raise
    
    def check_all_buckets(self):
        """检查所有配置的桶"""
        try:
            logging.info("开始检查所有OSS桶的存储情况")
            
            buckets = self.config.get('buckets', [])
            if not buckets:
                logging.warning("没有配置任何OSS桶")
                return
            
            for bucket_config in buckets:
                try:
                    # 获取存储信息
                    stats = self.get_bucket_storage_info(bucket_config)
                    
                    # 保存统计信息
                    self.save_storage_stats(stats)
                    
                    # 检查告警阈值
                    self._check_alert_threshold(stats)
                    
                except Exception as e:
                    logging.error(f"检查桶 {bucket_config['name']} 失败: {e}")
                    continue
            
            logging.info("所有桶检查完成")
            
        except Exception as e:
            logging.error(f"检查所有桶失败: {e}")
            raise
    
    def _check_alert_threshold(self, stats: Dict[str, Any]):
        """检查告警阈值"""
        try:
            threshold_gb = self.config.get('monitoring', {}).get('alert_threshold_gb', 1000)
            current_gb = stats['total_size_bytes'] / (1024**3)
            
            if current_gb > threshold_gb:
                logging.warning(f"桶 {stats['bucket_name']} 存储量超过阈值: {current_gb:.2f} GB > {threshold_gb} GB")
                # 这里可以添加发送告警通知的逻辑
                
        except Exception as e:
            logging.error(f"检查告警阈值失败: {e}")
    
    def cleanup_old_data(self):
        """清理旧数据"""
        try:
            retention_days = self.config.get('monitoring', {}).get('retention_days', 365)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM storage_stats WHERE check_time < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logging.info(f"已清理 {deleted_count} 条超过 {retention_days} 天的历史数据")
            
        except Exception as e:
            logging.error(f"清理旧数据失败: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OSS存储监控系统')
    parser.add_argument('--config', '-c', default='oss_monitor_config.json', 
                       help='配置文件路径')
    parser.add_argument('--check', action='store_true', 
                       help='执行存储检查')
    parser.add_argument('--report', action='store_true', 
                       help='生成存储报告')
    parser.add_argument('--bucket', '-b', 
                       help='指定桶名称（仅用于报告）')
    parser.add_argument('--days', '-d', type=int, default=30, 
                       help='报告天数（默认30天）')
    parser.add_argument('--cleanup', action='store_true', 
                       help='清理旧数据')
    
    args = parser.parse_args()
    
    try:
        monitor = OSSStorageMonitor(args.config)
        
        if args.check:
            monitor.check_all_buckets()
        
        if args.report:
            monitor.generate_storage_report(args.bucket, args.days)
        
        if args.cleanup:
            monitor.cleanup_old_data()
        
        if not any([args.check, args.report, args.cleanup]):
            print("请指定操作: --check, --report, 或 --cleanup")
            print("使用 --help 查看详细帮助")
            
    except KeyboardInterrupt:
        logging.info("用户中断操作")
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()