#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享返佣裂变系统
Referral Commission Fission System

功能特性：
1. 用户注册和邀请码生成
2. 分享链接生成和追踪
3. 多级返佣计算
4. 裂变数据统计
5. 返佣结算管理
"""

import hashlib
import uuid
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommissionType(Enum):
    """返佣类型"""
    DIRECT = "direct"      # 直接推荐
    INDIRECT = "indirect"  # 间接推荐
    BONUS = "bonus"        # 奖励返佣

@dataclass
class User:
    """用户信息"""
    user_id: str
    username: str
    email: str
    phone: str
    invite_code: str
    referrer_id: Optional[str] = None
    level: int = 1
    total_commission: float = 0.0
    created_at: datetime = None
    is_active: bool = True

@dataclass
class ReferralLink:
    """分享链接信息"""
    link_id: str
    user_id: str
    original_url: str
    short_code: str
    click_count: int = 0
    conversion_count: int = 0
    created_at: datetime = None
    expires_at: Optional[datetime] = None

@dataclass
class Commission:
    """返佣记录"""
    commission_id: str
    user_id: str
    referrer_id: str
    amount: float
    commission_type: CommissionType
    order_id: str
    status: str = "pending"  # pending, confirmed, paid
    created_at: datetime = None

class ReferralSystem:
    """返佣裂变系统核心类"""
    
    def __init__(self, db_path: str = "referral_system.db"):
        self.db_path = db_path
        self.commission_rates = {
            1: 0.10,  # 一级返佣 10%
            2: 0.05,  # 二级返佣 5%
            3: 0.02   # 三级返佣 2%
        }
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                invite_code TEXT UNIQUE NOT NULL,
                referrer_id TEXT,
                level INTEGER DEFAULT 1,
                total_commission REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id)
            )
        ''')
        
        # 分享链接表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referral_links (
                link_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                click_count INTEGER DEFAULT 0,
                conversion_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 返佣记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commissions (
                commission_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                referrer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                commission_type TEXT NOT NULL,
                order_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (referrer_id) REFERENCES users (user_id)
            )
        ''')
        
        # 点击记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_records (
                record_id TEXT PRIMARY KEY,
                link_id TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                converted BOOLEAN DEFAULT 0,
                FOREIGN KEY (link_id) REFERENCES referral_links (link_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def generate_invite_code(self, user_id: str) -> str:
        """生成邀请码"""
        timestamp = str(int(time.time()))
        raw_code = f"{user_id}_{timestamp}"
        invite_code = hashlib.md5(raw_code.encode()).hexdigest()[:8].upper()
        return invite_code
    
    def register_user(self, username: str, email: str, phone: str, 
                     referrer_code: Optional[str] = None) -> User:
        """用户注册"""
        user_id = str(uuid.uuid4())
        invite_code = self.generate_invite_code(user_id)
        
        # 查找推荐人
        referrer_id = None
        level = 1
        if referrer_code:
            referrer_id = self.get_user_by_invite_code(referrer_code)
            if referrer_id:
                level = self.get_user_level(referrer_id) + 1
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            phone=phone,
            invite_code=invite_code,
            referrer_id=referrer_id,
            level=level,
            created_at=datetime.now()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, email, phone, invite_code, referrer_id, level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user.user_id, user.username, user.email, user.phone, 
              user.invite_code, user.referrer_id, user.level))
        conn.commit()
        conn.close()
        
        logger.info(f"用户注册成功: {username} (ID: {user_id})")
        return user
    
    def get_user_by_invite_code(self, invite_code: str) -> Optional[str]:
        """通过邀请码获取用户ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE invite_code = ?', (invite_code,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_user_level(self, user_id: str) -> int:
        """获取用户层级"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT level FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 1
    
    def create_referral_link(self, user_id: str, original_url: str, 
                           expires_days: int = 30) -> ReferralLink:
        """创建分享链接"""
        link_id = str(uuid.uuid4())
        short_code = self.generate_short_code()
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        link = ReferralLink(
            link_id=link_id,
            user_id=user_id,
            original_url=original_url,
            short_code=short_code,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO referral_links (link_id, user_id, original_url, short_code, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (link.link_id, link.user_id, link.original_url, 
              link.short_code, link.expires_at))
        conn.commit()
        conn.close()
        
        logger.info(f"分享链接创建成功: {short_code}")
        return link
    
    def generate_short_code(self) -> str:
        """生成短链接代码"""
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:6]
    
    def track_click(self, short_code: str, ip_address: str = None, 
                   user_agent: str = None) -> Optional[str]:
        """追踪链接点击"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取链接信息
        cursor.execute('''
            SELECT link_id, original_url, expires_at FROM referral_links 
            WHERE short_code = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (short_code, datetime.now()))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        link_id, original_url, expires_at = result
        
        # 记录点击
        record_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO click_records (record_id, link_id, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (record_id, link_id, ip_address, user_agent))
        
        # 更新点击计数
        cursor.execute('''
            UPDATE referral_links SET click_count = click_count + 1 
            WHERE link_id = ?
        ''', (link_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"链接点击追踪: {short_code}")
        return original_url
    
    def process_conversion(self, user_id: str, order_id: str, amount: float) -> List[Commission]:
        """处理转化和返佣计算"""
        commissions = []
        
        # 获取用户层级关系
        referrers = self.get_referrer_chain(user_id)
        
        for level, referrer_id in enumerate(referrers, 1):
            if level > 3:  # 最多3级返佣
                break
            
            commission_rate = self.commission_rates.get(level, 0)
            commission_amount = amount * commission_rate
            
            if commission_amount > 0:
                commission = Commission(
                    commission_id=str(uuid.uuid4()),
                    user_id=user_id,
                    referrer_id=referrer_id,
                    amount=commission_amount,
                    commission_type=CommissionType.DIRECT if level == 1 else CommissionType.INDIRECT,
                    order_id=order_id,
                    created_at=datetime.now()
                )
                
                # 保存返佣记录
                self.save_commission(commission)
                commissions.append(commission)
                
                # 更新用户总返佣
                self.update_user_commission(referrer_id, commission_amount)
        
        # 更新转化计数
        self.update_conversion_count(user_id)
        
        logger.info(f"转化处理完成: 用户 {user_id}, 订单 {order_id}, 金额 {amount}")
        return commissions
    
    def get_referrer_chain(self, user_id: str) -> List[str]:
        """获取推荐人链条"""
        referrers = []
        current_user = user_id
        
        while current_user:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT referrer_id FROM users WHERE user_id = ?', (current_user,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                referrers.append(result[0])
                current_user = result[0]
            else:
                break
        
        return referrers
    
    def save_commission(self, commission: Commission):
        """保存返佣记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO commissions (commission_id, user_id, referrer_id, amount, 
                                   commission_type, order_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (commission.commission_id, commission.user_id, commission.referrer_id,
              commission.amount, commission.commission_type.value, commission.order_id,
              commission.status, commission.created_at))
        conn.commit()
        conn.close()
    
    def update_user_commission(self, user_id: str, amount: float):
        """更新用户总返佣"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET total_commission = total_commission + ? 
            WHERE user_id = ?
        ''', (amount, user_id))
        conn.commit()
        conn.close()
    
    def update_conversion_count(self, user_id: str):
        """更新转化计数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE referral_links SET conversion_count = conversion_count + 1 
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id: str) -> Dict:
        """获取用户统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户基本信息
        cursor.execute('''
            SELECT username, total_commission, level, created_at 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        user_info = cursor.fetchone()
        
        # 分享链接统计
        cursor.execute('''
            SELECT COUNT(*), SUM(click_count), SUM(conversion_count)
            FROM referral_links WHERE user_id = ?
        ''', (user_id,))
        link_stats = cursor.fetchone()
        
        # 返佣统计
        cursor.execute('''
            SELECT COUNT(*), SUM(amount)
            FROM commissions WHERE referrer_id = ? AND status = 'confirmed'
        ''', (user_id,))
        commission_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "user_info": {
                "username": user_info[0],
                "total_commission": user_info[1],
                "level": user_info[2],
                "created_at": user_info[3]
            },
            "link_stats": {
                "total_links": link_stats[0] or 0,
                "total_clicks": link_stats[1] or 0,
                "total_conversions": link_stats[2] or 0
            },
            "commission_stats": {
                "total_commissions": commission_stats[0] or 0,
                "total_amount": commission_stats[1] or 0
            }
        }
    
    def get_system_analytics(self) -> Dict:
        """获取系统分析数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户统计
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE created_at >= date("now", "-30 days")')
        new_users_30d = cursor.fetchone()[0]
        
        # 链接统计
        cursor.execute('SELECT COUNT(*) FROM referral_links')
        total_links = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(click_count) FROM referral_links')
        total_clicks = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(conversion_count) FROM referral_links')
        total_conversions = cursor.fetchone()[0] or 0
        
        # 返佣统计
        cursor.execute('SELECT SUM(amount) FROM commissions WHERE status = "confirmed"')
        total_commissions = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "users": {
                "total": total_users,
                "new_30d": new_users_30d
            },
            "links": {
                "total": total_links,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "conversion_rate": total_conversions / total_clicks if total_clicks > 0 else 0
            },
            "commissions": {
                "total_amount": total_commissions
            }
        }

def main():
    """主函数 - 演示系统使用"""
    # 初始化系统
    system = ReferralSystem()
    
    print("=== 分享返佣裂变系统演示 ===\n")
    
    # 1. 注册用户
    print("1. 用户注册")
    user1 = system.register_user("张三", "zhangsan@example.com", "13800138000")
    print(f"用户注册成功: {user1.username}, 邀请码: {user1.invite_code}")
    
    user2 = system.register_user("李四", "lisi@example.com", "13800138001", user1.invite_code)
    print(f"用户注册成功: {user2.username}, 邀请码: {user2.invite_code}")
    
    user3 = system.register_user("王五", "wangwu@example.com", "13800138002", user2.invite_code)
    print(f"用户注册成功: {user3.username}, 邀请码: {user3.invite_code}")
    
    # 2. 创建分享链接
    print("\n2. 创建分享链接")
    link1 = system.create_referral_link(user1.user_id, "https://example.com/product/123")
    print(f"分享链接创建: {link1.short_code}")
    
    # 3. 模拟点击和转化
    print("\n3. 模拟点击和转化")
    original_url = system.track_click(link1.short_code, "192.168.1.1", "Mozilla/5.0")
    print(f"链接点击追踪: {original_url}")
    
    # 4. 处理转化
    print("\n4. 处理转化和返佣")
    commissions = system.process_conversion(user3.user_id, "ORDER_001", 1000.0)
    for comm in commissions:
        print(f"返佣记录: {comm.referrer_id} -> {comm.amount:.2f}元 ({comm.commission_type.value})")
    
    # 5. 查看统计信息
    print("\n5. 用户统计信息")
    stats = system.get_user_stats(user1.user_id)
    print(f"用户 {stats['user_info']['username']} 统计:")
    print(f"  总返佣: {stats['user_info']['total_commission']:.2f}元")
    print(f"  分享链接: {stats['link_stats']['total_links']}个")
    print(f"  总点击: {stats['link_stats']['total_clicks']}次")
    print(f"  总转化: {stats['link_stats']['total_conversions']}次")
    
    # 6. 系统分析
    print("\n6. 系统分析")
    analytics = system.get_system_analytics()
    print(f"总用户数: {analytics['users']['total']}")
    print(f"30天新用户: {analytics['users']['new_30d']}")
    print(f"总点击量: {analytics['links']['total_clicks']}")
    print(f"总转化量: {analytics['links']['total_conversions']}")
    print(f"转化率: {analytics['links']['conversion_rate']:.2%}")
    print(f"总返佣金额: {analytics['commissions']['total_amount']:.2f}元")

if __name__ == "__main__":
    main()