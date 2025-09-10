#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS存储监控系统演示脚本
展示如何使用监控系统的各种功能
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oss_storage_monitor import OSSStorageMonitor


def create_demo_config():
    """创建演示配置文件"""
    demo_config = {
        "buckets": [
            {
                "name": "demo-bucket-1",
                "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
                "access_key_id": "demo-access-key-id",
                "access_key_secret": "demo-access-key-secret",
                "description": "演示存储桶1"
            },
            {
                "name": "demo-bucket-2",
                "endpoint": "https://oss-cn-beijing.aliyuncs.com",
                "access_key_id": "demo-access-key-id-2",
                "access_key_secret": "demo-access-key-secret-2",
                "description": "演示存储桶2"
            }
        ],
        "monitoring": {
            "check_interval_hours": 24,
            "retention_days": 30,
            "alert_threshold_gb": 100,
            "enable_daily_reports": True
        },
        "database": {
            "path": "demo_monitor.db",
            "backup_interval_days": 7
        },
        "reports": {
            "output_dir": "./demo_reports",
            "generate_charts": True,
            "chart_format": "png"
        },
        "logging": {
            "level": "INFO",
            "file": "demo_monitor.log",
            "max_size_mb": 10,
            "backup_count": 5
        }
    }
    
    with open("demo_config.json", 'w', encoding='utf-8') as f:
        json.dump(demo_config, f, indent=4, ensure_ascii=False)
    
    print("✓ 演示配置文件已创建: demo_config.json")


def simulate_storage_data(monitor, bucket_name, days=30):
    """模拟存储数据"""
    print(f"正在为 {bucket_name} 生成 {days} 天的模拟数据...")
    
    base_size = 100 * 1024 * 1024  # 100MB
    base_objects = 1000
    
    for i in range(days):
        # 模拟存储量增长
        growth_factor = 1 + (i * 0.05)  # 每天增长5%
        size_variation = 1 + (i % 7) * 0.1  # 每周循环变化
        
        total_size = int(base_size * growth_factor * size_variation)
        object_count = int(base_objects * growth_factor)
        
        stats = {
            'bucket_name': bucket_name,
            'total_size_bytes': total_size,
            'object_count': object_count,
            'check_time': datetime.now() - timedelta(days=days-i-1)
        }
        
        monitor.save_storage_stats(stats)
        
        if (i + 1) % 10 == 0:
            print(f"  已生成 {i + 1}/{days} 天数据")
    
    print(f"✓ {bucket_name} 模拟数据生成完成")


def demo_basic_monitoring():
    """演示基本监控功能"""
    print("\n" + "="*60)
    print("演示1: 基本监控功能")
    print("="*60)
    
    # 创建监控器
    monitor = OSSStorageMonitor("demo_config.json")
    
    # 为两个桶生成模拟数据
    simulate_storage_data(monitor, "demo-bucket-1", 30)
    simulate_storage_data(monitor, "demo-bucket-2", 30)
    
    print("\n✓ 模拟数据生成完成")
    
    # 显示当前状态
    print("\n当前存储状态:")
    for bucket in monitor.config['buckets']:
        bucket_name = bucket['name']
        df = monitor.get_storage_history(bucket_name, days=1)
        
        if not df.empty:
            latest = df.iloc[-1]
            print(f"  {bucket_name}:")
            print(f"    存储量: {latest['total_size_gb']:.2f} GB")
            print(f"    对象数: {latest['object_count']:,}")
            print(f"    今日新增: {latest['daily_increase_gb']:.2f} GB")


