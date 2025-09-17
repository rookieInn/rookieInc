#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信群机器人健康检查服务
提供HTTP健康检查端点
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 全局状态
bot_status = {
    'running': False,
    'last_check': None,
    'error': None
}

@app.route('/health')
def health_check():
    """健康检查接口"""
    try:
        current_time = datetime.now().isoformat()
        
        # 检查机器人是否在运行
        if bot_status['running']:
            return jsonify({
                'status': 'healthy',
                'bot': 'running',
                'last_check': bot_status['last_check'],
                'timestamp': current_time
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'bot': 'stopped',
                'error': bot_status.get('error', 'Unknown error'),
                'last_check': bot_status['last_check'],
                'timestamp': current_time
            }), 500
            
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/status')
def get_status():
    """获取机器人状态"""
    try:
        return jsonify({
            'bot_status': bot_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({'error': str(e)}), 500

def update_bot_status(running, error=None):
    """更新机器人状态"""
    global bot_status
    bot_status['running'] = running
    bot_status['last_check'] = datetime.now().isoformat()
    if error:
        bot_status['error'] = str(error)
    else:
        bot_status['error'] = None

def start_health_server():
    """启动健康检查服务器"""
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    logger.info(f"🚀 启动健康检查服务: http://{host}:{port}")
    logger.info(f"📊 健康检查: http://{host}:{port}/health")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 在后台线程中启动健康检查服务器
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # 模拟机器人状态更新
    try:
        while True:
            # 这里可以添加实际的机器人状态检查逻辑
            update_bot_status(True)
            time.sleep(30)  # 每30秒更新一次状态
    except KeyboardInterrupt:
        logger.info("健康检查服务停止")
        update_bot_status(False, "Service stopped")
        sys.exit(0)