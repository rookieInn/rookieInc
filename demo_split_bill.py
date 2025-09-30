#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分账程序演示脚本
展示如何使用分账程序的基本功能
"""

import sqlite3
import json
from datetime import datetime

def init_demo_data():
    """初始化演示数据"""
    conn = sqlite3.connect('split_bills.db')
    cursor = conn.cursor()
    
    # 清空现有数据
    cursor.execute('DELETE FROM bill_splits')
    cursor.execute('DELETE FROM bills')
    cursor.execute('DELETE FROM users')
    
    # 添加演示用户
    users = [
        ('张三', 'zhangsan@example.com', '13800138001'),
        ('李四', 'lisi@example.com', '13800138002'),
        ('王五', 'wangwu@example.com', '13800138003'),
        ('赵六', 'zhaoliu@example.com', '13800138004'),
        ('钱七', 'qianqi@example.com', '13800138005'),
    ]
    
    user_ids = []
    for name, email, phone in users:
        cursor.execute(
            'INSERT INTO users (name, email, phone) VALUES (?, ?, ?)',
            (name, email, phone)
        )
        user_ids.append(cursor.lastrowid)
    
    # 创建演示账单
    bills = [
        {
            'title': '聚餐费用',
            'total_amount': 300.00,
            'description': '周末聚餐，包含餐费和酒水',
            'split_type': 'equal',
            'user_ids': user_ids[:4]  # 前4个人
        },
        {
            'title': 'KTV包房费',
            'total_amount': 200.00,
            'description': 'KTV包房3小时',
            'split_type': 'equal',
            'user_ids': user_ids[:3]  # 前3个人
        },
        {
            'title': '打车费用',
            'total_amount': 50.00,
            'description': '从KTV到家的打车费',
            'split_type': 'custom',
            'user_ids': user_ids[:2],  # 前2个人
            'custom_amounts': {user_ids[0]: 30.00, user_ids[1]: 20.00}
        }
    ]
    
    for bill_data in bills:
        # 创建账单
        cursor.execute(
            'INSERT INTO bills (title, total_amount, description, split_type, created_by) VALUES (?, ?, ?, ?, ?)',
            (bill_data['title'], bill_data['total_amount'], bill_data['description'], 
             bill_data['split_type'], bill_data['user_ids'][0])
        )
        bill_id = cursor.lastrowid
        
        # 创建分账记录
        if bill_data['split_type'] == 'equal':
            amount_per_person = bill_data['total_amount'] / len(bill_data['user_ids'])
            for user_id in bill_data['user_ids']:
                cursor.execute(
                    'INSERT INTO bill_splits (bill_id, user_id, amount) VALUES (?, ?, ?)',
                    (bill_id, user_id, amount_per_person)
                )
        elif bill_data['split_type'] == 'custom':
            for user_id, amount in bill_data['custom_amounts'].items():
                cursor.execute(
                    'INSERT INTO bill_splits (bill_id, user_id, amount) VALUES (?, ?, ?)',
                    (bill_id, user_id, amount)
                )
        
        # 模拟部分支付
        if bill_data['title'] == '聚餐费用':
            # 张三已支付
            cursor.execute(
                'UPDATE bill_splits SET is_paid = TRUE, paid_at = CURRENT_TIMESTAMP WHERE bill_id = ? AND user_id = ?',
                (bill_id, user_ids[0])
            )
    
    conn.commit()
    conn.close()
    
    print("演示数据初始化完成！")
    print("包含以下内容：")
    print("- 5个用户：张三、李四、王五、赵六、钱七")
    print("- 3个账单：聚餐费用、KTV包房费、打车费用")
    print("- 部分支付状态：张三已支付聚餐费用")

def show_demo_data():
    """显示演示数据"""
    conn = sqlite3.connect('split_bills.db')
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("演示数据概览")
    print("="*50)
    
    # 显示用户
    cursor.execute('SELECT name, email, phone FROM users ORDER BY name')
    users = cursor.fetchall()
    print(f"\n用户列表 ({len(users)}人):")
    for name, email, phone in users:
        print(f"  - {name} ({email}, {phone})")
    
    # 显示账单
    cursor.execute('''
        SELECT b.title, b.total_amount, b.split_type, b.created_at, u.name
        FROM bills b
        LEFT JOIN users u ON b.created_by = u.id
        ORDER BY b.created_at DESC
    ''')
    bills = cursor.fetchall()
    
    print(f"\n账单列表 ({len(bills)}个):")
    for title, amount, split_type, created_at, creator in bills:
        print(f"  - {title}: ¥{amount:.2f} ({split_type}) - 创建者: {creator}")
        
        # 显示分账详情
        cursor.execute('''
            SELECT u.name, bs.amount, bs.is_paid
            FROM bill_splits bs
            JOIN users u ON bs.user_id = u.id
            WHERE bs.bill_id = (
                SELECT id FROM bills WHERE title = ? AND created_at = ?
            )
            ORDER BY u.name
        ''', (title, created_at))
        
        splits = cursor.fetchall()
        for name, amount, is_paid in splits:
            status = "已支付" if is_paid else "未支付"
            print(f"    * {name}: ¥{amount:.2f} ({status})")
    
    conn.close()

def main():
    """主函数"""
    print("分账程序演示")
    print("="*30)
    
    try:
        # 初始化演示数据
        init_demo_data()
        
        # 显示演示数据
        show_demo_data()
        
        print("\n" + "="*50)
        print("演示数据已准备就绪！")
        print("现在可以启动分账程序查看效果：")
        print("  python3 split_bill_app.py")
        print("然后访问: http://localhost:5000")
        print("="*50)
        
    except Exception as e:
        print(f"初始化演示数据失败: {e}")

if __name__ == "__main__":
    main()