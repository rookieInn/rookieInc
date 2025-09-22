#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的埋点API服务 - 集成AOP操作日志记录
在原有tracking_api.py基础上添加操作日志记录功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, Any, Optional
from configparser import ConfigParser
import traceback

# 导入原有的模型和服务
from tracking_models import (
    TrackingDatabase, 
    UserEvent, 
    PageView, 
    generate_session_id, 
    generate_event_id
)

# 导入AOP操作日志系统
from aop_operation_logger import (
    operation_log, log_create, log_update, log_delete, log_read,
    log_login, log_logout, log_system, log_config,
    OperationType, OperationStatus, get_operation_logger
)
from operation_log_service import get_operation_log_service

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

# 初始化操作日志服务
try:
    operation_log_service = get_operation_log_service()
    logger.info("✅ 操作日志服务初始化成功")
except Exception as e:
    logger.error(f"❌ 操作日志服务初始化失败: {e}")
    operation_log_service = None

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
@operation_log(
    operation_type=OperationType.CREATE,
    operation_name="埋点事件记录",
    description="记录用户行为埋点事件",
    module_name="tracking_api"
)
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
@operation_log(
    operation_type=OperationType.READ,
    operation_name="页面访问记录",
    description="记录用户页面访问行为",
    module_name="tracking_api"
)
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
@operation_log(
    operation_type=OperationType.CREATE,
    operation_name="批量埋点记录",
    description="批量记录用户行为埋点事件",
    module_name="tracking_api"
)
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
@log_read("事件统计查询", "查询埋点事件统计信息")
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
@log_read("页面统计查询", "查询页面访问统计信息")
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

# 新增操作日志管理API
@app.route('/api/operation-logs', methods=['GET'])
@log_read("操作日志查询", "查询系统操作日志")
def get_operation_logs():
    """获取操作日志列表"""
    try:
        if not operation_log_service:
            return jsonify({'error': 'Operation log service not available'}), 500
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        user_id = request.args.get('user_id')
        operation_type = request.args.get('operation_type')
        status = request.args.get('status')
        days = int(request.args.get('days', 7))
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logs = operation_log_service.get_logs(
            user_id=user_id,
            operation_type=operation_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=(page - 1) * limit
        )
        
        return jsonify({
            'success': True,
            'data': logs
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取操作日志失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/operation-logs/statistics', methods=['GET'])
@log_read("操作日志统计", "查询操作日志统计信息")
def get_operation_log_statistics():
    """获取操作日志统计信息"""
    try:
        if not operation_log_service:
            return jsonify({'error': 'Operation log service not available'}), 500
        
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = operation_log_service.get_statistics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 获取操作日志统计失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/operation-logs/export', methods=['POST'])
@log_export("操作日志导出", "导出操作日志数据")
def export_operation_logs():
    """导出操作日志"""
    try:
        if not operation_log_service:
            return jsonify({'error': 'Operation log service not available'}), 500
        
        data = request.get_json()
        days = data.get('days', 30)
        format_type = data.get('format', 'json')
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        filepath = operation_log_service.export_logs(start_date, end_date, format_type)
        
        if filepath:
            return jsonify({
                'success': True,
                'filepath': filepath,
                'message': 'Export completed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Export failed'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ 导出操作日志失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/operation-logs/cleanup', methods=['POST'])
@log_system("操作日志清理", "清理过期的操作日志")
def cleanup_operation_logs():
    """清理过期的操作日志"""
    try:
        if not operation_log_service:
            return jsonify({'error': 'Operation log service not available'}), 500
        
        data = request.get_json()
        days = data.get('days', 30)
        
        deleted_count = operation_log_service.cleanup_old_logs(days)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} old logs'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 清理操作日志失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/health', methods=['GET'])
@log_read("健康检查", "检查系统健康状态")
def health_check():
    """健康检查接口"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # 检查埋点数据库
        if db:
            try:
                db.client.admin.command('ping')
                health_status['services']['tracking_db'] = 'connected'
            except Exception as e:
                health_status['services']['tracking_db'] = f'error: {str(e)}'
                health_status['status'] = 'unhealthy'
        else:
            health_status['services']['tracking_db'] = 'not_initialized'
            health_status['status'] = 'unhealthy'
        
        # 检查操作日志服务
        if operation_log_service:
            health_status['services']['operation_logs'] = 'connected'
        else:
            health_status['services']['operation_logs'] = 'not_initialized'
            health_status['status'] = 'unhealthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 500
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
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
    
    logger.info(f"🚀 启动增强埋点API服务: http://{host}:{port}")
    logger.info(f"📊 健康检查: http://{host}:{port}/api/health")
    logger.info(f"📈 事件统计: http://{host}:{port}/api/stats/events")
    logger.info(f"📄 页面统计: http://{host}:{port}/api/stats/pages")
    logger.info(f"📋 操作日志: http://{host}:{port}/api/operation-logs")
    logger.info(f"📊 操作统计: http://{host}:{port}/api/operation-logs/statistics")
    
    app.run(host=host, port=port, debug=debug)