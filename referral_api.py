#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享返佣裂变系统 API 接口
Referral Commission Fission System API

提供RESTful API接口用于：
1. 用户注册和登录
2. 分享链接管理
3. 返佣数据查询
4. 统计分析接口
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import logging
from datetime import datetime
from referral_system import ReferralSystem, User, ReferralLink, Commission
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化返佣系统
referral_system = ReferralSystem()

@app.route('/')
def index():
    """首页"""
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    """用户注册API"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        referrer_code = data.get('referrer_code')
        
        if not all([username, email, phone]):
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和手机号不能为空'
            }), 400
        
        user = referral_system.register_user(username, email, phone, referrer_code)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'user_id': user.user_id,
                'username': user.username,
                'invite_code': user.invite_code,
                'level': user.level
            }
        })
    
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@app.route('/api/user/<user_id>')
def get_user_info(user_id):
    """获取用户信息"""
    try:
        stats = referral_system.get_user_stats(user_id)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@app.route('/api/link/create', methods=['POST'])
def create_referral_link():
    """创建分享链接API"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        original_url = data.get('original_url')
        expires_days = data.get('expires_days', 30)
        
        if not all([user_id, original_url]):
            return jsonify({
                'success': False,
                'message': '用户ID和原始URL不能为空'
            }), 400
        
        link = referral_system.create_referral_link(user_id, original_url, expires_days)
        
        return jsonify({
            'success': True,
            'message': '分享链接创建成功',
            'data': {
                'link_id': link.link_id,
                'short_code': link.short_code,
                'original_url': link.original_url,
                'short_url': f"https://your-domain.com/r/{link.short_code}",
                'expires_at': link.expires_at.isoformat() if link.expires_at else None
            }
        })
    
    except Exception as e:
        logger.error(f"创建分享链接失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建分享链接失败: {str(e)}'
        }), 500

@app.route('/api/link/<short_code>/click')
def track_link_click(short_code):
    """追踪链接点击API"""
    try:
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        original_url = referral_system.track_click(short_code, ip_address, user_agent)
        
        if original_url:
            return jsonify({
                'success': True,
                'data': {
                    'original_url': original_url,
                    'redirect': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '链接不存在或已过期'
            }), 404
    
    except Exception as e:
        logger.error(f"追踪链接点击失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'追踪链接点击失败: {str(e)}'
        }), 500

@app.route('/r/<short_code>')
def redirect_link(short_code):
    """短链接重定向"""
    try:
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        original_url = referral_system.track_click(short_code, ip_address, user_agent)
        
        if original_url:
            return f'<script>window.location.href = "{original_url}";</script>'
        else:
            return '<h1>链接不存在或已过期</h1>', 404
    
    except Exception as e:
        logger.error(f"链接重定向失败: {str(e)}")
        return '<h1>链接重定向失败</h1>', 500

@app.route('/api/conversion', methods=['POST'])
def process_conversion():
    """处理转化API"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        if not all([user_id, order_id, amount]):
            return jsonify({
                'success': False,
                'message': '用户ID、订单ID和金额不能为空'
            }), 400
        
        commissions = referral_system.process_conversion(user_id, order_id, float(amount))
        
        return jsonify({
            'success': True,
            'message': '转化处理成功',
            'data': {
                'commissions': [
                    {
                        'commission_id': comm.commission_id,
                        'referrer_id': comm.referrer_id,
                        'amount': comm.amount,
                        'type': comm.commission_type.value,
                        'status': comm.status
                    } for comm in commissions
                ]
            }
        })
    
    except Exception as e:
        logger.error(f"处理转化失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理转化失败: {str(e)}'
        }), 500

@app.route('/api/analytics')
def get_analytics():
    """获取系统分析数据API"""
    try:
        analytics = referral_system.get_system_analytics()
        return jsonify({
            'success': True,
            'data': analytics
        })
    except Exception as e:
        logger.error(f"获取分析数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取分析数据失败: {str(e)}'
        }), 500

@app.route('/api/commissions/<user_id>')
def get_user_commissions(user_id):
    """获取用户返佣记录API"""
    try:
        import sqlite3
        conn = sqlite3.connect(referral_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT commission_id, amount, commission_type, order_id, status, created_at
            FROM commissions 
            WHERE referrer_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        commissions = []
        for row in cursor.fetchall():
            commissions.append({
                'commission_id': row[0],
                'amount': row[1],
                'type': row[2],
                'order_id': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': commissions
        })
    
    except Exception as e:
        logger.error(f"获取返佣记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取返佣记录失败: {str(e)}'
        }), 500

@app.route('/api/links/<user_id>')
def get_user_links(user_id):
    """获取用户分享链接API"""
    try:
        import sqlite3
        conn = sqlite3.connect(referral_system.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT link_id, original_url, short_code, click_count, conversion_count, created_at, expires_at
            FROM referral_links 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        links = []
        for row in cursor.fetchall():
            links.append({
                'link_id': row[0],
                'original_url': row[1],
                'short_code': row[2],
                'short_url': f"https://your-domain.com/r/{row[2]}",
                'click_count': row[3],
                'conversion_count': row[4],
                'created_at': row[5],
                'expires_at': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': links
        })
    
    except Exception as e:
        logger.error(f"获取分享链接失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取分享链接失败: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    
    print("=== 分享返佣裂变系统 API 服务启动 ===")
    print("API文档地址: http://localhost:5000")
    print("测试接口: http://localhost:5000/api/analytics")
    
    app.run(host='0.0.0.0', port=5000, debug=True)