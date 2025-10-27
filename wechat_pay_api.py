#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信支付API接口
提供RESTful API接口，支持小程序支付、H5支付等
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, render_template_string
from werkzeug.exceptions import BadRequest
import threading
import time

from wechat_pay_core import WeChatPayCore

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_pay_api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化微信支付
wechat_pay = WeChatPayCore()

# 数据库初始化
def init_database():
    """初始化数据库"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        # 创建支付记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                out_trade_no TEXT UNIQUE NOT NULL,
                openid TEXT,
                total_fee INTEGER NOT NULL,
                body TEXT NOT NULL,
                attach TEXT,
                trade_type TEXT NOT NULL,
                prepay_id TEXT,
                transaction_id TEXT,
                trade_state TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建退款记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refunds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                out_trade_no TEXT NOT NULL,
                out_refund_no TEXT UNIQUE NOT NULL,
                refund_fee INTEGER NOT NULL,
                refund_desc TEXT,
                refund_id TEXT,
                refund_status TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

def save_payment_record(payment_data: Dict[str, Any]) -> bool:
    """保存支付记录"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO payments 
            (out_trade_no, openid, total_fee, body, attach, trade_type, prepay_id, transaction_id, trade_state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data.get('out_trade_no'),
            payment_data.get('openid'),
            payment_data.get('total_fee'),
            payment_data.get('body'),
            payment_data.get('attach'),
            payment_data.get('trade_type'),
            payment_data.get('prepay_id'),
            payment_data.get('transaction_id'),
            payment_data.get('trade_state', 'NOTPAY')
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"保存支付记录失败: {e}")
        return False

def update_payment_status(out_trade_no: str, transaction_id: str, trade_state: str) -> bool:
    """更新支付状态"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE payments 
            SET transaction_id = ?, trade_state = ?, update_time = CURRENT_TIMESTAMP
            WHERE out_trade_no = ?
        ''', (transaction_id, trade_state, out_trade_no))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"更新支付状态失败: {e}")
        return False

def save_refund_record(refund_data: Dict[str, Any]) -> bool:
    """保存退款记录"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO refunds 
            (out_trade_no, out_refund_no, refund_fee, refund_desc, refund_id, refund_status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            refund_data.get('out_trade_no'),
            refund_data.get('out_refund_no'),
            refund_data.get('refund_fee'),
            refund_data.get('refund_desc'),
            refund_data.get('refund_id'),
            refund_data.get('refund_status', 'PROCESSING')
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"保存退款记录失败: {e}")
        return False

