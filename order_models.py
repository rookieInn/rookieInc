"""
订单数据模型和数据库操作
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import threading
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待处理
    CONFIRMED = "confirmed"  # 已确认
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"      # 已过期

class Order:
    """订单类"""
    
    def __init__(self, order_id: str = None, user_id: str = None, 
                 amount: float = 0.0, status: OrderStatus = OrderStatus.PENDING,
                 created_at: datetime = None, updated_at: datetime = None,
                 expires_at: datetime = None, items: List[Dict] = None,
                 customer_info: Dict = None):
        self.order_id = order_id
        self.user_id = user_id
        self.amount = amount
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.expires_at = expires_at or (self.created_at + timedelta(minutes=30))
        self.items = items or []
        self.customer_info = customer_info or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'items': self.items,
            'customer_info': self.customer_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        """从字典创建订单对象"""
        return cls(
            order_id=data.get('order_id'),
            user_id=data.get('user_id'),
            amount=data.get('amount', 0.0),
            status=OrderStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat())),
            expires_at=datetime.fromisoformat(data.get('expires_at', (datetime.now() + timedelta(minutes=30)).isoformat())),
            items=data.get('items', []),
            customer_info=data.get('customer_info', {})
        )

class OrderManager:
    """订单管理器"""
    
    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        self.start_expiry_checker()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    items TEXT NOT NULL,
                    customer_info TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS order_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_status TEXT,
                    new_status TEXT,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id)
                )
            ''')
            
            conn.commit()
    
    def create_order(self, user_id: str, amount: float, items: List[Dict] = None, 
                    customer_info: Dict = None, expiry_minutes: int = 30) -> Order:
        """创建新订单"""
        with self.lock:
            order_id = f"ORD_{int(time.time() * 1000)}"
            expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
            
            order = Order(
                order_id=order_id,
                user_id=user_id,
                amount=amount,
                status=OrderStatus.PENDING,
                expires_at=expires_at,
                items=items or [],
                customer_info=customer_info or {}
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO orders (order_id, user_id, amount, status, created_at, 
                                      updated_at, expires_at, items, customer_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order.order_id, order.user_id, order.amount, order.status.value,
                    order.created_at.isoformat(), order.updated_at.isoformat(),
                    order.expires_at.isoformat(), json.dumps(order.items),
                    json.dumps(order.customer_info)
                ))
                conn.commit()
            
            self._log_order_action(order.order_id, "CREATE", None, order.status.value, "订单创建")
            logger.info(f"订单创建成功: {order.order_id}")
            return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT order_id, user_id, amount, status, created_at, updated_at,
                       expires_at, items, customer_info
                FROM orders WHERE order_id = ?
            ''', (order_id,))
            
            row = cursor.fetchone()
            if row:
                return Order(
                    order_id=row[0],
                    user_id=row[1],
                    amount=row[2],
                    status=OrderStatus(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    updated_at=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]),
                    items=json.loads(row[7]),
                    customer_info=json.loads(row[8])
                )
            return None
    
    def update_order_status(self, order_id: str, new_status: OrderStatus, 
                          message: str = "") -> bool:
        """更新订单状态"""
        with self.lock:
            order = self.get_order(order_id)
            if not order:
                return False
            
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE orders SET status = ?, updated_at = ?
                    WHERE order_id = ?
                ''', (new_status.value, order.updated_at.isoformat(), order_id))
                conn.commit()
            
            self._log_order_action(order_id, "STATUS_UPDATE", old_status.value, 
                                 new_status.value, message)
            logger.info(f"订单状态更新: {order_id} {old_status.value} -> {new_status.value}")
            return True
    
    def get_expired_orders(self) -> List[Order]:
        """获取已过期的订单"""
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT order_id, user_id, amount, status, created_at, updated_at,
                       expires_at, items, customer_info
                FROM orders 
                WHERE status IN (?, ?) AND expires_at < ?
            ''', (OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value, now.isoformat()))
            
            orders = []
            for row in cursor.fetchall():
                orders.append(Order(
                    order_id=row[0],
                    user_id=row[1],
                    amount=row[2],
                    status=OrderStatus(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    updated_at=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]),
                    items=json.loads(row[7]),
                    customer_info=json.loads(row[8])
                ))
            return orders
    
    def _log_order_action(self, order_id: str, action: str, old_status: str, 
                         new_status: str, message: str):
        """记录订单操作日志"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO order_logs (order_id, action, old_status, new_status, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_id, action, old_status, new_status, message, datetime.now().isoformat()))
            conn.commit()
    
    def start_expiry_checker(self):
        """启动过期检查器"""
        def check_expired_orders():
            while True:
                try:
                    expired_orders = self.get_expired_orders()
                    for order in expired_orders:
                        if order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                            self.update_order_status(order.order_id, OrderStatus.EXPIRED, 
                                                   "订单超时自动关闭")
                            logger.info(f"订单自动关闭: {order.order_id}")
                    
                    # 每30秒检查一次
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"检查过期订单时出错: {e}")
                    time.sleep(60)
        
        # 在后台线程中运行
        thread = threading.Thread(target=check_expired_orders, daemon=True)
        thread.start()
        logger.info("订单过期检查器已启动")
    
    def get_orders_by_user(self, user_id: str) -> List[Order]:
        """获取用户的所有订单"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT order_id, user_id, amount, status, created_at, updated_at,
                       expires_at, items, customer_info
                FROM orders WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            
            orders = []
            for row in cursor.fetchall():
                orders.append(Order(
                    order_id=row[0],
                    user_id=row[1],
                    amount=row[2],
                    status=OrderStatus(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    updated_at=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]),
                    items=json.loads(row[7]),
                    customer_info=json.loads(row[8])
                ))
            return orders
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """获取订单统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总订单数
            cursor = conn.execute('SELECT COUNT(*) FROM orders')
            total_orders = cursor.fetchone()[0]
            
            # 各状态订单数
            cursor = conn.execute('''
                SELECT status, COUNT(*) FROM orders GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # 今日订单数
            today = datetime.now().date().isoformat()
            cursor = conn.execute('''
                SELECT COUNT(*) FROM orders WHERE DATE(created_at) = ?
            ''', (today,))
            today_orders = cursor.fetchone()[0]
            
            # 总收入
            cursor = conn.execute('''
                SELECT SUM(amount) FROM orders WHERE status = ?
            ''', (OrderStatus.COMPLETED.value,))
            total_revenue = cursor.fetchone()[0] or 0
            
            return {
                'total_orders': total_orders,
                'status_counts': status_counts,
                'today_orders': today_orders,
                'total_revenue': total_revenue
            }