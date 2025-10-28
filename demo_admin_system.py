#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示后台管理系统 - 展示AOP操作日志记录功能
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# 导入AOP操作日志系统
from aop_operation_logger import (
    operation_log, log_create, log_update, log_delete, log_read,
    log_login, log_logout, log_system, log_config,
    OperationType, OperationStatus, log_operation_manually
)
from operation_log_service import get_operation_log_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'demo_secret_key_2024'
CORS(app)

# 模拟数据库
users_db = {}
config_db = {}
system_logs = []

# 初始化操作日志服务
try:
    operation_log_service = get_operation_log_service()
    logger.info("✅ 操作日志服务初始化成功")
except Exception as e:
    logger.error(f"❌ 操作日志服务初始化失败: {e}")
    operation_log_service = None

class User:
    """用户模型"""
    def __init__(self, user_id, username, email, role='user'):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = datetime.now()
        self.last_login = None
        self.is_active = True

class Config:
    """配置模型"""
    def __init__(self, config_id, key, value, description=''):
        self.config_id = config_id
        self.key = key
        self.value = value
        self.description = description
        self.updated_at = datetime.now()
        self.updated_by = None

# 初始化一些示例数据
def init_demo_data():
    """初始化演示数据"""
    # 创建管理员用户
    admin_user = User('admin_001', 'admin', 'admin@demo.com', 'admin')
    users_db['admin_001'] = admin_user
    
    # 创建普通用户
    user1 = User('user_001', 'user1', 'user1@demo.com', 'user')
    user2 = User('user_002', 'user2', 'user2@demo.com', 'user')
    users_db['user_001'] = user1
    users_db['user_002'] = user2
    
    # 创建配置项
    configs = [
        Config('config_001', 'site_name', '演示管理系统', '网站名称'),
        Config('config_002', 'max_users', '1000', '最大用户数'),
        Config('config_003', 'enable_registration', 'true', '是否允许注册'),
        Config('config_004', 'maintenance_mode', 'false', '维护模式')
    ]
    
    for config in configs:
        config_db[config.config_id] = config

# 用户认证装饰器
def require_auth(f):
    """需要认证的装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        if not user_id or user_id not in users_db:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前用户"""
    user_id = request.cookies.get('user_id')
    return users_db.get(user_id)

# 路由定义
@app.route('/')
def index():
    """首页"""
    return render_template('demo_admin/index.html')

@app.route('/login', methods=['GET', 'POST'])
@log_login("用户登录", "用户登录系统")
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的认证逻辑
        if username == 'admin' and password == 'admin123':
            user = users_db['admin_001']
            user.last_login = datetime.now()
            
            response = redirect(url_for('dashboard'))
            response.set_cookie('user_id', user.user_id)
            return response
        elif username == 'user1' and password == 'user123':
            user = users_db['user_001']
            user.last_login = datetime.now()
            
            response = redirect(url_for('dashboard'))
            response.set_cookie('user_id', user.user_id)
            return response
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('demo_admin/login.html')

@app.route('/logout')
@log_logout("用户登出", "用户登出系统")
def logout():
    """用户登出"""
    response = redirect(url_for('login'))
    response.set_cookie('user_id', '', expires=0)
    return response

@app.route('/dashboard')
@require_auth
@log_read("仪表板访问", "访问系统仪表板")
def dashboard():
    """仪表板"""
    user = get_current_user()
    
    # 获取统计数据
    stats = {
        'total_users': len(users_db),
        'total_configs': len(config_db),
        'recent_logs': system_logs[-10:] if system_logs else []
    }
    
    return render_template('demo_admin/dashboard.html', user=user, stats=stats)

@app.route('/users')
@require_auth
@log_read("用户列表查询", "查询用户列表")
def users():
    """用户管理页面"""
    user = get_current_user()
    return render_template('demo_admin/users.html', user=user, users=list(users_db.values()))