@app.route('/api/wechat/pay/miniprogram', methods=['POST'])
def create_miniprogram_payment():
    """创建小程序支付订单"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['openid', 'total_fee', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 创建支付订单
        result = wechat_pay.create_miniprogram_payment(
            openid=data['openid'],
            total_fee=data['total_fee'],
            body=data['body'],
            out_trade_no=data.get('out_trade_no'),
            attach=data.get('attach'),
            time_expire=data.get('time_expire')
        )
        
        if result['success']:
            # 保存支付记录
            payment_data = {
                'out_trade_no': result['out_trade_no'],
                'openid': data['openid'],
                'total_fee': data['total_fee'],
                'body': data['body'],
                'attach': data.get('attach'),
                'trade_type': 'JSAPI',
                'prepay_id': result['prepay_id']
            }
            save_payment_record(payment_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'out_trade_no': result['out_trade_no'],
                    'prepay_id': result['prepay_id'],
                    'miniprogram_params': result['miniprogram_params']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"创建小程序支付订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/h5', methods=['POST'])
def create_h5_payment():
    """创建H5支付订单"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['total_fee', 'body']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 创建支付订单
        result = wechat_pay.create_h5_payment(
            total_fee=data['total_fee'],
            body=data['body'],
            out_trade_no=data.get('out_trade_no'),
            attach=data.get('attach'),
            time_expire=data.get('time_expire')
        )
        
        if result['success']:
            # 保存支付记录
            payment_data = {
                'out_trade_no': result['out_trade_no'],
                'total_fee': data['total_fee'],
                'body': data['body'],
                'attach': data.get('attach'),
                'trade_type': 'MWEB',
                'prepay_id': result['prepay_id']
            }
            save_payment_record(payment_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'out_trade_no': result['out_trade_no'],
                    'prepay_id': result['prepay_id'],
                    'mweb_url': result['mweb_url']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"创建H5支付订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/query', methods=['POST'])
def query_payment():
    """查询支付订单状态"""
    try:
        data = request.get_json()
        
        if 'out_trade_no' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: out_trade_no'
            }), 400
        
        # 查询订单
        result = wechat_pay.query_order(data['out_trade_no'])
        
        if result['success']:
            # 更新本地数据库
            if result.get('transaction_id'):
                update_payment_status(
                    data['out_trade_no'],
                    result['transaction_id'],
                    result['trade_state']
                )
            
            return jsonify({
                'success': True,
                'data': {
                    'out_trade_no': data['out_trade_no'],
                    'trade_state': result['trade_state'],
                    'trade_state_desc': result['trade_state_desc'],
                    'transaction_id': result.get('transaction_id')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"查询支付订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/close', methods=['POST'])
def close_payment():
    """关闭支付订单"""
    try:
        data = request.get_json()
        
        if 'out_trade_no' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: out_trade_no'
            }), 400
        
        # 关闭订单
        result = wechat_pay.close_order(data['out_trade_no'])
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '订单关闭成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"关闭支付订单失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/refund', methods=['POST'])
def create_refund():
    """申请退款"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['out_trade_no', 'out_refund_no', 'total_fee', 'refund_fee']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 申请退款
        result = wechat_pay.refund(
            out_trade_no=data['out_trade_no'],
            out_refund_no=data['out_refund_no'],
            total_fee=data['total_fee'],
            refund_fee=data['refund_fee'],
            refund_desc=data.get('refund_desc')
        )
        
        if result['success']:
            # 保存退款记录
            refund_data = {
                'out_trade_no': data['out_trade_no'],
                'out_refund_no': data['out_refund_no'],
                'refund_fee': data['refund_fee'],
                'refund_desc': data.get('refund_desc'),
                'refund_id': result['refund_id']
            }
            save_refund_record(refund_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'out_refund_no': data['out_refund_no'],
                    'refund_id': result['refund_id']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"申请退款失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/notify', methods=['POST'])
def payment_notify():
    """支付回调通知"""
    try:
        # 获取原始XML数据
        xml_data = request.get_data(as_text=True)
        
        # 验证签名
        is_valid, notify_data = wechat_pay.verify_notify(xml_data)
        
        if not is_valid:
            logger.warning("支付回调签名验证失败")
            return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名验证失败]]></return_msg></xml>'
        
        # 处理支付结果
        out_trade_no = notify_data.get('out_trade_no')
        transaction_id = notify_data.get('transaction_id')
        trade_state = notify_data.get('result_code')
        
        if trade_state == 'SUCCESS':
            # 支付成功，更新数据库
            update_payment_status(out_trade_no, transaction_id, 'SUCCESS')
            logger.info(f"支付成功: {out_trade_no}")
            
            # 这里可以添加业务逻辑，如发货、发送通知等
            # process_payment_success(out_trade_no, notify_data)
            
        else:
            # 支付失败
            update_payment_status(out_trade_no, transaction_id, 'FAIL')
            logger.warning(f"支付失败: {out_trade_no}")
        
        # 返回成功响应
        return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
        
    except Exception as e:
        logger.error(f"处理支付回调失败: {e}")
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[处理失败]]></return_msg></xml>'

@app.route('/api/wechat/pay/refund/notify', methods=['POST'])
def refund_notify():
    """退款回调通知"""
    try:
        # 获取原始XML数据
        xml_data = request.get_data(as_text=True)
        
        # 验证签名
        is_valid, notify_data = wechat_pay.verify_refund_notify(xml_data)
        
        if not is_valid:
            logger.warning("退款回调签名验证失败")
            return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[签名验证失败]]></return_msg></xml>'
        
        # 处理退款结果
        out_refund_no = notify_data.get('out_refund_no')
        refund_status = notify_data.get('refund_status')
        
        if refund_status == 'SUCCESS':
            logger.info(f"退款成功: {out_refund_no}")
            # 这里可以添加业务逻辑，如更新订单状态等
            # process_refund_success(out_refund_no, notify_data)
        else:
            logger.warning(f"退款失败: {out_refund_no}")
        
        # 返回成功响应
        return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
        
    except Exception as e:
        logger.error(f"处理退款回调失败: {e}")
        return '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[处理失败]]></return_msg></xml>'

@app.route('/api/wechat/pay/status/<out_trade_no>', methods=['GET'])
def get_payment_status(out_trade_no):
    """获取支付状态"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT out_trade_no, trade_state, transaction_id, create_time, update_time
            FROM payments 
            WHERE out_trade_no = ?
        ''', (out_trade_no,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'data': {
                    'out_trade_no': result[0],
                    'trade_state': result[1],
                    'transaction_id': result[2],
                    'create_time': result[3],
                    'update_time': result[4]
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '订单不存在'
            }), 404
            
    except Exception as e:
        logger.error(f"获取支付状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/records', methods=['GET'])
def get_payment_records():
    """获取支付记录列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute('SELECT COUNT(*) FROM payments')
        total = cursor.fetchone()[0]
        
        # 获取记录
        cursor.execute('''
            SELECT out_trade_no, openid, total_fee, body, trade_type, trade_state, create_time
            FROM payments 
            ORDER BY create_time DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        records = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'records': [
                    {
                        'out_trade_no': record[0],
                        'openid': record[1],
                        'total_fee': record[2],
                        'body': record[3],
                        'trade_type': record[4],
                        'trade_state': record[5],
                        'create_time': record[6]
                    }
                    for record in records
                ],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取支付记录失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/wechat/pay/dashboard', methods=['GET'])
