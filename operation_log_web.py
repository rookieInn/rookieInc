#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志Web管理界面
提供操作日志的Web查看和管理功能
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

from operation_log_service import OperationLogService
from aop_operation_logger import OperationType, OperationStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OperationLogWebApp:
    """操作日志Web应用"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """初始化Web应用"""
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.service = OperationLogService(config_file)
        
        # 设置路由
        self._setup_routes()
        
        # 设置模板目录
        self._setup_templates()
        
        logger.info("✅ 操作日志Web应用初始化成功")
    
    def _setup_templates(self):
        """设置模板目录"""
        template_dir = "templates/operation_logs"
        os.makedirs(template_dir, exist_ok=True)
        
        # 创建基础模板
        self._create_base_template(template_dir)
        self._create_dashboard_template(template_dir)
        self._create_logs_template(template_dir)
        self._create_statistics_template(template_dir)
    
    def _create_base_template(self, template_dir: str):
        """创建基础模板"""
        base_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}操作日志管理{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .sidebar { min-height: 100vh; }
        .log-entry { border-left: 4px solid #dee2e6; }
        .log-entry.success { border-left-color: #28a745; }
        .log-entry.failed { border-left-color: #dc3545; }
        .log-details { font-size: 0.9rem; color: #6c757d; }
        .status-badge { font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
                <div class="position-sticky pt-3">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="/operation-logs/dashboard">
                                <i class="bi bi-speedometer2"></i> 仪表板
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/operation-logs/logs">
                                <i class="bi bi-list-ul"></i> 日志列表
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/operation-logs/statistics">
                                <i class="bi bi-bar-chart"></i> 统计分析
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/operation-logs/export">
                                <i class="bi bi-download"></i> 导出日志
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
        
        with open(os.path.join(template_dir, "base.html"), 'w', encoding='utf-8') as f:
            f.write(base_html)
    
    def _create_dashboard_template(self, template_dir: str):
        """创建仪表板模板"""
        dashboard_html = '''{% extends "base.html" %}
{% block title %}操作日志仪表板{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">操作日志仪表板</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button class="btn btn-sm btn-outline-secondary" onclick="refreshDashboard()">
            <i class="bi bi-arrow-clockwise"></i> 刷新
        </button>
    </div>
</div>

<!-- 统计卡片 -->
<div class="row mb-4">
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">总操作数</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800" id="totalLogs">-</div>
                    </div>
                    <div class="col-auto">
                        <i class="bi bi-list-ul fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">成功操作</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800" id="successLogs">-</div>
                    </div>
                    <div class="col-auto">
                        <i class="bi bi-check-circle fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-danger shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-danger text-uppercase mb-1">失败操作</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800" id="failedLogs">-</div>
                    </div>
                    <div class="col-auto">
                        <i class="bi bi-x-circle fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
                <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">错误率</div>
                        <div class="h5 mb-0 font-weight-bold text-gray-800" id="errorRate">-</div>
                    </div>
                    <div class="col-auto">
                        <i class="bi bi-exclamation-triangle fa-2x text-gray-300"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 图表区域 -->
<div class="row">
    <div class="col-xl-8 col-lg-7">
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">操作趋势</h6>
            </div>
            <div class="card-body">
                <div class="chart-area">
                    <canvas id="operationTrendChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    <div class="col-xl-4 col-lg-5">
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">操作类型分布</h6>
            </div>
            <div class="card-body">
                <div class="chart-pie pt-4 pb-2">
                    <canvas id="operationTypeChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 最近日志 -->
<div class="row">
    <div class="col-lg-12">
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">最近操作日志</h6>
            </div>
            <div class="card-body">
                <div id="recentLogs">
                    <div class="text-center">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let operationTrendChart, operationTypeChart;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

// 加载仪表板数据
async function loadDashboardData() {
    try {
        const response = await fetch('/api/operation-logs/dashboard');
        const data = await response.json();
        
        if (data.success) {
            updateSummaryCards(data.data.summary);
            updateRecentLogs(data.data.recent_logs);
            updateCharts(data.data);
        } else {
            console.error('加载仪表板数据失败:', data.error);
        }
    } catch (error) {
        console.error('加载仪表板数据失败:', error);
    }
}

// 更新统计卡片
function updateSummaryCards(summary) {
    document.getElementById('totalLogs').textContent = summary.total_logs || 0;
    document.getElementById('successLogs').textContent = summary.success_logs || 0;
    document.getElementById('failedLogs').textContent = summary.failed_logs || 0;
    document.getElementById('errorRate').textContent = (summary.error_rate || 0) + '%';
}

// 更新最近日志
function updateRecentLogs(logs) {
    const container = document.getElementById('recentLogs');
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无最近日志</p>';
        return;
    }
    
    const logsHtml = logs.map(log => `
        <div class="log-entry ${log.status} p-3 mb-2 bg-light rounded">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">${log.operation_name || '未知操作'}</h6>
                    <p class="mb-1">${log.description || ''}</p>
                    <div class="log-details">
                        <span class="badge status-badge bg-${log.status === 'success' ? 'success' : 'danger'}">${log.status === 'success' ? '成功' : '失败'}</span>
                        <span class="ms-2">${log.module_name || ''}</span>
                        <span class="ms-2">${log.username || '系统'}</span>
                        <span class="ms-2">${new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                </div>
                <div>
                    <span class="text-muted">${log.execution_time || 0}ms</span>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = logsHtml;
}

// 更新图表
function updateCharts(data) {
    updateOperationTrendChart(data.daily_stats);
    updateOperationTypeChart(data.operation_type_stats);
}

// 更新操作趋势图表
function updateOperationTrendChart(dailyStats) {
    const ctx = document.getElementById('operationTrendChart').getContext('2d');
    
    if (operationTrendChart) {
        operationTrendChart.destroy();
    }
    
    const labels = dailyStats.map(stat => stat.date);
    const successData = dailyStats.map(stat => stat.success);
    const failedData = dailyStats.map(stat => stat.failed);
    
    operationTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '成功操作',
                data: successData,
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.1
            }, {
                label: '失败操作',
                data: failedData,
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 更新操作类型图表
function updateOperationTypeChart(typeStats) {
    const ctx = document.getElementById('operationTypeChart').getContext('2d');
    
    if (operationTypeChart) {
        operationTypeChart.destroy();
    }
    
    const labels = Object.keys(typeStats);
    const data = Object.values(typeStats);
    
    operationTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// 刷新仪表板
function refreshDashboard() {
    loadDashboardData();
}
</script>
{% endblock %}'''
        
        with open(os.path.join(template_dir, "dashboard.html"), 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
    
    def _create_logs_template(self, template_dir: str):
        """创建日志列表模板"""
        logs_html = '''{% extends "base.html" %}
{% block title %}操作日志列表{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">操作日志列表</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button class="btn btn-sm btn-outline-secondary" onclick="exportLogs()">
            <i class="bi bi-download"></i> 导出
        </button>
    </div>
</div>

<!-- 搜索和过滤 -->
<div class="card mb-4">
    <div class="card-body">
        <form id="searchForm" class="row g-3">
            <div class="col-md-3">
                <label for="searchKeyword" class="form-label">搜索关键词</label>
                <input type="text" class="form-control" id="searchKeyword" placeholder="搜索操作名称、描述等">
            </div>
            <div class="col-md-2">
                <label for="operationType" class="form-label">操作类型</label>
                <select class="form-select" id="operationType">
                    <option value="">全部</option>
                    <option value="create">创建</option>
                    <option value="update">更新</option>
                    <option value="delete">删除</option>
                    <option value="read">查询</option>
                    <option value="login">登录</option>
                    <option value="logout">登出</option>
                    <option value="system">系统</option>
                </select>
            </div>
            <div class="col-md-2">
                <label for="status" class="form-label">状态</label>
                <select class="form-select" id="status">
                    <option value="">全部</option>
                    <option value="success">成功</option>
                    <option value="failed">失败</option>
                </select>
            </div>
            <div class="col-md-2">
                <label for="dateRange" class="form-label">时间范围</label>
                <select class="form-select" id="dateRange">
                    <option value="1">最近1天</option>
                    <option value="7" selected>最近7天</option>
                    <option value="30">最近30天</option>
                    <option value="90">最近90天</option>
                </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
                <button type="submit" class="btn btn-primary me-2">
                    <i class="bi bi-search"></i> 搜索
                </button>
                <button type="button" class="btn btn-outline-secondary" onclick="resetSearch()">
                    <i class="bi bi-arrow-clockwise"></i> 重置
                </button>
            </div>
        </form>
    </div>
</div>

<!-- 日志列表 -->
<div class="card">
    <div class="card-body">
        <div id="logsContainer">
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
            </div>
        </div>
        
        <!-- 分页 -->
        <nav aria-label="日志分页">
            <ul class="pagination justify-content-center" id="pagination">
            </ul>
        </nav>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
let currentPage = 1;
let pageSize = 20;
let totalPages = 1;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadLogs();
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 1;
        loadLogs();
    });
});

// 加载日志列表
async function loadLogs() {
    try {
        const formData = new FormData(document.getElementById('searchForm'));
        const params = new URLSearchParams();
        
        params.append('page', currentPage);
        params.append('limit', pageSize);
        
        for (let [key, value] of formData.entries()) {
            if (value) params.append(key, value);
        }
        
        const response = await fetch(`/api/operation-logs/logs?${params}`);
        const data = await response.json();
        
        if (data.success) {
            displayLogs(data.data.logs);
            updatePagination(data.data.total, data.data.page, data.data.limit);
        } else {
            console.error('加载日志失败:', data.error);
        }
    } catch (error) {
        console.error('加载日志失败:', error);
    }
}

// 显示日志列表
function displayLogs(logs) {
    const container = document.getElementById('logsContainer');
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">暂无日志数据</p>';
        return;
    }
    
    const logsHtml = logs.map(log => `
        <div class="log-entry ${log.status} p-3 mb-3 bg-light rounded">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-2">
                        <h6 class="mb-0 me-3">${log.operation_name || '未知操作'}</h6>
                        <span class="badge bg-${log.status === 'success' ? 'success' : 'danger'}">${log.status === 'success' ? '成功' : '失败'}</span>
                        <span class="badge bg-secondary ms-2">${log.operation_type || ''}</span>
                    </div>
                    <p class="mb-2 text-muted">${log.description || ''}</p>
                    <div class="log-details">
                        <small class="text-muted">
                            <i class="bi bi-person"></i> ${log.username || '系统'} |
                            <i class="bi bi-folder"></i> ${log.module_name || ''} |
                            <i class="bi bi-clock"></i> ${new Date(log.timestamp).toLocaleString()} |
                            <i class="bi bi-stopwatch"></i> ${log.execution_time || 0}ms
                            ${log.ip_address ? `| <i class="bi bi-geo-alt"></i> ${log.ip_address}` : ''}
                        </small>
                    </div>
                    ${log.error_message ? `<div class="alert alert-danger mt-2 mb-0"><small>${log.error_message}</small></div>` : ''}
                </div>
                <div class="ms-3">
                    <button class="btn btn-sm btn-outline-info" onclick="showLogDetails('${log.log_id}')">
                        <i class="bi bi-eye"></i> 详情
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = logsHtml;
}

// 更新分页
function updatePagination(total, page, limit) {
    totalPages = Math.ceil(total / limit);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHtml = '';
    
    // 上一页
    paginationHtml += `
        <li class="page-item ${page === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${page - 1})">上一页</a>
        </li>
    `;
    
    // 页码
    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(totalPages, page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="page-item ${i === page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    // 下一页
    paginationHtml += `
        <li class="page-item ${page === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${page + 1})">下一页</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHtml;
}

// 切换页面
function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadLogs();
}

// 重置搜索
function resetSearch() {
    document.getElementById('searchForm').reset();
    currentPage = 1;
    loadLogs();
}

// 显示日志详情
function showLogDetails(logId) {
    // 这里可以实现模态框显示详细信息
    alert('日志详情功能待实现: ' + logId);
}

// 导出日志
function exportLogs() {
    const formData = new FormData(document.getElementById('searchForm'));
    const params = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value) params.append(key, value);
    }
    
    window.open(`/api/operation-logs/export?${params}`, '_blank');
}
</script>
{% endblock %}'''
        
        with open(os.path.join(template_dir, "logs.html"), 'w', encoding='utf-8') as f:
            f.write(logs_html)
    
    def _create_statistics_template(self, template_dir: str):
        """创建统计分析模板"""
        stats_html = '''{% extends "base.html" %}
{% block title %}操作日志统计分析{% endblock %}
{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">操作日志统计分析</h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button class="btn btn-sm btn-outline-secondary" onclick="refreshStatistics()">
            <i class="bi bi-arrow-clockwise"></i> 刷新
        </button>
    </div>
</div>

<!-- 统计概览 -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">总操作数</h5>
                <h2 class="text-primary" id="totalOperations">-</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">成功率</h5>
                <h2 class="text-success" id="successRate">-</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">平均执行时间</h5>
                <h2 class="text-info" id="avgExecutionTime">-</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h5 class="card-title">活跃用户</h5>
                <h2 class="text-warning" id="activeUsers">-</h2>
            </div>
        </div>
    </div>
</div>

<!-- 图表区域 -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">操作类型分布</h5>
            </div>
            <div class="card-body">
                <canvas id="operationTypeChart"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">用户活跃度</h5>
            </div>
            <div class="card-body">
                <canvas id="userActivityChart"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">操作趋势</h5>
            </div>
            <div class="card-body">
                <canvas id="operationTrendChart"></canvas>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
});

// 加载统计数据
async function loadStatistics() {
    try {
        const response = await fetch('/api/operation-logs/statistics');
        const data = await response.json();
        
        if (data.success) {
            updateStatistics(data.data);
        } else {
            console.error('加载统计数据失败:', data.error);
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 更新统计信息
function updateStatistics(data) {
    // 更新概览卡片
    document.getElementById('totalOperations').textContent = data.summary?.total_logs || 0;
    document.getElementById('successRate').textContent = (data.summary?.success_rate || 0) + '%';
    document.getElementById('avgExecutionTime').textContent = (data.summary?.avg_execution_time || 0) + 'ms';
    document.getElementById('activeUsers').textContent = data.summary?.total_users || 0;
    
    // 更新图表
    updateOperationTypeChart(data.operation_type_stats);
    updateUserActivityChart(data.user_stats);
    updateOperationTrendChart(data.daily_stats);
}

// 更新操作类型图表
function updateOperationTypeChart(typeStats) {
    const ctx = document.getElementById('operationTypeChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(typeStats || {}),
            datasets: [{
                data: Object.values(typeStats || {}),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
}

// 更新用户活跃度图表
function updateUserActivityChart(userStats) {
    const ctx = document.getElementById('userActivityChart').getContext('2d');
    
    const users = Object.keys(userStats || {});
    const activities = Object.values(userStats || {});
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: users,
            datasets: [{
                label: '操作次数',
                data: activities,
                backgroundColor: '#36A2EB'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 更新操作趋势图表
function updateOperationTrendChart(dailyStats) {
    const ctx = document.getElementById('operationTrendChart').getContext('2d');
    
    const labels = dailyStats?.map(stat => stat.date) || [];
    const successData = dailyStats?.map(stat => stat.success) || [];
    const failedData = dailyStats?.map(stat => stat.failed) || [];
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '成功操作',
                data: successData,
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.1
            }, {
                label: '失败操作',
                data: failedData,
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 刷新统计
function refreshStatistics() {
    loadStatistics();
}
</script>
{% endblock %}'''
        
        with open(os.path.join(template_dir, "statistics.html"), 'w', encoding='utf-8') as f:
            f.write(stats_html)
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/operation-logs/dashboard')
        def dashboard():
            """仪表板页面"""
            return render_template('operation_logs/dashboard.html')
        
        @self.app.route('/operation-logs/logs')
        def logs():
            """日志列表页面"""
            return render_template('operation_logs/logs.html')
        
        @self.app.route('/operation-logs/statistics')
        def statistics():
            """统计分析页面"""
            return render_template('operation_logs/statistics.html')
        
        @self.app.route('/api/operation-logs/dashboard')
        def api_dashboard():
            """获取仪表板数据API"""
            try:
                days = int(request.args.get('days', 7))
                data = self.service.get_dashboard_data(days)
                return jsonify({'success': True, 'data': data})
            except Exception as e:
                logger.error(f"❌ 获取仪表板数据失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/operation-logs/logs')
        def api_logs():
            """获取日志列表API"""
            try:
                # 获取查询参数
                page = int(request.args.get('page', 1))
                limit = int(request.args.get('limit', 20))
                offset = (page - 1) * limit
                
                user_id = request.args.get('user_id')
                username = request.args.get('username')
                operation_type = request.args.get('operation_type')
                operation_name = request.args.get('operation_name')
                module_name = request.args.get('module_name')
                status = request.args.get('status')
                ip_address = request.args.get('ip_address')
                
                # 时间范围
                date_range = int(request.args.get('dateRange', 7))
                end_date = datetime.now()
                start_date = end_date - timedelta(days=date_range)
                
                # 搜索关键词
                keyword = request.args.get('searchKeyword')
                
                if keyword:
                    logs = self.service.search_logs(keyword, limit=limit)
                    total = len(logs)
                else:
                    logs = self.service.get_logs(
                        user_id=user_id,
                        username=username,
                        operation_type=operation_type,
                        operation_name=operation_name,
                        module_name=module_name,
                        status=status,
                        start_date=start_date,
                        end_date=end_date,
                        ip_address=ip_address,
                        limit=limit,
                        offset=offset
                    )
                    
                    # 获取总数（简化处理）
                    total = len(logs) + offset
                
                return jsonify({
                    'success': True,
                    'data': {
                        'logs': logs,
                        'total': total,
                        'page': page,
                        'limit': limit
                    }
                })
            except Exception as e:
                logger.error(f"❌ 获取日志列表失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/operation-logs/statistics')
        def api_statistics():
            """获取统计数据API"""
            try:
                days = int(request.args.get('days', 30))
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                stats = self.service.get_statistics(start_date, end_date)
                user_stats = self.service.get_user_statistics(days)
                operation_type_stats = self.service.get_operation_type_statistics(days)
                performance = self.service.get_performance_statistics(days)
                daily_stats = self.service.get_daily_statistics(days)
                
                data = {
                    'summary': {
                        'total_logs': stats.get('total_logs', 0),
                        'success_logs': stats.get('success_logs', 0),
                        'failed_logs': stats.get('failed_logs', 0),
                        'success_rate': performance.get('success_rate', 0),
                        'avg_execution_time': performance.get('avg_execution_time', 0),
                        'total_users': user_stats.get('total_users', 0)
                    },
                    'operation_type_stats': operation_type_stats.get('operation_type_stats', {}),
                    'user_stats': user_stats.get('user_stats', {}),
                    'daily_stats': daily_stats
                }
                
                return jsonify({'success': True, 'data': data})
            except Exception as e:
                logger.error(f"❌ 获取统计数据失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/operation-logs/export')
        def api_export():
            """导出日志API"""
            try:
                # 获取查询参数
                date_range = int(request.args.get('dateRange', 7))
                end_date = datetime.now()
                start_date = end_date - timedelta(days=date_range)
                
                format_type = request.args.get('format', 'json')
                
                filepath = self.service.export_logs(start_date, end_date, format_type)
                
                if filepath and os.path.exists(filepath):
                    return send_from_directory(
                        os.path.dirname(filepath),
                        os.path.basename(filepath),
                        as_attachment=True
                    )
                else:
                    return jsonify({'success': False, 'error': '导出失败'}), 500
            except Exception as e:
                logger.error(f"❌ 导出日志失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/operation-logs/cleanup', methods=['POST'])
        def api_cleanup():
            """清理旧日志API"""
            try:
                days = int(request.json.get('days', 30))
                deleted_count = self.service.cleanup_old_logs(days)
                return jsonify({
                    'success': True,
                    'message': f'已清理 {deleted_count} 条旧日志'
                })
            except Exception as e:
                logger.error(f"❌ 清理旧日志失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5001, debug=False):
        """运行Web应用"""
        logger.info(f"🚀 启动操作日志Web应用: http://{host}:{port}")
        logger.info(f"📊 仪表板: http://{host}:{port}/operation-logs/dashboard")
        logger.info(f"📋 日志列表: http://{host}:{port}/operation-logs/logs")
        logger.info(f"📈 统计分析: http://{host}:{port}/operation-logs/statistics")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='操作日志Web管理界面')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=5001, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--config', default='config.ini', help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        app = OperationLogWebApp(args.config)
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()