def demo_data_analysis():
    """演示数据分析功能"""
    print("\n" + "="*60)
    print("演示2: 数据分析功能")
    print("="*60)
    
    monitor = OSSStorageMonitor("demo_config.json")
    
    # 获取所有桶的历史数据
    all_buckets_df = monitor.get_storage_history(days=30)
    
    if all_buckets_df.empty:
        print("没有找到历史数据")
        return
    
    print("\n存储趋势分析:")
    print("-" * 40)
    
    # 按桶分组分析
    for bucket_name in all_buckets_df['bucket_name'].unique():
        bucket_df = all_buckets_df[all_buckets_df['bucket_name'] == bucket_name]
        
        print(f"\n{bucket_name}:")
        print(f"  当前存储: {bucket_df['total_size_gb'].iloc[-1]:.2f} GB")
        print(f"  平均每日新增: {bucket_df['daily_increase_gb'].mean():.2f} GB")
        print(f"  最大每日新增: {bucket_df['daily_increase_gb'].max():.2f} GB")
        print(f"  总新增存储: {bucket_df['daily_increase_gb'].sum():.2f} GB")
        print(f"  存储增长率: {((bucket_df['total_size_gb'].iloc[-1] / bucket_df['total_size_gb'].iloc[0]) - 1) * 100:.1f}%")


def demo_report_generation():
    """演示报告生成功能"""
    print("\n" + "="*60)
    print("演示3: 报告生成功能")
    print("="*60)
    
    monitor = OSSStorageMonitor("demo_config.json")
    
    # 生成所有桶的报告
    print("正在生成存储报告...")
    monitor.generate_storage_report(days=30)
    
    # 生成各桶的单独报告
    for bucket in monitor.config['buckets']:
        bucket_name = bucket['name']
        print(f"正在生成 {bucket_name} 的报告...")
        monitor.generate_storage_report(bucket_name, days=30)
    
    # 检查报告文件
    reports_dir = Path("demo_reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.txt"))
        chart_files = list(reports_dir.glob("*.png"))
        
        print(f"\n✓ 报告生成完成:")
        print(f"  文本报告: {len(report_files)} 个")
        print(f"  图表文件: {len(chart_files)} 个")
        print(f"  报告目录: {reports_dir.absolute()}")
        
        # 显示报告内容预览
        if report_files:
            print(f"\n报告内容预览 ({report_files[0].name}):")
            print("-" * 40)
            with open(report_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
                # 显示前500个字符
                print(content[:500] + "..." if len(content) > 500 else content)


def demo_alert_system():
    """演示告警系统"""
    print("\n" + "="*60)
    print("演示4: 告警系统")
    print("="*60)
    
    monitor = OSSStorageMonitor("demo_config.json")
    
    # 获取当前存储状态
    all_buckets_df = monitor.get_storage_history(days=1)
    
    if all_buckets_df.empty:
        print("没有找到存储数据")
        return
    
    alert_threshold = monitor.config['monitoring']['alert_threshold_gb']
    
    print(f"告警阈值: {alert_threshold} GB")
    print("-" * 40)
    
    for bucket_name in all_buckets_df['bucket_name'].unique():
        bucket_df = all_buckets_df[all_buckets_df['bucket_name'] == bucket_name]
        current_size = bucket_df['total_size_gb'].iloc[-1]
        
        print(f"\n{bucket_name}:")
        print(f"  当前存储: {current_size:.2f} GB")
        
        if current_size > alert_threshold:
            print(f"  ⚠️  告警: 存储量超过阈值 ({current_size:.2f} GB > {alert_threshold} GB)")
        else:
            print(f"  ✅ 正常: 存储量在阈值范围内")


def demo_cleanup_functionality():
    """演示数据清理功能"""
    print("\n" + "="*60)
    print("演示5: 数据清理功能")
    print("="*60)
    
    monitor = OSSStorageMonitor("demo_config.json")
    
    # 添加一些超过保留期的旧数据
    old_date = datetime.now() - timedelta(days=40)
    old_stats = {
        'bucket_name': 'demo-bucket-1',
        'total_size_bytes': 50 * 1024 * 1024,
        'object_count': 500,
        'check_time': old_date
    }
    monitor.save_storage_stats(old_stats)
    
    # 检查清理前的数据量
    conn = monitor.monitor.db_path if hasattr(monitor, 'monitor') else monitor.db_path
    import sqlite3
    conn = sqlite3.connect(conn)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM storage_stats")
    before_count = cursor.fetchone()[0]
    
    print(f"清理前数据量: {before_count} 条记录")
    
    # 执行清理
    print("正在执行数据清理...")
    monitor.cleanup_old_data()
    
    # 检查清理后的数据量
    cursor.execute("SELECT COUNT(*) FROM storage_stats")
    after_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"清理后数据量: {after_count} 条记录")
    print(f"清理了 {before_count - after_count} 条过期记录")