def payment_dashboard():
    """支付数据看板"""
    try:
        conn = sqlite3.connect('wechat_pay.db')
        cursor = conn.cursor()
        
        # 今日支付统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN trade_state = 'SUCCESS' THEN 1 ELSE 0 END) as success_orders,
                SUM(CASE WHEN trade_state = 'SUCCESS' THEN total_fee ELSE 0 END) as success_amount
            FROM payments 
            WHERE DATE(create_time) = DATE('now')
        ''')
        today_stats = cursor.fetchone()
        
        # 总支付统计
        cursor.execute('''
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN trade_state = 'SUCCESS' THEN 1 ELSE 0 END) as success_orders,
                SUM(CASE WHEN trade_state = 'SUCCESS' THEN total_fee ELSE 0 END) as success_amount
            FROM payments
        ''')
        total_stats = cursor.fetchone()
        
        # 最近7天支付趋势
        cursor.execute('''
            SELECT 
                DATE(create_time) as date,
                COUNT(*) as orders,
                SUM(CASE WHEN trade_state = 'SUCCESS' THEN total_fee ELSE 0 END) as amount
            FROM payments 
            WHERE create_time >= DATE('now', '-7 days')
            GROUP BY DATE(create_time)
            ORDER BY date
        ''')
        trend_data = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'today': {
                    'total_orders': today_stats[0] or 0,
                    'success_orders': today_stats[1] or 0,
                    'success_amount': today_stats[2] or 0
                },
                'total': {
                    'total_orders': total_stats[0] or 0,
                    'success_orders': total_stats[1] or 0,
                    'success_amount': total_stats[2] or 0
                },
                'trend': [
                    {
                        'date': record[0],
                        'orders': record[1],
                        'amount': record[2]
                    }
                    for record in trend_data
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"获取支付看板数据失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """首页"""
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>微信支付API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .api-item { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .method { display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-weight: bold; }
            .post { background-color: #28a745; }
            .get { background-color: #007bff; }
            code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>微信支付API接口</h1>
            <p>支持小程序支付、H5支付、订单查询、退款等功能</p>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/miniprogram</h3>
                <p>创建小程序支付订单</p>
                <p><strong>参数:</strong> openid, total_fee, body, out_trade_no(可选), attach(可选)</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/h5</h3>
                <p>创建H5支付订单</p>
                <p><strong>参数:</strong> total_fee, body, out_trade_no(可选), attach(可选)</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/query</h3>
                <p>查询支付订单状态</p>
                <p><strong>参数:</strong> out_trade_no</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/close</h3>
                <p>关闭支付订单</p>
                <p><strong>参数:</strong> out_trade_no</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/refund</h3>
                <p>申请退款</p>
                <p><strong>参数:</strong> out_trade_no, out_refund_no, total_fee, refund_fee, refund_desc(可选)</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method get">GET</span> /api/wechat/pay/status/{out_trade_no}</h3>
                <p>获取支付状态</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method get">GET</span> /api/wechat/pay/records</h3>
                <p>获取支付记录列表</p>
                <p><strong>参数:</strong> page(可选), limit(可选)</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method get">GET</span> /api/wechat/pay/dashboard</h3>
                <p>获取支付数据看板</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/notify</h3>
                <p>支付回调通知（微信服务器调用）</p>
            </div>
            
            <div class="api-item">
                <h3><span class="method post">POST</span> /api/wechat/pay/refund/notify</h3>
                <p>退款回调通知（微信服务器调用）</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html_template

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动API服务
    print("微信支付API服务启动中...")
    print("=" * 50)
    print("API文档: http://localhost:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)