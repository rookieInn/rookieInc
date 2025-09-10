#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS存储监控Web仪表板
提供Web界面查看存储监控数据和趋势图表
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Web框架
try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_cors import CORS
except ImportError:
    print("请安装Flask库: pip install flask flask-cors")
    sys.exit(1)

# 数据处理和可视化
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import base64
    from io import BytesIO
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except ImportError:
    print("请安装数据处理库: pip install pandas matplotlib")
    sys.exit(1)

# 导入监控器
from oss_storage_monitor import OSSStorageMonitor


class OSSMonitorDashboard:
    """OSS监控Web仪表板"""
    
    def __init__(self, config_file: str = "oss_monitor_config.json"):
        """初始化仪表板"""
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.monitor = OSSStorageMonitor(config_file)
        self.db_path = self.monitor.db_path
        
        # 设置路由
        self._setup_routes()
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _setup_routes(self):
        """设置Web路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/buckets')
        def get_buckets():
            """获取桶列表"""
            try:
                buckets = self.monitor.config.get('buckets', [])
                bucket_list = []
                
                for bucket in buckets:
                    # 获取最新统计信息
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT total_size_bytes, object_count, check_time, daily_increase_bytes
                        FROM storage_stats 
                        WHERE bucket_name = ?
                        ORDER BY check_time DESC LIMIT 1
                    ''', (bucket['name'],))
                    
                    result = cursor.fetchone()
                    conn.close()
                    
                    bucket_info = {
                        'name': bucket['name'],
                        'endpoint': bucket['endpoint'],
                        'description': bucket.get('description', ''),
                        'total_size_gb': 0,
                        'object_count': 0,
                        'daily_increase_gb': 0,
                        'last_check': None
                    }
                    
                    if result:
                        bucket_info.update({
                            'total_size_gb': round(result[0] / (1024**3), 2),
                            'object_count': result[1],
                            'daily_increase_gb': round(result[3] / (1024**3), 2),
                            'last_check': result[2]
                        })
                    
                    bucket_list.append(bucket_info)
                
                return jsonify(bucket_list)
                
            except Exception as e:
                logging.error(f"获取桶列表失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats/<bucket_name>')
        def get_bucket_stats(bucket_name):
            """获取指定桶的统计信息"""
            try:
                days = request.args.get('days', 30, type=int)
                df = self.monitor.get_storage_history(bucket_name, days)
                
                if df.empty:
                    return jsonify({'error': '没有找到数据'}), 404
                
                # 转换为JSON格式
                stats = []
                for _, row in df.iterrows():
                    stats.append({
                        'date': row['check_time'].strftime('%Y-%m-%d'),
                        'total_size_gb': round(row['total_size_gb'], 2),
                        'daily_increase_gb': round(row['daily_increase_gb'], 2),
                        'object_count': int(row['object_count'])
                    })
                
                return jsonify(stats)
                
            except Exception as e:
                logging.error(f"获取桶统计信息失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/summary')
        def get_summary():
            """获取总体摘要信息"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 获取所有桶的最新数据
                cursor.execute('''
                    SELECT bucket_name, total_size_bytes, object_count, daily_increase_bytes, check_time
                    FROM storage_stats s1
                    WHERE check_time = (
                        SELECT MAX(check_time) 
                        FROM storage_stats s2 
                        WHERE s2.bucket_name = s1.bucket_name
                    )
                ''')
                
                results = cursor.fetchall()
                conn.close()
                
                total_size_gb = sum(row[1] for row in results) / (1024**3)
                total_objects = sum(row[2] for row in results)
                total_daily_increase_gb = sum(row[3] for row in results) / (1024**3)
                
                # 计算平均每日新增
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT AVG(daily_increase_bytes) FROM storage_stats 
                    WHERE check_time >= ?
                ''', (datetime.now() - timedelta(days=7),))
                
                avg_daily_increase = cursor.fetchone()[0] or 0
                conn.close()
                
                summary = {
                    'total_buckets': len(results),
                    'total_size_gb': round(total_size_gb, 2),
                    'total_objects': total_objects,
                    'total_daily_increase_gb': round(total_daily_increase_gb, 2),
                    'avg_daily_increase_gb': round(avg_daily_increase / (1024**3), 2),
                    'last_update': max(row[4] for row in results) if results else None
                }
                
                return jsonify(summary)
                
            except Exception as e:
                logging.error(f"获取摘要信息失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chart/<bucket_name>')
        def get_bucket_chart(bucket_name):
            """获取桶的图表数据"""
            try:
                days = request.args.get('days', 30, type=int)
                chart_type = request.args.get('type', 'trend')  # trend, daily
                
                df = self.monitor.get_storage_history(bucket_name, days)
                
                if df.empty:
                    return jsonify({'error': '没有找到数据'}), 404
                
                # 生成图表
                fig, ax = plt.subplots(figsize=(10, 6))
                
                if chart_type == 'trend':
                    ax.plot(df['check_time'], df['total_size_gb'], 
                           marker='o', linewidth=2, markersize=4)
                    ax.set_title(f'{bucket_name} - 存储量趋势', fontsize=14, fontweight='bold')
                    ax.set_ylabel('存储量 (GB)', fontsize=12)
                else:  # daily
                    ax.bar(df['check_time'], df['daily_increase_gb'], 
                          alpha=0.7, color='orange')
                    ax.set_title(f'{bucket_name} - 每日新增存储量', fontsize=14, fontweight='bold')
                    ax.set_ylabel('新增存储量 (GB)', fontsize=12)
                
                ax.set_xlabel('日期', fontsize=12)
                ax.grid(True, alpha=0.3)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                
                # 转换为base64图片
                img_buffer = BytesIO()
                plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plt.close()
                
                return jsonify({'image': f'data:image/png;base64,{img_base64}'})
                
            except Exception as e:
                logging.error(f"生成图表失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/check', methods=['POST'])
        def trigger_check():
            """触发存储检查"""
            try:
                self.monitor.check_all_buckets()
                return jsonify({'message': '存储检查已触发'})
            except Exception as e:
                logging.error(f"触发存储检查失败: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/report', methods=['POST'])
        def generate_report():
            """生成报告"""
            try:
                data = request.get_json()
                bucket_name = data.get('bucket_name')
                days = data.get('days', 30)
                
                self.monitor.generate_storage_report(bucket_name, days)
                return jsonify({'message': '报告已生成'})
            except Exception as e:
                logging.error(f"生成报告失败: {e}")
                return jsonify({'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web服务器"""
        logging.info(f"启动OSS监控仪表板: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_html_template():
    """创建HTML模板文件"""
    template_dir = Path("templates")
    template_dir.mkdir(exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSS存储监控仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .card h3 {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .card .unit {
            color: #999;
            font-size: 0.8rem;
        }
        
        .buckets-section {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .buckets-section h2 {
            margin-bottom: 1.5rem;
            color: #333;
        }
        
        .buckets-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .bucket-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            transition: all 0.2s;
        }
        
        .bucket-card:hover {
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        }
        
        .bucket-name {
            font-weight: bold;
            font-size: 1.1rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .bucket-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
        }
        
        .stat-label {
            color: #666;
        }
        
        .stat-value {
            font-weight: bold;
            color: #333;
        }
        
        .chart-section {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .chart-controls {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            align-items: center;
        }
        
        .chart-controls select, .chart-controls button {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: white;
        }
        
        .chart-controls button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
        }
        
        .chart-controls button:hover {
            background: #5a6fd8;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        
        .error {
            color: #e74c3c;
            background: #fdf2f2;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .actions {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>OSS存储监控仪表板</h1>
        <p>实时监控阿里云OSS存储使用情况和趋势</p>
    </div>
    
    <div class="container">
        <div class="actions">
            <button class="btn btn-primary" onclick="triggerCheck()">立即检查</button>
            <button class="btn btn-secondary" onclick="generateReport()">生成报告</button>
            <button class="btn btn-secondary" onclick="refreshData()">刷新数据</button>
        </div>
        
        <div class="summary-cards" id="summaryCards">
            <div class="loading">加载中...</div>
        </div>
        
        <div class="buckets-section">
            <h2>桶概览</h2>
            <div class="buckets-grid" id="bucketsGrid">
                <div class="loading">加载中...</div>
            </div>
        </div>
        
        <div class="chart-section">
            <h2>存储趋势</h2>
            <div class="chart-controls">
                <select id="bucketSelect">
                    <option value="">选择桶...</option>
                </select>
                <select id="daysSelect">
                    <option value="7">最近7天</option>
                    <option value="30" selected>最近30天</option>
                    <option value="90">最近90天</option>
                </select>
                <select id="chartTypeSelect">
                    <option value="trend">存储量趋势</option>
                    <option value="daily">每日新增</option>
                </select>
                <button onclick="updateChart()">更新图表</button>
            </div>
            <div class="chart-container">
                <canvas id="storageChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let chart = null;
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadSummary();
            loadBuckets();
            loadBucketOptions();
        });
        
        // 加载摘要信息
        async function loadSummary() {
            try {
                const response = await fetch('/api/summary');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                const summaryCards = document.getElementById('summaryCards');
                summaryCards.innerHTML = `
                    <div class="card">
                        <h3>总桶数</h3>
                        <div class="value">${data.total_buckets}</div>
                        <div class="unit">个</div>
                    </div>
                    <div class="card">
                        <h3>总存储量</h3>
                        <div class="value">${data.total_size_gb}</div>
                        <div class="unit">GB</div>
                    </div>
                    <div class="card">
                        <h3>总对象数</h3>
                        <div class="value">${data.total_objects.toLocaleString()}</div>
                        <div class="unit">个</div>
                    </div>
                    <div class="card">
                        <h3>今日新增</h3>
                        <div class="value">${data.total_daily_increase_gb}</div>
                        <div class="unit">GB</div>
                    </div>
                    <div class="card">
                        <h3>平均每日新增</h3>
                        <div class="value">${data.avg_daily_increase_gb}</div>
                        <div class="unit">GB/天</div>
                    </div>
                `;
            } catch (error) {
                document.getElementById('summaryCards').innerHTML = 
                    `<div class="error">加载摘要信息失败: ${error.message}</div>`;
            }
        }
        
        // 加载桶列表
        async function loadBuckets() {
            try {
                const response = await fetch('/api/buckets');
                const buckets = await response.json();
                
                if (buckets.error) {
                    throw new Error(buckets.error);
                }
                
                const bucketsGrid = document.getElementById('bucketsGrid');
                bucketsGrid.innerHTML = buckets.map(bucket => `
                    <div class="bucket-card">
                        <div class="bucket-name">${bucket.name}</div>
                        <div class="bucket-stats">
                            <div class="stat-item">
                                <span class="stat-label">存储量:</span>
                                <span class="stat-value">${bucket.total_size_gb} GB</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">对象数:</span>
                                <span class="stat-value">${bucket.object_count.toLocaleString()}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">今日新增:</span>
                                <span class="stat-value">${bucket.daily_increase_gb} GB</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">最后检查:</span>
                                <span class="stat-value">${bucket.last_check ? new Date(bucket.last_check).toLocaleString() : 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                document.getElementById('bucketsGrid').innerHTML = 
                    `<div class="error">加载桶信息失败: ${error.message}</div>`;
            }
        }
        
        // 加载桶选择选项
        async function loadBucketOptions() {
            try {
                const response = await fetch('/api/buckets');
                const buckets = await response.json();
                
                if (buckets.error) {
                    throw new Error(buckets.error);
                }
                
                const bucketSelect = document.getElementById('bucketSelect');
                bucketSelect.innerHTML = '<option value="">选择桶...</option>' +
                    buckets.map(bucket => 
                        `<option value="${bucket.name}">${bucket.name}</option>`
                    ).join('');
            } catch (error) {
                console.error('加载桶选项失败:', error);
            }
        }
        
        // 更新图表
        async function updateChart() {
            const bucketName = document.getElementById('bucketSelect').value;
            const days = document.getElementById('daysSelect').value;
            const chartType = document.getElementById('chartTypeSelect').value;
            
            if (!bucketName) {
                alert('请选择一个桶');
                return;
            }
            
            try {
                const response = await fetch(`/api/chart/${bucketName}?days=${days}&type=${chartType}`);
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // 创建图片元素
                const img = new Image();
                img.onload = function() {
                    const canvas = document.getElementById('storageChart');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                };
                img.src = data.image;
                
            } catch (error) {
                console.error('更新图表失败:', error);
                alert('更新图表失败: ' + error.message);
            }
        }
        
        // 触发检查
        async function triggerCheck() {
            try {
                const response = await fetch('/api/check', { method: 'POST' });
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                alert('存储检查已触发');
                setTimeout(() => {
                    loadSummary();
                    loadBuckets();
                }, 2000);
            } catch (error) {
                alert('触发检查失败: ' + error.message);
            }
        }
        
        // 生成报告
        async function generateReport() {
            const bucketName = document.getElementById('bucketSelect').value;
            const days = document.getElementById('daysSelect').value;
            
            try {
                const response = await fetch('/api/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        bucket_name: bucketName || null,
                        days: parseInt(days)
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                alert('报告已生成');
            } catch (error) {
                alert('生成报告失败: ' + error.message);
            }
        }
        
        // 刷新数据
        function refreshData() {
            loadSummary();
            loadBuckets();
            loadBucketOptions();
        }
    </script>
</body>
</html>'''
    
    with open(template_dir / "dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OSS存储监控Web仪表板')
    parser.add_argument('--config', '-c', default='oss_monitor_config.json', 
                       help='配置文件路径')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, 
                       help='服务器端口')
    parser.add_argument('--debug', action='store_true', 
                       help='启用调试模式')
    
    args = parser.parse_args()
    
    try:
        # 创建HTML模板
        create_html_template()
        
        # 启动仪表板
        dashboard = OSSMonitorDashboard(args.config)
        dashboard.run(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logging.info("用户中断操作")
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()