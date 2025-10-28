"""
订单状态变更通知系统
"""
import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from order_models import Order, OrderStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationConfig:
    """通知配置"""
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 smtp_username: str = None, smtp_password: str = None,
                 from_email: str = None, webhook_url: str = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.webhook_url = webhook_url

class OrderNotificationManager:
    """订单通知管理器"""
    
    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        self.notification_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载通知模板"""
        return {
            'order_created': {
                'subject': '订单创建成功 - {order_id}',
                'body': '''
                尊敬的客户，您好！
                
                您的订单已成功创建：
                订单号：{order_id}
                金额：¥{amount}
                状态：{status}
                创建时间：{created_at}
                过期时间：{expires_at}
                
                请在30分钟内完成支付，否则订单将自动关闭。
                
                感谢您的购买！
                '''
            },
            'order_confirmed': {
                'subject': '订单确认 - {order_id}',
                'body': '''
                尊敬的客户，您好！
                
                您的订单已确认：
                订单号：{order_id}
                金额：¥{amount}
                状态：{status}
                确认时间：{updated_at}
                
                我们将尽快为您处理订单。
                
                感谢您的购买！
                '''
            },
            'order_cancelled': {
                'subject': '订单取消 - {order_id}',
                'body': '''
                尊敬的客户，您好！
                
                您的订单已取消：
                订单号：{order_id}
                金额：¥{amount}
                状态：{status}
                取消时间：{updated_at}
                取消原因：{reason}
                
                如有疑问，请联系客服。
                '''
            },
            'order_expired': {
                'subject': '订单超时关闭 - {order_id}',
                'body': '''
                尊敬的客户，您好！
                
                很抱歉，您的订单因超时未支付已自动关闭：
                订单号：{order_id}
                金额：¥{amount}
                状态：{status}
                关闭时间：{updated_at}
                
                您可以重新下单购买。
                
                感谢您的理解！
                '''
            },
            'order_completed': {
                'subject': '订单完成 - {order_id}',
                'body': '''
                尊敬的客户，您好！
                
                您的订单已完成：
                订单号：{order_id}
                金额：¥{amount}
                状态：{status}
                完成时间：{updated_at}
                
                感谢您的购买，期待再次为您服务！
                '''
            }
        }
    
    def send_email_notification(self, to_email: str, template_key: str, 
                              order: Order, extra_data: Dict = None) -> bool:
        """发送邮件通知"""
        if not self.config.smtp_server or not self.config.from_email:
            logger.warning("邮件配置不完整，跳过邮件通知")
            return False
        
        try:
            template = self.notification_templates.get(template_key)
            if not template:
                logger.error(f"未找到通知模板: {template_key}")
                return False
            
            # 准备模板数据
            template_data = {
                'order_id': order.order_id,
                'amount': order.amount,
                'status': order.status.value,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'expires_at': order.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'reason': extra_data.get('reason', '') if extra_data else ''
            }
            
            # 格式化模板
            subject = template['subject'].format(**template_data)
            body = template['body'].format(**template_data)
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件通知发送成功: {to_email} - {template_key}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件通知失败: {e}")
            return False
    
    def send_webhook_notification(self, template_key: str, order: Order, 
                                extra_data: Dict = None) -> bool:
        """发送Webhook通知"""
        if not self.config.webhook_url:
            logger.warning("Webhook URL未配置，跳过Webhook通知")
            return False
        
        try:
            import requests
            
            # 准备通知数据
            notification_data = {
                'event_type': template_key,
                'order': order.to_dict(),
                'timestamp': datetime.now().isoformat(),
                'extra_data': extra_data or {}
            }
            
            # 发送Webhook
            response = requests.post(
                self.config.webhook_url,
                json=notification_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook通知发送成功: {template_key}")
                return True
            else:
                logger.error(f"Webhook通知失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送Webhook通知失败: {e}")
            return False
    
    def send_notification(self, template_key: str, order: Order, 
                         to_email: str = None, extra_data: Dict = None) -> bool:
        """发送通知（邮件 + Webhook）"""
        success = True
        
        # 发送邮件通知
        if to_email:
            email_success = self.send_email_notification(to_email, template_key, order, extra_data)
            success = success and email_success
        
        # 发送Webhook通知
        webhook_success = self.send_webhook_notification(template_key, order, extra_data)
        success = success and webhook_success
        
        return success
    
    def notify_order_created(self, order: Order, customer_email: str = None) -> bool:
        """通知订单创建"""
        return self.send_notification('order_created', order, customer_email)
    
    def notify_order_confirmed(self, order: Order, customer_email: str = None) -> bool:
        """通知订单确认"""
        return self.send_notification('order_confirmed', order, customer_email)
    
    def notify_order_cancelled(self, order: Order, customer_email: str = None, 
                              reason: str = '') -> bool:
        """通知订单取消"""
        extra_data = {'reason': reason}
        return self.send_notification('order_cancelled', order, customer_email, extra_data)
    
    def notify_order_expired(self, order: Order, customer_email: str = None) -> bool:
        """通知订单过期"""
        return self.send_notification('order_expired', order, customer_email)
    
    def notify_order_completed(self, order: Order, customer_email: str = None) -> bool:
        """通知订单完成"""
        return self.send_notification('order_completed', order, customer_email)

class OrderNotificationService:
    """订单通知服务（集成到订单管理器中）"""
    
    def __init__(self, order_manager, notification_config: NotificationConfig = None):
        self.order_manager = order_manager
        self.notification_manager = OrderNotificationManager(notification_config)
    
    def create_order_with_notification(self, user_id: str, amount: float, 
                                     items: List[Dict] = None, 
                                     customer_info: Dict = None,
                                     expiry_minutes: int = 30) -> Order:
        """创建订单并发送通知"""
        # 创建订单
        order = self.order_manager.create_order(
            user_id=user_id,
            amount=amount,
            items=items,
            customer_info=customer_info,
            expiry_minutes=expiry_minutes
        )
        
        # 发送创建通知
        customer_email = customer_info.get('email') if customer_info else None
        self.notification_manager.notify_order_created(order, customer_email)
        
        return order
    
    def update_order_status_with_notification(self, order_id: str, new_status: OrderStatus, 
                                            message: str = "", customer_email: str = None) -> bool:
        """更新订单状态并发送通知"""
        # 更新状态
        success = self.order_manager.update_order_status(order_id, new_status, message)
        
        if success:
            # 获取更新后的订单
            order = self.order_manager.get_order(order_id)
            if order:
                # 根据状态发送相应通知
                if new_status == OrderStatus.CONFIRMED:
                    self.notification_manager.notify_order_confirmed(order, customer_email)
                elif new_status == OrderStatus.CANCELLED:
                    self.notification_manager.notify_order_cancelled(order, customer_email, message)
                elif new_status == OrderStatus.EXPIRED:
                    self.notification_manager.notify_order_expired(order, customer_email)
                elif new_status == OrderStatus.COMPLETED:
                    self.notification_manager.notify_order_completed(order, customer_email)
        
        return success

# 示例配置
def create_notification_config():
    """创建通知配置示例"""
    return NotificationConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-app-password",
        from_email="your-email@gmail.com",
        webhook_url="https://your-webhook-url.com/order-notifications"
    )