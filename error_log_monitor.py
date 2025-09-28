#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误日志监控系统
监控指定日志文件中的错误，当错误数量超过阈值时发送邮件通知
"""

import os
import re
import json
import time
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque
from typing import List, Dict, Set
import psutil
import platform


class ErrorLogMonitor:
    def __init__(self, config_file: str = "error_monitor_config.json"):
        """初始化错误日志监控器"""
        self.config = self.load_config(config_file)
        self.error_counts = defaultdict(int)  # 文件路径 -> 错误数量
        self.last_check_times = {}  # 文件路径 -> 最后检查时间
        self.notification_history = deque()  # 通知历史记录
        self.setup_logging()
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 不存在，使用默认配置")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "monitor": {
                "log_file_paths": ["./bookmark_sync.log", "./sql_to_docs.log"],
                "error_patterns": ["ERROR", "FATAL", "CRITICAL", "Exception", "Traceback"],
                "time_window_minutes": 5,
                "error_threshold": 10,
                "check_interval_seconds": 30
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_email": "your_email@gmail.com",
                "to_emails": ["admin@yourcompany.com"],
                "subject_prefix": "[系统错误监控]"
            },
            "notification": {
                "cooldown_minutes": 30,
                "max_notifications_per_hour": 5,
                "include_error_details": True,
                "include_system_info": True
            }
        }
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('error_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def is_file_accessible(self, file_path: str) -> bool:
        """检查文件是否可访问"""
        try:
            return os.path.exists(file_path) and os.access(file_path, os.R_OK)
        except Exception:
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def read_log_file(self, file_path: str, last_position: int = 0) -> tuple:
        """读取日志文件的新内容"""
        try:
            if not self.is_file_accessible(file_path):
                return "", last_position
            
            current_size = self.get_file_size(file_path)
            if current_size <= last_position:
                return "", last_position
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_position)
                new_content = f.read()
                return new_content, current_size
        except Exception as e:
            self.logger.error(f"读取文件 {file_path} 失败: {e}")
            return "", last_position
    
    def count_errors_in_content(self, content: str) -> int:
        """统计内容中的错误数量"""
        if not content:
            return 0
        
        error_count = 0
        error_patterns = self.config['monitor']['error_patterns']
        
        for line in content.split('\n'):
            if not line.strip():
                continue
                
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    error_count += 1
                    break
        
        return error_count
    
    def check_log_files(self) -> Dict[str, int]:
        """检查所有日志文件的错误数量"""
        current_time = datetime.now()
        time_window = timedelta(minutes=self.config['monitor']['time_window_minutes'])
        error_counts = defaultdict(int)
        
        for log_file in self.config['monitor']['log_file_paths']:
            if not self.is_file_accessible(log_file):
                self.logger.warning(f"无法访问日志文件: {log_file}")
                continue
            
            # 读取文件内容
            content, _ = self.read_log_file(log_file)
            if not content:
                continue
            
            # 统计错误数量
            error_count = self.count_errors_in_content(content)
            if error_count > 0:
                error_counts[log_file] = error_count
                self.logger.info(f"文件 {log_file} 中发现 {error_count} 个错误")
        
        return dict(error_counts)
    
    def should_send_notification(self) -> bool:
        """判断是否应该发送通知"""
        current_time = datetime.now()
        
        # 检查冷却时间
        cooldown_minutes = self.config['notification']['cooldown_minutes']
        if self.notification_history:
            last_notification = self.notification_history[-1]
            if current_time - last_notification < timedelta(minutes=cooldown_minutes):
                return False
        
        # 检查每小时最大通知次数
        max_per_hour = self.config['notification']['max_notifications_per_hour']
        one_hour_ago = current_time - timedelta(hours=1)
        recent_notifications = [t for t in self.notification_history if t > one_hour_ago]
        if len(recent_notifications) >= max_per_hour:
            return False
        
        return True
    
    def get_system_info(self) -> str:
        """获取系统信息"""
        try:
            info = []
            info.append(f"系统: {platform.system()} {platform.release()}")
            info.append(f"CPU使用率: {psutil.cpu_percent(interval=1)}%")
            info.append(f"内存使用率: {psutil.virtual_memory().percent}%")
            info.append(f"磁盘使用率: {psutil.disk_usage('/').percent}%")
            
            # 获取运行时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            info.append(f"系统运行时间: {uptime}")
            
            return "\n".join(info)
        except Exception as e:
            return f"获取系统信息失败: {e}"
    
    def create_email_content(self, error_counts: Dict[str, int]) -> str:
        """创建邮件内容"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""
