#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信服务Web管理界面
支持通过Web界面动态切换短信渠道、查看统计信息等
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import time
from datetime import datetime, timedelta
from sms_service import SMSManager, SMSProvider, SMSConfig
import threading

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 请修改为实际的密钥

# 全局短信管理器
sms_manager = None
stats_lock = threading.Lock()


def init_sms_manager():
    """初始化短信管理器"""
    global sms_manager
    sms_manager = SMSManager("sms_config.json")


@app.route('/')
def index():
    """首页 - 显示服务提供商状态"""
    if not sms_manager:
        init_sms_manager()
    
    status = sms_manager.get_provider_status()
    return render_template('index.html', providers=status)


@app.route('/api/status')
def api_status():
    """API: 获取服务提供商状态"""
    if not sms_manager:
        init_sms_manager()
    
    status = sms_manager.get_provider_status()
    return jsonify({
        'success': True,
        'data': status,
        'timestamp': time.time()
    })


@app.route('/api/send', methods=['POST'])
def api_send_sms():
    """API: 发送短信"""
    if not sms_manager:
        init_sms_manager()
    
    data = request.get_json()
    phone = data.get('phone')
    content = data.get('content')
    template_params = data.get('template_params', {})
    provider_name = data.get('provider_name')
    
    if not phone or not content:
        return jsonify({
            'success': False,
            'error': '手机号和内容不能为空'
        })
    
    # 发送短信
    result = sms_manager.send_sms(
        phone=phone,
        content=content,
        template_params=template_params,
        provider_name=provider_name
    )
    
    return jsonify({
        'success': result.success,
        'message_id': result.message_id,
        'error_code': result.error_code,
        'error_message': result.error_message,
        'provider': result.provider,
        'send_time': result.send_time
    })


