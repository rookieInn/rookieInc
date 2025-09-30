#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分账程序 - 方便实用的分账工具
支持多种分账方式：平均分账、按比例分账、自定义分账
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os
from typing import List, Dict, Any

app = Flask(__name__)
app.secret_key = 'split_bill_secret_key_2024'

# 数据库初始化
def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('split_bills.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建账单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            total_amount REAL NOT NULL,
            description TEXT,
            split_type TEXT NOT NULL,  -- 'equal', 'proportional', 'custom'
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # 创建分账记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_splits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            is_paid BOOLEAN DEFAULT FALSE,
            paid_at TIMESTAMP,
            FOREIGN KEY (bill_id) REFERENCES bills (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class SplitBillManager:
    """分账管理器"""
    
    def __init__(self):
        self.db_path = 'split_bills.db'
    
    def add_user(self, name: str, email: str = '', phone: str = '') -> int:
        """添加用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None  # 用户名已存在
        finally:
            conn.close()
    
    def get_users(self) -> List[Dict]:
        """获取所有用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, phone FROM users ORDER BY name')
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3]
            })
        conn.close()
        return users
    
    def create_bill(self, title: str, total_amount: float, description: str, 
                   split_type: str, user_ids: List[int], custom_amounts: Dict[int, float] = None) -> int:
        """创建账单"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 创建账单
            cursor.execute(
                'INSERT INTO bills (title, total_amount, description, split_type, created_by) VALUES (?, ?, ?, ?, ?)',
                (title, total_amount, description, split_type, user_ids[0] if user_ids else None)
            )
            bill_id = cursor.lastrowid
            
            # 计算分账金额
            if split_type == 'equal':
                amount_per_person = total_amount / len(user_ids)
                for user_id in user_ids:
                    cursor.execute(
                        'INSERT INTO bill_splits (bill_id, user_id, amount) VALUES (?, ?, ?)',
                        (bill_id, user_id, amount_per_person)
                    )
            
            elif split_type == 'proportional':
                # 这里简化处理，实际应该根据用户指定的比例
                amount_per_person = total_amount / len(user_ids)
                for user_id in user_ids:
                    cursor.execute(
                        'INSERT INTO bill_splits (bill_id, user_id, amount) VALUES (?, ?, ?)',
                        (bill_id, user_id, amount_per_person)
                    )
            
            elif split_type == 'custom' and custom_amounts:
                for user_id, amount in custom_amounts.items():
                    cursor.execute(
                        'INSERT INTO bill_splits (bill_id, user_id, amount) VALUES (?, ?, ?)',
                        (bill_id, user_id, amount)
                    )
            
            conn.commit()
            return bill_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_bills(self) -> List[Dict]:
        """获取所有账单"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.id, b.title, b.total_amount, b.description, b.split_type, 
                   b.created_at, u.name as created_by_name
            FROM bills b
            LEFT JOIN users u ON b.created_by = u.id
            ORDER BY b.created_at DESC
        ''')
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row[0],
                'title': row[1],
                'total_amount': row[2],
                'description': row[3],
                'split_type': row[4],
                'created_at': row[5],
                'created_by_name': row[6]
            })
        conn.close()
        return bills
    
    def get_bill_details(self, bill_id: int) -> Dict:
        """获取账单详情"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取账单基本信息
        cursor.execute('''
            SELECT b.id, b.title, b.total_amount, b.description, b.split_type, 
                   b.created_at, u.name as created_by_name
            FROM bills b
            LEFT JOIN users u ON b.created_by = u.id
            WHERE b.id = ?
        ''', (bill_id,))
        
        bill_row = cursor.fetchone()
        if not bill_row:
            return None
        
        bill = {
            'id': bill_row[0],
            'title': bill_row[1],
            'total_amount': bill_row[2],
            'description': bill_row[3],
            'split_type': bill_row[4],
            'created_at': bill_row[5],
            'created_by_name': bill_row[6]
        }
        
        # 获取分账详情
        cursor.execute('''
            SELECT bs.user_id, u.name, bs.amount, bs.is_paid, bs.paid_at
            FROM bill_splits bs
            JOIN users u ON bs.user_id = u.id
            WHERE bs.bill_id = ?
            ORDER BY u.name
        ''', (bill_id,))
        
        splits = []
        for row in cursor.fetchall():
            splits.append({
                'user_id': row[0],
                'user_name': row[1],
                'amount': row[2],
                'is_paid': bool(row[3]),
                'paid_at': row[4]
            })
        
        bill['splits'] = splits
        conn.close()
        return bill
    
    def mark_paid(self, bill_id: int, user_id: int) -> bool:
        """标记为已支付"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE bill_splits 
                SET is_paid = TRUE, paid_at = CURRENT_TIMESTAMP
                WHERE bill_id = ? AND user_id = ?
            ''', (bill_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

# 初始化管理器
manager = SplitBillManager()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/users')
def users_page():
    """用户管理页面"""
    users = manager.get_users()
    return render_template('users.html', users=users)

@app.route('/bills')
def bills_page():
    """账单列表页面"""
    bills = manager.get_bills()
    return render_template('bills.html', bills=bills)

@app.route('/bill/<int:bill_id>')
def bill_detail(bill_id):
    """账单详情页面"""
    bill = manager.get_bill_details(bill_id)
    if not bill:
        return "账单不存在", 404
    return render_template('bill_detail.html', bill=bill)

@app.route('/api/users', methods=['POST'])
def add_user():
    """添加用户API"""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': '用户名不能为空'})
    
    user_id = manager.add_user(name, email, phone)
    if user_id:
        return jsonify({'success': True, 'message': '用户添加成功', 'user_id': user_id})
    else:
        return jsonify({'success': False, 'message': '用户名已存在'})

@app.route('/api/bills', methods=['POST'])
def create_bill():
    """创建账单API"""
    data = request.get_json()
    title = data.get('title', '').strip()
    total_amount = float(data.get('total_amount', 0))
    description = data.get('description', '').strip()
    split_type = data.get('split_type', 'equal')
    user_ids = data.get('user_ids', [])
    custom_amounts = data.get('custom_amounts', {})
    
    if not title or total_amount <= 0 or not user_ids:
        return jsonify({'success': False, 'message': '请填写完整信息'})
    
    try:
        bill_id = manager.create_bill(title, total_amount, description, split_type, user_ids, custom_amounts)
        return jsonify({'success': True, 'message': '账单创建成功', 'bill_id': bill_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'})

@app.route('/api/bills/<int:bill_id>/pay', methods=['POST'])
def mark_paid():
    """标记支付API"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if manager.mark_paid(bill_id, user_id):
        return jsonify({'success': True, 'message': '标记成功'})
    else:
        return jsonify({'success': False, 'message': '标记失败'})

@app.route('/api/users')
def get_users():
    """获取用户列表API"""
    users = manager.get_users()
    return jsonify(users)

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动应用
    print("分账程序启动中...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)