系统错误监控报告
================

时间: {current_time}

错误统计:
"""
        
        total_errors = sum(error_counts.values())
        content += f"总错误数量: {total_errors}\n"
        content += f"错误阈值: {self.config['monitor']['error_threshold']}\n"
        content += f"时间窗口: {self.config['monitor']['time_window_minutes']} 分钟\n\n"
        
        for log_file, count in error_counts.items():
            content += f"文件: {log_file}\n"
            content += f"错误数量: {count}\n\n"
        
        if self.config['notification']['include_system_info']:
            content += "系统信息:\n"
            content += "=" * 20 + "\n"
            content += self.get_system_info() + "\n\n"
        
        content += "请及时检查系统状态并处理相关问题。\n"
        content += "\n此邮件由错误监控系统自动发送。"
        
        return content
    
    def send_email(self, error_counts: Dict[str, int]) -> bool:
        """发送邮件通知"""
        try:
            if not self.should_send_notification():
                self.logger.info("跳过邮件发送（冷却时间或频率限制）")
                return False
            
            email_config = self.config['email']
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"{email_config['subject_prefix']} 系统错误数量超过阈值"
            
            # 添加邮件内容
            body = self.create_email_content(error_counts)
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['from_email'], email_config['to_emails'], text)
            server.quit()
            
            # 记录通知时间
            self.notification_history.append(datetime.now())
            
            self.logger.info(f"邮件发送成功，收件人: {email_config['to_emails']}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """运行一次监控周期"""
        self.logger.info("开始监控周期...")
        
        # 检查日志文件
        error_counts = self.check_log_files()
        
        if not error_counts:
            self.logger.info("未发现错误日志")
            return
        
        # 计算总错误数
        total_errors = sum(error_counts.values())
        threshold = self.config['monitor']['error_threshold']
        
        self.logger.info(f"总错误数: {total_errors}, 阈值: {threshold}")
        
        # 如果超过阈值，发送邮件
        if total_errors >= threshold:
            self.logger.warning(f"错误数量超过阈值！总错误数: {total_errors}")
            self.send_email(error_counts)
        else:
            self.logger.info("错误数量未超过阈值")
    
    def run(self):
        """运行监控服务"""
        self.logger.info("错误日志监控服务启动")
        self.logger.info(f"监控文件: {self.config['monitor']['log_file_paths']}")
        self.logger.info(f"错误阈值: {self.config['monitor']['error_threshold']}")
        self.logger.info(f"检查间隔: {self.config['monitor']['check_interval_seconds']} 秒")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.config['monitor']['check_interval_seconds'])
        except KeyboardInterrupt:
            self.logger.info("监控服务停止")
        except Exception as e:
            self.logger.error(f"监控服务异常: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='错误日志监控系统')
    parser.add_argument('--config', default='error_monitor_config.json', 
                       help='配置文件路径')
    parser.add_argument('--test', action='store_true', 
                       help='测试模式，只运行一次检查')
    
    args = parser.parse_args()
    
    monitor = ErrorLogMonitor(args.config)
    
    if args.test:
        print("运行测试模式...")
        monitor.run_monitoring_cycle()
    else:
        monitor.run()


if __name__ == "__main__":
    main()