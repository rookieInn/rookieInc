#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频水印Web服务
提供RESTful API接口处理视频水印
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil

# 导入视频水印处理器
from video_watermark import VideoWatermarkProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'data/video/input'
OUTPUT_FOLDER = 'data/video/output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}

# 创建必要目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 初始化视频处理器
video_processor = VideoWatermarkProcessor()

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查FFmpeg是否可用
        video_processor._check_ffmpeg()
        
        return jsonify({
            'status': 'healthy',
            'ffmpeg': 'available',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'ffmpeg': 'unavailable',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            return jsonify({
                'message': '文件上传成功',
                'filename': filename,
                'filepath': filepath
            }), 200
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        logger.error(f"上传文件失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watermark/text', methods=['POST'])
def add_text_watermark():
    """添加文字水印"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['input_file', 'text']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        input_file = data['input_file']
        text = data['text']
        position = data.get('position', 'bottom-right')
        font_size = data.get('font_size', 24)
        font_color = data.get('font_color', 'white')
        background_color = data.get('background_color', 'black@0.5')
        margin = data.get('margin', 20)
        
        # 检查输入文件是否存在
        input_path = os.path.join(UPLOAD_FOLDER, input_file)
        if not os.path.exists(input_path):
            return jsonify({'error': '输入文件不存在'}), 400
        
        # 生成输出文件名
        output_filename = f"watermarked_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{input_file}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 添加水印
        success = video_processor.add_text_watermark(
            input_path, output_path, text, position,
            font_size, font_color, background_color, margin
        )
        
        if success:
            return jsonify({
                'message': '水印添加成功',
                'output_file': output_filename,
                'output_path': output_path
            }), 200
        else:
            return jsonify({'error': '水印添加失败'}), 500
            
    except Exception as e:
        logger.error(f"添加文字水印失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watermark/image', methods=['POST'])
def add_image_watermark():
    """添加图片水印"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['input_file', 'watermark_file']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必需参数: {field}'}), 400
        
        input_file = data['input_file']
        watermark_file = data['watermark_file']
        position = data.get('position', 'bottom-right')
        opacity = data.get('opacity', 0.7)
        scale = data.get('scale', 0.2)
        
        # 检查文件是否存在
        input_path = os.path.join(UPLOAD_FOLDER, input_file)
        watermark_path = os.path.join(UPLOAD_FOLDER, watermark_file)
        
        if not os.path.exists(input_path):
            return jsonify({'error': '输入文件不存在'}), 400
        if not os.path.exists(watermark_path):
            return jsonify({'error': '水印文件不存在'}), 400
        
        # 生成输出文件名
        output_filename = f"watermarked_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{input_file}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 添加水印
        success = video_processor.add_image_watermark(
            input_path, output_path, watermark_path, position, opacity, scale
        )
        
        if success:
            return jsonify({
                'message': '水印添加成功',
                'output_file': output_filename,
                'output_path': output_path
            }), 200
        else:
            return jsonify({'error': '水印添加失败'}), 500
            
    except Exception as e:
        logger.error(f"添加图片水印失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载处理后的文件"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def list_files():
    """列出所有文件"""
    try:
        input_files = []
        output_files = []
        
        # 列出输入文件
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_size = os.path.getsize(file_path)
                input_files.append({
                    'filename': filename,
                    'size': file_size,
                    'type': 'input'
                })
        
        # 列出输出文件
        for filename in os.listdir(OUTPUT_FOLDER):
            if allowed_file(filename):
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                file_size = os.path.getsize(file_path)
                output_files.append({
                    'filename': filename,
                    'size': file_size,
                    'type': 'output'
                })
        
        return jsonify({
            'input_files': input_files,
            'output_files': output_files
        }), 200
        
    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """获取服务状态"""
    try:
        return jsonify({
            'status': 'running',
            'upload_folder': UPLOAD_FOLDER,
            'output_folder': OUTPUT_FOLDER,
            'supported_formats': list(ALLOWED_EXTENSIONS),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 获取配置
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 启动视频水印服务: http://{host}:{port}")
    logger.info(f"📊 健康检查: http://{host}:{port}/health")
    logger.info(f"📁 上传目录: {UPLOAD_FOLDER}")
    logger.info(f"📁 输出目录: {OUTPUT_FOLDER}")
    
    app.run(host=host, port=port, debug=debug)