@app.route('/api/switch', methods=['POST'])
def api_switch_provider():
    """API: 切换服务提供商状态"""
    if not sms_manager:
        init_sms_manager()
    
    data = request.get_json()
    provider_name = data.get('provider_name')
    enabled = data.get('enabled', True)
    
    if not provider_name:
        return jsonify({
            'success': False,
            'error': '服务提供商名称不能为空'
        })
    
    try:
        sms_manager.switch_provider(provider_name, enabled)
        return jsonify({
            'success': True,
            'message': f'服务提供商 {provider_name} 已{"启用" if enabled else "禁用"}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/stats')
def api_stats():
    """API: 获取统计信息"""
    if not sms_manager:
        init_sms_manager()
    
    with stats_lock:
        stats = {}
        for name, provider_stats in sms_manager.usage_stats.items():
            config = sms_manager.configs.get(name)
            stats[name] = {
                'provider': config.provider.value if config else 'unknown',
                'total_sent': provider_stats.get('total_sent', 0),
                'success_count': provider_stats.get('success_count', 0),
                'error_count': provider_stats.get('error_count', 0),
                'daily_sent': provider_stats.get('daily_sent', 0),
                'last_send_time': provider_stats.get('last_send_time'),
                'success_rate': provider_stats.get('success_count', 0) / max(provider_stats.get('total_sent', 1), 1),
                'daily_limit': config.daily_limit if config else None,
                'cost_per_sms': config.cost_per_sms if config else None
            }
    
    return jsonify({
        'success': True,
        'data': stats,
        'timestamp': time.time()
    })


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API: 获取或更新配置"""
    if not sms_manager:
        init_sms_manager()
    
    if request.method == 'GET':
        # 返回配置信息（隐藏敏感信息）
        config_data = {}
        for name, config in sms_manager.configs.items():
            config_data[name] = {
                'provider': config.provider.value,
                'sign_name': config.sign_name,
                'template_id': config.template_id,
                'endpoint': config.endpoint,
                'region': config.region,
                'enabled': config.enabled,
                'priority': config.priority,
                'daily_limit': config.daily_limit,
                'cost_per_sms': config.cost_per_sms,
                'access_key': config.access_key[:8] + '...' if config.access_key else '',
                'secret_key': '***' if config.secret_key else ''
            }
        
        return jsonify({
            'success': True,
            'data': config_data
        })
    
    elif request.method == 'POST':
        # 更新配置
        data = request.get_json()
        provider_name = data.get('provider_name')
        config_updates = data.get('config', {})
        
        if not provider_name or provider_name not in sms_manager.configs:
            return jsonify({
                'success': False,
                'error': '无效的服务提供商名称'
            })
        
        try:
            config = sms_manager.configs[provider_name]
            
            # 更新配置
            if 'enabled' in config_updates:
                config.enabled = config_updates['enabled']
            if 'priority' in config_updates:
                config.priority = config_updates['priority']
            if 'daily_limit' in config_updates:
                config.daily_limit = config_updates['daily_limit']
            if 'cost_per_sms' in config_updates:
                config.cost_per_sms = config_updates['cost_per_sms']
            
            # 保存配置
            sms_manager.save_config()
            
            return jsonify({
                'success': True,
                'message': '配置已更新'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })


@app.route('/api/reset_stats', methods=['POST'])
def api_reset_stats():
    """API: 重置统计信息"""
    if not sms_manager:
        init_sms_manager()
    
    with stats_lock:
        for name in sms_manager.usage_stats:
            sms_manager.usage_stats[name] = {
                'total_sent': 0,
                'success_count': 0,
                'error_count': 0,
                'last_send_time': None,
                'daily_sent': 0,
                'last_reset_date': time.strftime("%Y-%m-%d")
            }
    
    return jsonify({
        'success': True,
        'message': '统计信息已重置'
    })


# 创建HTML模板
def create_templates():
    """创建HTML模板文件"""
    import os
    
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    
    # 创建基础模板
    base_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}短信服务管理{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .status-card { transition: all 0.3s ease; }
        .status-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .provider-enabled { border-left: 4px solid #28a745; }
        .provider-disabled { border-left: 4px solid #dc3545; }
        .stats-number { font-size: 1.5rem; font-weight: bold; }
        .success-rate { color: #28a745; }
        .error-rate { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-chat-dots"></i> 短信服务管理
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">状态监控</a>
                <a class="nav-link" href="/send">发送短信</a>
                <a class="nav-link" href="/config">配置管理</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    # 创建首页模板
    index_template = '''{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h2><i class="bi bi-activity"></i> 服务提供商状态</h2>
        <p class="text-muted">实时监控各短信服务提供商的状态和统计信息</p>
    </div>
</div>

<div class="row" id="providers-container">
    <!-- 服务提供商卡片将通过JavaScript动态加载 -->
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="bi bi-graph-up"></i> 实时统计</h5>
                <button class="btn btn-sm btn-outline-primary" onclick="refreshStats()">
                    <i class="bi bi-arrow-clockwise"></i> 刷新
                </button>
            </div>
            <div class="card-body">
                <div class="row" id="stats-container">
                    <!-- 统计信息将通过JavaScript动态加载 -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let refreshInterval;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadProviders();
    loadStats();
    
    // 每30秒自动刷新
    refreshInterval = setInterval(function() {
        loadProviders();
        loadStats();
    }, 30000);
});

// 加载服务提供商状态
async function loadProviders() {
    try {
        const response = await axios.get('/api/status');
        if (response.data.success) {
            displayProviders(response.data.data);
        }
    } catch (error) {
        console.error('加载服务提供商状态失败:', error);
    }
}

// 显示服务提供商状态
function displayProviders(providers) {
    const container = document.getElementById('providers-container');
    container.innerHTML = '';
    
    for (const [name, info] of Object.entries(providers)) {
        const card = createProviderCard(name, info);
        container.appendChild(card);
    }
}

// 创建服务提供商卡片
function createProviderCard(name, info) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-3';
    
    const statusClass = info.enabled ? 'provider-enabled' : 'provider-disabled';
    const statusText = info.enabled ? '启用' : '禁用';
    const statusIcon = info.enabled ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger';
    
    col.innerHTML = `
        <div class="card status-card ${statusClass}">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-0">${name}</h6>
                    <span class="badge bg-${info.enabled ? 'success' : 'danger'}">
                        <i class="bi ${statusIcon}"></i> ${statusText}
                    </span>
                </div>
                <p class="text-muted small mb-2">${info.provider}</p>
                
                <div class="row text-center">
                    <div class="col-4">
                        <div class="stats-number text-primary">${info.total_sent}</div>
                        <small class="text-muted">总发送</small>
                    </div>
                    <div class="col-4">
                        <div class="stats-number ${info.success_rate > 0.8 ? 'success-rate' : 'error-rate'}">
                            ${(info.success_rate * 100).toFixed(1)}%
                        </div>
                        <small class="text-muted">成功率</small>
                    </div>
                    <div class="col-4">
                        <div class="stats-number text-info">${info.daily_sent}</div>
                        <small class="text-muted">今日发送</small>
                    </div>
                </div>
                
                <div class="mt-3">
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">优先级: ${info.priority}</small>
                        <small class="text-muted">余额: ¥${info.balance.toFixed(2)}</small>
                    </div>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">每日限制: ${info.daily_limit || '无'}</small>
                        <button class="btn btn-sm btn-outline-${info.enabled ? 'danger' : 'success'}" 
                                onclick="toggleProvider('${name}', ${!info.enabled})">
                            ${info.enabled ? '禁用' : '启用'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

// 切换服务提供商状态
async function toggleProvider(name, enabled) {
    try {
        const response = await axios.post('/api/switch', {
            provider_name: name,
            enabled: enabled
        });
        
        if (response.data.success) {
            showAlert('success', response.data.message);
            loadProviders();
        } else {
            showAlert('danger', response.data.error);
        }
    } catch (error) {
        showAlert('danger', '操作失败: ' + error.message);
    }
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await axios.get('/api/stats');
        if (response.data.success) {
            displayStats(response.data.data);
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

// 显示统计信息
function displayStats(stats) {
    const container = document.getElementById('stats-container');
    container.innerHTML = '';
    
    for (const [name, info] of Object.entries(stats)) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-3 mb-3';
        
        col.innerHTML = `
            <div class="card text-center">
                <div class="card-body">
                    <h6 class="card-title">${name}</h6>
                    <div class="stats-number text-primary">${info.total_sent}</div>
                    <small class="text-muted">总发送量</small>
                    <div class="mt-2">
                        <span class="badge bg-success">成功 ${info.success_count}</span>
                        <span class="badge bg-danger">失败 ${info.error_count}</span>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    }
}

// 刷新统计信息
function refreshStats() {
    loadProviders();
    loadStats();
}

// 显示提示信息
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 3秒后自动消失
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// 页面卸载时清除定时器
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
</script>
{% endblock %}'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)


if __name__ == '__main__':
    # 创建模板文件
    create_templates()
    
    # 初始化短信管理器
    init_sms_manager()
    
    print("短信服务Web管理界面启动中...")
    print("访问地址: http://localhost:5000")
    print("功能包括:")
    print("  - 实时监控服务提供商状态")
    print("  - 动态切换服务提供商")
    print("  - 查看发送统计信息")
    print("  - 配置管理")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)