@app.route('/users/create', methods=['GET', 'POST'])
@require_auth
@log_create("用户创建", "创建新用户")
def create_user():
    """创建用户"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'user')
        
        # 检查用户名是否已存在
        if any(u.username == username for u in users_db.values()):
            flash('用户名已存在', 'error')
            return render_template('demo_admin/create_user.html')
        
        # 创建新用户
        user_id = f'user_{len(users_db) + 1:03d}'
        new_user = User(user_id, username, email, role)
        users_db[user_id] = new_user
        
        flash('用户创建成功', 'success')
        return redirect(url_for('users'))
    
    return render_template('demo_admin/create_user.html')

@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@require_auth
@log_update("用户信息更新", "更新用户信息")
def edit_user(user_id):
    """编辑用户"""
    if user_id not in users_db:
        flash('用户不存在', 'error')
        return redirect(url_for('users'))
    
    user = users_db[user_id]
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        user.is_active = request.form.get('is_active') == 'on'
        
        flash('用户信息更新成功', 'success')
        return redirect(url_for('users'))
    
    return render_template('demo_admin/edit_user.html', user=user)

@app.route('/users/<user_id>/delete', methods=['POST'])
@require_auth
@log_delete("用户删除", "删除用户")
def delete_user(user_id):
    """删除用户"""
    if user_id not in users_db:
        flash('用户不存在', 'error')
        return redirect(url_for('users'))
    
    # 不能删除自己
    current_user = get_current_user()
    if user_id == current_user.user_id:
        flash('不能删除自己', 'error')
        return redirect(url_for('users'))
    
    del users_db[user_id]
    flash('用户删除成功', 'success')
    return redirect(url_for('users'))

@app.route('/configs')
@require_auth
@log_read("配置列表查询", "查询系统配置列表")
def configs():
    """配置管理页面"""
    user = get_current_user()
    return render_template('demo_admin/configs.html', user=user, configs=list(config_db.values()))

@app.route('/configs/<config_id>/edit', methods=['GET', 'POST'])
@require_auth
@log_config("配置更新", "更新系统配置")
def edit_config(config_id):
    """编辑配置"""
    if config_id not in config_db:
        flash('配置不存在', 'error')
        return redirect(url_for('configs'))
    
    config = config_db[config_id]
    
    if request.method == 'POST':
        old_value = config.value
        config.value = request.form.get('value')
        config.description = request.form.get('description')
        config.updated_at = datetime.now()
        config.updated_by = get_current_user().user_id
        
        # 记录配置变更
        log_operation_manually(
            operation_type=OperationType.CONFIG,
            operation_name="配置值更新",
            description=f"配置项 {config.key} 从 '{old_value}' 更新为 '{config.value}'",
            user_id=get_current_user().user_id,
            username=get_current_user().username,
            status=OperationStatus.SUCCESS
        )
        
        flash('配置更新成功', 'success')
        return redirect(url_for('configs'))
    
    return render_template('demo_admin/edit_config.html', config=config)

@app.route('/system/logs')
@require_auth
@log_read("系统日志查询", "查询系统操作日志")
def system_logs_page():
    """系统日志页面"""
    user = get_current_user()
    
    # 获取操作日志
    operation_logs = []
    if operation_log_service:
        try:
            operation_logs = operation_log_service.get_recent_logs(hours=24, limit=50)
        except Exception as e:
            logger.error(f"获取操作日志失败: {e}")
    
    return render_template('demo_admin/system_logs.html', 
                         user=user, 
                         logs=operation_logs)

@app.route('/api/users', methods=['GET'])
@require_auth
@log_read("用户数据API", "通过API获取用户数据")
def api_users():
    """用户数据API"""
    users_data = []
    for user in users_db.values():
        users_data.append({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    
    return jsonify({
        'success': True,
        'data': users_data
    })

@app.route('/api/configs', methods=['GET'])
@require_auth
@log_read("配置数据API", "通过API获取配置数据")
def api_configs():
    """配置数据API"""
    configs_data = []
    for config in config_db.values():
        configs_data.append({
            'config_id': config.config_id,
            'key': config.key,
            'value': config.value,
            'description': config.description,
            'updated_at': config.updated_at.isoformat(),
            'updated_by': config.updated_by
        })
    
    return jsonify({
        'success': True,
        'data': configs_data
    })

@app.route('/api/operation-logs', methods=['GET'])
@require_auth
@log_read("操作日志API", "通过API获取操作日志")
def api_operation_logs():
    """操作日志API"""
    if not operation_log_service:
        return jsonify({
            'success': False,
            'error': 'Operation log service not available'
        }), 500
    
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        operation_type = request.args.get('operation_type')
        status = request.args.get('status')
        
        logs = operation_log_service.get_logs(
            operation_type=operation_type,
            status=status,
            limit=limit,
            offset=(page - 1) * limit
        )
        
        return jsonify({
            'success': True,
            'data': logs
        })
    except Exception as e:
        logger.error(f"获取操作日志失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/operation-logs/statistics', methods=['GET'])
@require_auth
@log_read("操作日志统计API", "通过API获取操作日志统计")
def api_operation_log_statistics():
    """操作日志统计API"""
    if not operation_log_service:
        return jsonify({
            'success': False,
            'error': 'Operation log service not available'
        }), 500
    
    try:
        days = int(request.args.get('days', 7))
        stats = operation_log_service.get_statistics(
            start_date=datetime.now() - timedelta(days=days),
            end_date=datetime.now()
        )
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取操作日志统计失败: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# 创建模板目录和文件
def create_templates():
    """创建HTML模板"""
    template_dir = "templates/demo_admin"
    os.makedirs(template_dir, exist_ok=True)
    
    # 基础模板
    base_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}演示管理系统{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; }
        .log-entry { border-left: 4px solid #dee2e6; }
        .log-entry.success { border-left-color: #28a745; }
        .log-entry.failed { border-left-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
                <div class="position-sticky pt-3">
                    <div class="text-center mb-3">
                        <h5>演示管理系统</h5>
                        <small class="text-muted">AOP操作日志演示</small>
                    </div>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">
                                <i class="bi bi-speedometer2"></i> 仪表板
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('users') }}">
                                <i class="bi bi-people"></i> 用户管理
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('configs') }}">
                                <i class="bi bi-gear"></i> 配置管理
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('system_logs_page') }}">
                                <i class="bi bi-journal-text"></i> 操作日志
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">
                                <i class="bi bi-box-arrow-right"></i> 退出登录
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, "base.html"), 'w', encoding='utf-8') as f:
        f.write(base_html)
    
    # 登录页面
    login_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - 演示管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card mt-5">
                    <div class="card-body">
                        <h3 class="card-title text-center mb-4">演示管理系统</h3>
                        <p class="text-center text-muted mb-4">AOP操作日志记录演示</p>
                        
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                                        {{ message }}
                                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                    </div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label for="username" class="form-label">用户名</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">密码</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">登录</button>
                        </form>
                        
                        <div class="mt-4">
                            <h6>演示账号：</h6>
                            <ul class="list-unstyled">
                                <li><strong>管理员：</strong> admin / admin123</li>
                                <li><strong>普通用户：</strong> user1 / user123</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    with open(os.path.join(template_dir, "login.html"), 'w', encoding='utf-8') as f:
        f.write(login_html)
    
    # 仪表板页面
    dashboard_html = '''{% extends "base.html" %}
{% block title %}仪表板 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">仪表板</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary">刷新</button>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">总用户数</h5>
                <h2 class="text-primary">{{ stats.total_users }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">配置项数</h5>
                <h2 class="text-success">{{ stats.total_configs }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">系统日志</h5>
                <h2 class="text-info">{{ stats.recent_logs|length }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">当前用户</h5>
                <h2 class="text-warning">{{ user.username }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">欢迎使用演示管理系统</h5>
            </div>
            <div class="card-body">
                <p>这是一个演示AOP操作日志记录功能的后台管理系统。</p>
                <p>您可以尝试以下操作来查看操作日志记录：</p>
                <ul>
                    <li>用户管理 - 创建、编辑、删除用户</li>
                    <li>配置管理 - 修改系统配置</li>
                    <li>查看操作日志 - 查看所有操作记录</li>
                </ul>
                <p class="text-muted">所有操作都会自动记录到操作日志中，您可以在"操作日志"页面查看详细信息。</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "dashboard.html"), 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    # 用户管理页面
    users_html = '''{% extends "base.html" %}
{% block title %}用户管理 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">用户管理</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <a href="{{ url_for('create_user') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> 创建用户
        </a>
    </div>
</div>

<div class="table-responsive">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>最后登录</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>
                    <span class="badge bg-{{ 'primary' if user.role == 'admin' else 'secondary' }}">
                        {{ user.role }}
                    </span>
                </td>
                <td>
                    <span class="badge bg-{{ 'success' if user.is_active else 'danger' }}">
                        {{ '活跃' if user.is_active else '禁用' }}
                    </span>
                </td>
                <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td>{{ user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '从未登录' }}</td>
                <td>
                    <a href="{{ url_for('edit_user', user_id=user.user_id) }}" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-pencil"></i> 编辑
                    </a>
                    {% if user.user_id != session.get('user_id') %}
                    <form method="POST" action="{{ url_for('delete_user', user_id=user.user_id) }}" class="d-inline" onsubmit="return confirm('确定要删除这个用户吗？')">
                        <button type="submit" class="btn btn-sm btn-outline-danger">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "users.html"), 'w', encoding='utf-8') as f:
        f.write(users_html)
    
    # 创建用户页面
    create_user_html = '''{% extends "base.html" %}
{% block title %}创建用户 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">创建用户</h1>
    <a href="{{ url_for('users') }}" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left"></i> 返回
    </a>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">用户名</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">邮箱</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="role" class="form-label">角色</label>
                        <select class="form-select" id="role" name="role">
                            <option value="user">普通用户</option>
                            <option value="admin">管理员</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">创建用户</button>
                    <a href="{{ url_for('users') }}" class="btn btn-secondary">取消</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "create_user.html"), 'w', encoding='utf-8') as f:
        f.write(create_user_html)
    
    # 编辑用户页面
    edit_user_html = '''{% extends "base.html" %}
{% block title %}编辑用户 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">编辑用户</h1>
    <a href="{{ url_for('users') }}" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left"></i> 返回
    </a>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">用户名</label>
                        <input type="text" class="form-control" id="username" value="{{ user.username }}" disabled>
                        <div class="form-text">用户名不可修改</div>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">邮箱</label>
                        <input type="email" class="form-control" id="email" name="email" value="{{ user.email }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="role" class="form-label">角色</label>
                        <select class="form-select" id="role" name="role">
                            <option value="user" {{ 'selected' if user.role == 'user' else '' }}>普通用户</option>
                            <option value="admin" {{ 'selected' if user.role == 'admin' else '' }}>管理员</option>
                        </select>
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="is_active" name="is_active" {{ 'checked' if user.is_active else '' }}>
                        <label class="form-check-label" for="is_active">启用用户</label>
                    </div>
                    <button type="submit" class="btn btn-primary">更新用户</button>
                    <a href="{{ url_for('users') }}" class="btn btn-secondary">取消</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "edit_user.html"), 'w', encoding='utf-8') as f:
        f.write(edit_user_html)
    
    # 配置管理页面
    configs_html = '''{% extends "base.html" %}
{% block title %}配置管理 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">配置管理</h1>
</div>

<div class="table-responsive">
    <table class="table table-striped">
        <thead>
            <tr>
                <th>配置键</th>
                <th>配置值</th>
                <th>描述</th>
                <th>更新时间</th>
                <th>更新人</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            {% for config in configs %}
            <tr>
                <td><code>{{ config.key }}</code></td>
                <td>{{ config.value }}</td>
                <td>{{ config.description }}</td>
                <td>{{ config.updated_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td>{{ config.updated_by or '系统' }}</td>
                <td>
                    <a href="{{ url_for('edit_config', config_id=config.config_id) }}" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-pencil"></i> 编辑
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "configs.html"), 'w', encoding='utf-8') as f:
        f.write(configs_html)
    
    # 编辑配置页面
    edit_config_html = '''{% extends "base.html" %}
{% block title %}编辑配置 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">编辑配置</h1>
    <a href="{{ url_for('configs') }}" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left"></i> 返回
    </a>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="key" class="form-label">配置键</label>
                        <input type="text" class="form-control" id="key" value="{{ config.key }}" disabled>
                        <div class="form-text">配置键不可修改</div>
                    </div>
                    <div class="mb-3">
                        <label for="value" class="form-label">配置值</label>
                        <input type="text" class="form-control" id="value" name="value" value="{{ config.value }}" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">描述</label>
                        <textarea class="form-control" id="description" name="description" rows="3">{{ config.description }}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">更新配置</button>
                    <a href="{{ url_for('configs') }}" class="btn btn-secondary">取消</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(os.path.join(template_dir, "edit_config.html"), 'w', encoding='utf-8') as f:
        f.write(edit_config_html)
    
    # 系统日志页面
    system_logs_html = '''{% extends "base.html" %}
{% block title %}操作日志 - 演示管理系统{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">操作日志</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button class="btn btn-sm btn-outline-secondary" onclick="refreshLogs()">
            <i class="bi bi-arrow-clockwise"></i> 刷新
        </button>
    </div>
</div>

<div id="logsContainer">
    {% if logs %}
        {% for log in logs %}
        <div class="log-entry {{ log.status }} p-3 mb-3 bg-light rounded">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-2">
                        <h6 class="mb-0 me-3">{{ log.operation_name or '未知操作' }}</h6>
                        <span class="badge bg-{{ 'success' if log.status == 'success' else 'danger' }}">
                            {{ '成功' if log.status == 'success' else '失败' }}
                        </span>
                        <span class="badge bg-secondary ms-2">{{ log.operation_type or '' }}</span>
                    </div>
                    <p class="mb-2 text-muted">{{ log.description or '' }}</p>
                    <div class="text-muted small">
                        <i class="bi bi-person"></i> {{ log.username or '系统' }} |
                        <i class="bi bi-folder"></i> {{ log.module_name or '' }} |
                        <i class="bi bi-clock"></i> {{ log.timestamp[:19].replace('T', ' ') }} |
                        <i class="bi bi-stopwatch"></i> {{ log.execution_time or 0 }}ms
                        {% if log.ip_address %}
                        | <i class="bi bi-geo-alt"></i> {{ log.ip_address }}
                        {% endif %}
                    </div>
                    {% if log.error_message %}
                    <div class="alert alert-danger mt-2 mb-0">
                        <small>{{ log.error_message }}</small>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="text-center text-muted">
            <i class="bi bi-journal-text" style="font-size: 3rem;"></i>
            <p class="mt-3">暂无操作日志</p>
        </div>
    {% endif %}
</div>
{% endblock %}

<script>
function refreshLogs() {
    location.reload();
}
</script>'''
    
    with open(os.path.join(template_dir, "system_logs.html"), 'w', encoding='utf-8') as f:
        f.write(system_logs_html)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='演示后台管理系统 - AOP操作日志记录')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5002, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    try:
        # 创建模板
        create_templates()
        
        # 初始化演示数据
        init_demo_data()
        
        logger.info("✅ 演示管理系统初始化成功")
        logger.info(f"🚀 启动演示管理系统: http://{args.host}:{args.port}")
        logger.info("📋 演示账号:")
        logger.info("   管理员: admin / admin123")
        logger.info("   普通用户: user1 / user123")
        
        app.run(host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()