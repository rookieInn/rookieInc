#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面埋点API服务
提供RESTful API接口接收前端埋点数据并存储到MongoDB
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any, Optional
from configparser import ConfigParser
import traceback

from tracking_models import (
    TrackingDatabase, 
    UserEvent, 
    PageView, 
    generate_session_id, 
    generate_event_id
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 读取配置
config = ConfigParser()
config.read('config.ini', encoding='utf-8')

# 配置CORS
if config.getboolean('tracking_api', 'enable_cors', fallback=True):
    CORS(app, origins='*')

# 初始化数据库连接
try:
    db = TrackingDatabase()
    logger.info("✅ 数据库连接初始化成功")
except Exception as e:
    logger.error(f"❌ 数据库连接初始化失败: {e}")
    db = None

def validate_api_key() -> bool:
    """验证API密钥"""
    api_key = config.get('tracking_api', 'api_key', fallback='')
    if not api_key:
        return True  # 如果没有设置API密钥，则跳过验证
    
    provided_key = request.headers.get('X-API-Key', '')
    return provided_key == api_key

def get_client_info() -> Dict[str, Any]:
    """获取客户端信息"""
    return {
        'user_agent': request.headers.get('User-Agent', ''),
        'ip_address': request.remote_addr,
        'referrer': request.headers.get('Referer', ''),
        'accept_language': request.headers.get('Accept-Language', ''),
        'accept_encoding': request.headers.get('Accept-Encoding', '')
    }

@app.route('/api/track/event', methods=['POST'])
def track_event():
    """接收用户事件数据"""
    try:
        if not validate_api_key():
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 获取客户端信息
        client_info = get_client_info()
        
        # 创建用户事件对象
        event = UserEvent(
            event_id=generate_event_id(),
            user_id=data.get('user_id'),
            session_id=data.get('session_id', generate_session_id()),
            event_type=data.get('event_type', 'custom'),
            page_url=data.get('page_url', ''),
            page_title=data.get('page_title', ''),
            element_id=data.get('element_id'),
            element_class=data.get('element_class'),
            element_text=data.get('element_text'),
            x_position=data.get('x_position'),
            y_position=data.get('y_position'),
            scroll_depth=data.get('scroll_depth'),
            referrer=data.get('referrer', client_info['referrer']),
            user_agent=client_info['user_agent'],
            screen_resolution=data.get('screen_resolution'),
            viewport_size=data.get('viewport_size'),
            timestamp=datetime.now(),
            custom_data=data.get('custom_data'),
            duration=data.get('duration')
        )
        
        # 插入数据库
        success = db.insert_event(event)
        
        if success:
            return jsonify({
                'success': True,
                'event_id': event.event_id,
                'message': 'Event tracked successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to insert event'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ 事件跟踪失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/track/pageview', methods=['POST'])
def track_pageview():
    """接收页面访问数据"""
    try:
        if not validate_api_key():
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 获取客户端信息
        client_info = get_client_info()
        
        # 创建页面访问对象
        pageview = PageView(
            page_id=generate_event_id(),
            user_id=data.get('user_id'),
            session_id=data.get('session_id', generate_session_id()),
            page_url=data.get('page_url', ''),
            page_title=data.get('page_title', ''),
            referrer=data.get('referrer', client_info['referrer']),
            user_agent=client_info['user_agent'],
            screen_resolution=data.get('screen_resolution'),
            viewport_size=data.get('viewport_size'),
            load_time=data.get('load_time'),
            timestamp=datetime.now(),
            exit_timestamp=data.get('exit_timestamp'),
            duration=data.get('duration')
        )
        
        # 插入数据库
        success = db.insert_pageview(pageview)
        
        if success:
            return jsonify({
                'success': True,
                'page_id': pageview.page_id,
                'message': 'Pageview tracked successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to insert pageview'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ 页面访问跟踪失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/track/batch', methods=['POST'])
def track_batch():
    """批量接收埋点数据"""
    try:
        if not validate_api_key():
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        data = request.get_json()
        if not data or 'events' not in data:
            return jsonify({'error': 'No events data provided'}), 400
        
        events = data['events']
        if not isinstance(events, list):
            return jsonify({'error': 'Events must be a list'}), 400
        
        client_info = get_client_info()
        results = []
        
        for event_data in events:
            try:
                # 创建用户事件对象
                event = UserEvent(
                    event_id=generate_event_id(),
                    user_id=event_data.get('user_id'),
                    session_id=event_data.get('session_id', generate_session_id()),
                    event_type=event_data.get('event_type', 'custom'),
                    page_url=event_data.get('page_url', ''),
                    page_title=event_data.get('page_title', ''),
                    element_id=event_data.get('element_id'),
                    element_class=event_data.get('element_class'),
                    element_text=event_data.get('element_text'),
                    x_position=event_data.get('x_position'),
                    y_position=event_data.get('y_position'),
                    scroll_depth=event_data.get('scroll_depth'),
                    referrer=event_data.get('referrer', client_info['referrer']),
                    user_agent=client_info['user_agent'],
                    screen_resolution=event_data.get('screen_resolution'),
                    viewport_size=event_data.get('viewport_size'),
                    timestamp=datetime.now(),
                    custom_data=event_data.get('custom_data'),
                    duration=event_data.get('duration')
                )
                
                # 插入数据库
                success = db.insert_event(event)
                results.append({
                    'event_id': event.event_id,
                    'success': success
                })
                
            except Exception as e:
                logger.error(f"❌ 批量事件处理失败: {e}")
                results.append({
                    'event_id': None,
                    'success': False,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'total_events': len(events),
            'successful_events': success_count,
            'failed_events': len(events) - success_count,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 批量跟踪失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/stats/events', methods=['GET'])
def get_event_stats():
    """获取事件统计信息"""
    try:
        if not validate_api_key():
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # 获取查询参数
        days = int(request.args.get('days', 7))
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        # 获取统计信息
        stats = db.get_event_statistics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取事件统计失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/stats/pages', methods=['GET'])
def get_page_stats():
    """获取页面统计信息"""
    try:
        if not validate_api_key():
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # 获取查询参数
        days = int(request.args.get('days', 7))
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        # 获取统计信息
        stats = db.get_page_statistics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取页面统计失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        if db:
            # 测试数据库连接
            db.client.admin.command('ping')
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # 从配置文件读取服务器配置
    host = config.get('tracking_api', 'host', fallback='0.0.0.0')
    port = config.getint('tracking_api', 'port', fallback=5000)
    debug = config.getboolean('tracking_api', 'debug', fallback=True)
    
    logger.info(f"🚀 启动埋点API服务: http://{host}:{port}")
    logger.info(f"📊 健康检查: http://{host}:{port}/api/health")
    logger.info(f"📈 事件统计: http://{host}:{port}/api/stats/events")
    logger.info(f"📄 页面统计: http://{host}:{port}/api/stats/pages")
    
    app.run(host=host, port=port, debug=debug)