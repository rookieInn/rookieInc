#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS存储监控定时任务调度器
支持cron表达式和系统服务
"""

import os
import sys
import time
import json
import logging
import schedule
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# 导入监控器
from oss_storage_monitor import OSSStorageMonitor


class OSSMonitorScheduler:
    """OSS监控定时调度器"""
    
    def __init__(self, config_file: str = "oss_monitor_config.json"):
        """初始化调度器"""
        self.config_file = config_file
        self.monitor = OSSStorageMonitor(config_file)
        self._setup_logging()
        
        # 加载调度配置
        self.schedule_config = self._load_schedule_config()
        
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('oss_monitor_scheduler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def _load_schedule_config(self) -> Dict[str, Any]:
        """加载调度配置"""
        config = self.monitor.config
        
        # 默认调度配置
        default_schedule = {
            "check_interval": "daily",  # daily, hourly, weekly
            "check_time": "02:00",      # 检查时间 (HH:MM)
            "report_interval": "weekly", # 报告生成间隔
            "report_time": "09:00",     # 报告生成时间
            "cleanup_interval": "monthly", # 数据清理间隔
            "cleanup_time": "03:00",    # 数据清理时间
            "enable_notifications": True,  # 启用通知
            "notification_webhook": "",    # 通知webhook URL
            "max_retries": 3,          # 最大重试次数
            "retry_delay": 300         # 重试延迟(秒)
        }
        
        # 合并用户配置
        user_schedule = config.get('scheduler', {})
        for key, value in user_schedule.items():
            if key in default_schedule:
                default_schedule[key] = value
        
        return default_schedule
    
    def check_storage(self):
        """执行存储检查任务"""
        try:
            logging.info("开始执行存储检查任务")
            start_time = time.time()
            
            self.monitor.check_all_buckets()
            
            duration = time.time() - start_time
            logging.info(f"存储检查任务完成，耗时: {duration:.2f}秒")
            
            # 发送成功通知
            self._send_notification("存储检查完成", f"检查耗时: {duration:.2f}秒")
            
        except Exception as e:
            logging.error(f"存储检查任务失败: {e}")
            self._send_notification("存储检查失败", str(e))
            raise
    
    def generate_reports(self):
        """生成报告任务"""
        try:
            logging.info("开始生成存储报告")
            start_time = time.time()
            
            # 生成所有桶的报告
            self.monitor.generate_storage_report(days=30)
            
            # 生成各桶的单独报告
            buckets = self.monitor.config.get('buckets', [])
            for bucket in buckets:
                bucket_name = bucket['name']
                self.monitor.generate_storage_report(bucket_name, days=30)
            
            duration = time.time() - start_time
            logging.info(f"报告生成任务完成，耗时: {duration:.2f}秒")
            
            self._send_notification("报告生成完成", f"生成了 {len(buckets) + 1} 个报告")
            
        except Exception as e:
            logging.error(f"报告生成任务失败: {e}")
            self._send_notification("报告生成失败", str(e))
            raise
    
    def cleanup_old_data(self):
        """清理旧数据任务"""
        try:
            logging.info("开始清理旧数据")
            start_time = time.time()
            
            self.monitor.cleanup_old_data()
            
            duration = time.time() - start_time
            logging.info(f"数据清理任务完成，耗时: {duration:.2f}秒")
            
            self._send_notification("数据清理完成", f"清理耗时: {duration:.2f}秒")
            
        except Exception as e:
            logging.error(f"数据清理任务失败: {e}")
            self._send_notification("数据清理失败", str(e))
            raise
    
    def _send_notification(self, title: str, message: str):
        """发送通知"""
        if not self.schedule_config.get('enable_notifications', False):
            return
        
        try:
            webhook_url = self.schedule_config.get('notification_webhook', '')
            if not webhook_url:
                logging.info(f"通知: {title} - {message}")
                return
            
            # 这里可以集成各种通知方式
            # 例如：钉钉、企业微信、邮件等
            self._send_webhook_notification(webhook_url, title, message)
            
        except Exception as e:
            logging.error(f"发送通知失败: {e}")
    
    def _send_webhook_notification(self, webhook_url: str, title: str, message: str):
        """发送webhook通知"""
        try:
            import requests
            
            payload = {
                "title": title,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "service": "OSS存储监控"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info("通知发送成功")
            
        except Exception as e:
            logging.error(f"发送webhook通知失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        try:
            # 清除现有任务
            schedule.clear()
            
            # 存储检查任务
            check_interval = self.schedule_config.get('check_interval', 'daily')
            check_time = self.schedule_config.get('check_time', '02:00')
            
            if check_interval == 'daily':
                schedule.every().day.at(check_time).do(self.check_storage)
            elif check_interval == 'hourly':
                schedule.every().hour.do(self.check_storage)
            elif check_interval == 'weekly':
                schedule.every().monday.at(check_time).do(self.check_storage)
            
            # 报告生成任务
            report_interval = self.schedule_config.get('report_interval', 'weekly')
            report_time = self.schedule_config.get('report_time', '09:00')
            
            if report_interval == 'daily':
                schedule.every().day.at(report_time).do(self.generate_reports)
            elif report_interval == 'weekly':
                schedule.every().monday.at(report_time).do(self.generate_reports)
            elif report_interval == 'monthly':
                schedule.every().month.do(self.generate_reports)
            
            # 数据清理任务
            cleanup_interval = self.schedule_config.get('cleanup_interval', 'monthly')
            cleanup_time = self.schedule_config.get('cleanup_time', '03:00')
            
            if cleanup_interval == 'daily':
                schedule.every().day.at(cleanup_time).do(self.cleanup_old_data)
            elif cleanup_interval == 'weekly':
                schedule.every().sunday.at(cleanup_time).do(self.cleanup_old_data)
            elif cleanup_interval == 'monthly':
                schedule.every().month.do(self.cleanup_old_data)
            
            logging.info("定时任务设置完成")
            self._print_schedule_info()
            
        except Exception as e:
            logging.error(f"设置定时任务失败: {e}")
            raise
    
    def _print_schedule_info(self):
        """打印调度信息"""
        logging.info("当前调度任务:")
        for job in schedule.jobs:
            logging.info(f"  - {job.job_func.__name__}: {job.next_run}")
    
    def run_scheduler(self):
        """运行调度器"""
        try:
            logging.info("OSS监控调度器启动")
            self.setup_schedule()
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logging.info("用户中断调度器")
        except Exception as e:
            logging.error(f"调度器运行失败: {e}")
            raise
    
    def run_once(self, task: str):
        """运行单次任务"""
        try:
            if task == 'check':
                self.check_storage()
            elif task == 'report':
                self.generate_reports()
            elif task == 'cleanup':
                self.cleanup_old_data()
            else:
                raise ValueError(f"未知任务: {task}")
                
        except Exception as e:
            logging.error(f"执行任务 {task} 失败: {e}")
            raise


def create_systemd_service():
    """创建systemd服务文件"""
    service_content = '''[Unit]
Description=OSS Storage Monitor Scheduler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace
ExecStart=/usr/bin/python3 /workspace/oss_monitor_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    with open('/etc/systemd/system/oss-monitor.service', 'w') as f:
        f.write(service_content)
    
    print("systemd服务文件已创建: /etc/systemd/system/oss-monitor.service")
    print("使用以下命令启用服务:")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable oss-monitor")
    print("  sudo systemctl start oss-monitor")


def create_cron_job():
    """创建cron任务"""
    cron_content = '''# OSS存储监控定时任务
# 每天凌晨2点检查存储
0 2 * * * /usr/bin/python3 /workspace/oss_monitor_scheduler.py --run-once check

# 每周一上午9点生成报告
0 9 * * 1 /usr/bin/python3 /workspace/oss_monitor_scheduler.py --run-once report

# 每月1号凌晨3点清理旧数据
0 3 1 * * /usr/bin/python3 /workspace/oss_monitor_scheduler.py --run-once cleanup
'''
    
    cron_file = '/etc/cron.d/oss-monitor'
    with open(cron_file, 'w') as f:
        f.write(cron_content)
    
    print(f"cron任务已创建: {cron_file}")
    print("使用以下命令查看cron任务:")
    print("  crontab -l")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OSS存储监控定时调度器')
    parser.add_argument('--config', '-c', default='oss_monitor_config.json', 
                       help='配置文件路径')
    parser.add_argument('--run-once', choices=['check', 'report', 'cleanup'],
                       help='运行单次任务')
    parser.add_argument('--daemon', action='store_true',
                       help='以守护进程模式运行')
    parser.add_argument('--create-service', action='store_true',
                       help='创建systemd服务文件')
    parser.add_argument('--create-cron', action='store_true',
                       help='创建cron任务')
    
    args = parser.parse_args()
    
    try:
        if args.create_service:
            create_systemd_service()
            return
        
        if args.create_cron:
            create_cron_job()
            return
        
        scheduler = OSSMonitorScheduler(args.config)
        
        if args.run_once:
            scheduler.run_once(args.run_once)
        else:
            if args.daemon:
                # 守护进程模式
                import daemon
                with daemon.DaemonContext():
                    scheduler.run_scheduler()
            else:
                scheduler.run_scheduler()
                
    except KeyboardInterrupt:
        logging.info("用户中断操作")
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()