def demo_web_dashboard():
    """演示Web仪表板"""
    print("\n" + "="*60)
    print("演示6: Web仪表板")
    print("="*60)
    
    print("Web仪表板功能:")
    print("1. 实时存储状态监控")
    print("2. 存储趋势图表")
    print("3. 桶对比分析")
    print("4. 报告生成")
    print("5. 手动触发检查")
    
    print("\n启动Web仪表板:")
    print("  python3 oss_monitor_dashboard.py --config demo_config.json")
    print("\n然后访问: http://localhost:5000")
    
    print("\nWeb仪表板特性:")
    print("  - 响应式设计，支持移动端")
    print("  - 实时数据更新")
    print("  - 交互式图表")
    print("  - 多桶对比")
    print("  - 一键报告生成")


def demo_scheduler():
    """演示定时调度器"""
    print("\n" + "="*60)
    print("演示7: 定时调度器")
    print("="*60)
    
    print("定时调度器功能:")
    print("1. 自动存储检查")
    print("2. 定期报告生成")
    print("3. 数据清理")
    print("4. 告警通知")
    
    print("\n启动定时调度器:")
    print("  python3 oss_monitor_scheduler.py --config demo_config.json")
    
    print("\n单次任务执行:")
    print("  python3 oss_monitor_scheduler.py --run-once check")
    print("  python3 oss_monitor_scheduler.py --run-once report")
    print("  python3 oss_monitor_scheduler.py --run-once cleanup")
    
    print("\n系统服务:")
    print("  sudo systemctl enable oss-monitor")
    print("  sudo systemctl start oss-monitor")


def cleanup_demo_files():
    """清理演示文件"""
    print("\n" + "="*60)
    print("清理演示文件")
    print("="*60)
    
    demo_files = [
        "demo_config.json",
        "demo_monitor.db",
        "demo_monitor.log",
        "demo_reports"
    ]
    
    for file_path in demo_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"✓ 已删除文件: {file_path}")
            else:
                import shutil
                shutil.rmtree(path)
                print(f"✓ 已删除目录: {file_path}")


def main():
    """主函数"""
    print("OSS存储监控系统演示")
    print("="*60)
    
    try:
        # 创建演示配置
        create_demo_config()
        
        # 运行各种演示
        demo_basic_monitoring()
        demo_data_analysis()
        demo_report_generation()
        demo_alert_system()
        demo_cleanup_functionality()
        demo_web_dashboard()
        demo_scheduler()
        
        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
        
        print("\n下一步操作:")
        print("1. 编辑 demo_config.json 配置真实的OSS桶信息")
        print("2. 运行测试: python3 test_oss_monitor.py")
        print("3. 启动Web仪表板: python3 oss_monitor_dashboard.py --config demo_config.json")
        print("4. 启动定时调度器: python3 oss_monitor_scheduler.py --config demo_config.json")
        
        # 询问是否清理演示文件
        response = input("\n是否清理演示文件？(y/n): ").strip().lower()
        if response == 'y':
            cleanup_demo_files()
        else:
            print("演示文件已保留，您可以继续使用")
        
    except KeyboardInterrupt:
        print("\n用户中断演示")
    except Exception as e:
        print(f"\n演示执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()