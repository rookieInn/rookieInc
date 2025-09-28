#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件通知工具
用于发送系统错误通知邮件
"""

import smtplib
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
import os


class EmailNotifier:
    def __init__(self, config_file: str = "error_monitor_config.json"):
        """初始化邮件通知器"""
        self.config = self.load_config(config_file)
        self.setup_logging()
    
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 不存在")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {}
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_html_email(self, subject: str, content: str, error_details: Optional[Dict] = None) -> str:
        """创建HTML格式的邮件内容"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .error-details {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .error-item {{ margin: 10px 0; padding: 10px; background-color: #fff; border-left: 4px solid #f44336; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 系统错误监控警报</h2>
            </div>
            
            <div class="content">
                <h3>{subject}</h3>
                <p>{content}</p>
                
                {self._format_error_details_html(error_details) if error_details else ''}
            </div>
            
            <div class="footer">
                <p>此邮件由系统错误监控服务自动发送</p>
                <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def _format_error_details_html(self, error_details: Dict) -> str:
        """格式化错误详情为HTML"""
        if not error_details:
            return ""
        
        html = "<div class='error-details'><h4>错误详情:</h4>"
        
        for log_file, errors in error_details.items():
            html += f"<div class='error-item'>"
            html += f"<strong>文件:</strong> {log_file}<br>"
            html += f"<strong>错误数量:</strong> {errors['count']}<br>"
            
            if 'sample_errors' in errors and errors['sample_errors']:
                html += "<strong>错误示例:</strong><br>"
                html += "<ul>"
                for error in errors['sample_errors'][:5]:  # 只显示前5个错误
                    html += f"<li>{error}</li>"
                html += "</ul>"
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def send_email(self, 
                   subject: str, 
                   content: str, 
                   to_emails: List[str], 
                   error_details: Optional[Dict] = None,
                   attachments: Optional[List[str]] = None) -> bool:
        """发送邮件"""
        try:
            email_config = self.config.get('email', {})
            
            if not email_config:
                self.logger.error("邮件配置未找到")
                return False
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = email_config.get('from_email', '')
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"{email_config.get('subject_prefix', '[系统监控]')} {subject}"
            
            # 创建纯文本版本
            text_content = content
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 创建HTML版本
            html_content = self.create_html_email(subject, content, error_details)
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 添加附件
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(attachment_path)}'
                            )
                            msg.attach(part)
            
            # 发送邮件
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['from_email'], to_emails, text)
            server.quit()
            
            self.logger.info(f"邮件发送成功，收件人: {to_emails}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return False
    
    def send_error_notification(self, error_counts: Dict[str, int], 
                               sample_errors: Optional[Dict[str, List[str]]] = None) -> bool:
        """发送错误通知邮件"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_errors = sum(error_counts.values())
        
        subject = f"系统错误数量超过阈值 (总计: {total_errors})"
        content = f"""
系统在 {current_time} 检测到错误数量超过预设阈值。

错误统计:
- 总错误数量: {total_errors}
- 错误阈值: {self.config.get('monitor', {}).get('error_threshold', 10)}
- 时间窗口: {self.config.get('monitor', {}).get('time_window_minutes', 5)} 分钟

各文件错误统计:
"""
        
        for log_file, count in error_counts.items():
            content += f"- {log_file}: {count} 个错误\n"
        
        content += "\n请及时检查系统状态并处理相关问题。"
        
        # 准备错误详情
        error_details = {}
        for log_file, count in error_counts.items():
            error_details[log_file] = {
                'count': count,
                'sample_errors': sample_errors.get(log_file, []) if sample_errors else []
            }
        
        # 获取收件人列表
        to_emails = self.config.get('email', {}).get('to_emails', [])
        if not to_emails:
            self.logger.error("未配置收件人邮箱")
            return False
        
        return self.send_email(subject, content, to_emails, error_details)
    
    def send_test_email(self) -> bool:
        """发送测试邮件"""
        subject = "错误监控系统测试邮件"
        content = """
这是一封测试邮件，用于验证错误监控系统的邮件发送功能。

如果您收到这封邮件，说明邮件配置正确，系统可以正常发送通知。

测试时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        to_emails = self.config.get('email', {}).get('to_emails', [])
        if not to_emails:
            print("未配置收件人邮箱")
            return False
        
        return self.send_email(subject, content, to_emails)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='邮件通知工具')
    parser.add_argument('--config', default='error_monitor_config.json', 
                       help='配置文件路径')
    parser.add_argument('--test', action='store_true', 
                       help='发送测试邮件')
    parser.add_argument('--subject', default='测试邮件', 
                       help='邮件主题')
    parser.add_argument('--content', default='这是一封测试邮件', 
                       help='邮件内容')
    parser.add_argument('--to', nargs='+', 
                       help='收件人邮箱地址')
    
    args = parser.parse_args()
    
    notifier = EmailNotifier(args.config)
    
    if args.test:
        print("发送测试邮件...")
        success = notifier.send_test_email()
        if success:
            print("测试邮件发送成功")
        else:
            print("测试邮件发送失败")
    else:
        to_emails = args.to or notifier.config.get('email', {}).get('to_emails', [])
        if not to_emails:
            print("请指定收件人邮箱地址")
            return
        
        success = notifier.send_email(args.subject, args.content, to_emails)
        if success:
            print("邮件发送成功")
        else:
            print("邮件发送失败")


if __name__ == "__main__":
    main()