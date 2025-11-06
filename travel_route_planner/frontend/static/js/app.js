/**
 * AI旅游路线规划系统前端JavaScript
 */

// 全局变量
let currentUser = null;
let currentToken = null;
let map = null;
let chatSessionId = null;

// API基础URL
const API_BASE_URL = '/api/v1';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * 初始化应用程序
 */
function initializeApp() {
    // 设置事件监听器
    setupEventListeners();
    
    // 检查用户登录状态
    checkAuthStatus();
    
    // 初始化聊天会话
    chatSessionId = generateSessionId();
    
    // 设置默认日期
    setDefaultDates();
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 导航链接
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            showSection(target);
        });
    });
    
    // 登录/注册按钮
    document.getElementById('loginBtn').addEventListener('click', showLoginModal);
    document.getElementById('registerBtn').addEventListener('click', showRegisterModal);
    
    // 表单提交
    document.getElementById('planForm').addEventListener('submit', handlePlanSubmit);
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // 聊天功能
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    const exportBtn = document.getElementById('exportPdfBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportSelectionToPDF);
    }
    
    // 视图切换
    document.getElementById('mapViewBtn').addEventListener('click', showMapView);
    document.getElementById('listViewBtn').addEventListener('click', showListView);
}

/**
 * 显示指定区域
 */
function showSection(sectionId) {
    // 隐藏所有区域
    document.querySelectorAll('main section').forEach(section => {
        section.style.display = 'none';
    });
    
    // 显示目标区域
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('fade-in');
        
        // 如果是我的计划区域，加载用户计划
        if (sectionId === 'my-plans') {
            loadUserPlans();
        }
    }
    
    // 更新导航状态
    updateNavigationState(sectionId);
}

/**
 * 更新导航状态
 */
function updateNavigationState(activeSection) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${activeSection}`) {
            link.classList.add('active');
        }
    });
}

/**
 * 检查用户认证状态
 */
function checkAuthStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        currentToken = token;
        // 验证token有效性
        validateToken();
    }
}

/**
 * 验证token
 */
async function validateToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            updateAuthUI(true);
        } else {
            localStorage.removeItem('token');
            currentToken = null;
            currentUser = null;
            updateAuthUI(false);
        }
    } catch (error) {
        console.error('Token验证失败:', error);
        updateAuthUI(false);
    }
}

/**
 * 更新认证UI
 */
function updateAuthUI(isLoggedIn) {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    
    if (isLoggedIn) {
        loginBtn.textContent = currentUser.username;
        loginBtn.className = 'btn btn-outline-light me-2';
        registerBtn.textContent = '退出';
        registerBtn.className = 'btn btn-light';
        registerBtn.onclick = logout;
    } else {
        loginBtn.textContent = '登录';
        loginBtn.className = 'btn btn-outline-light me-2';
        loginBtn.onclick = showLoginModal;
        registerBtn.textContent = '注册';
        registerBtn.className = 'btn btn-light';
        registerBtn.onclick = showRegisterModal;
    }
}

/**
 * 显示登录模态框
 */
function showLoginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

/**
 * 显示注册模态框
 */
function showRegisterModal() {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

/**
 * 处理登录
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('token', currentToken);
            
            updateAuthUI(true);
            hideLoading();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            modal.hide();
            
            showSuccess('登录成功！');
        } else {
            throw new Error(data.detail || '登录失败');
        }
    } catch (error) {
        hideLoading();
        showError('登录失败: ' + error.message);
    }
}

/**
 * 处理注册
 */
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideLoading();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            modal.hide();
            
            showSuccess('注册成功！请登录');
            showLoginModal();
        } else {
            throw new Error(data.detail || '注册失败');
        }
    } catch (error) {
        hideLoading();
        showError('注册失败: ' + error.message);
    }
}

/**
 * 退出登录
 */
function logout() {
    localStorage.removeItem('token');
    currentToken = null;
    currentUser = null;
    updateAuthUI(false);
    showSuccess('已退出登录');
}

/**
 * 处理路线规划表单提交
 */
async function handlePlanSubmit(e) {
    e.preventDefault();
    
    if (!currentUser) {
        showError('请先登录');
        showLoginModal();
        return;
    }
    
    const formData = {
        destination: document.getElementById('destination').value,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        budget: document.getElementById('budget').value ? parseFloat(document.getElementById('budget').value) : null,
        travel_type: document.getElementById('travelType').value || null,
        preferences: document.getElementById('preferences').value ? {
            description: document.getElementById('preferences').value
        } : null
    };
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/route/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayPlanResult(data);
            hideLoading();
        } else {
            throw new Error(data.detail || '路线规划失败');
        }
    } catch (error) {
        hideLoading();
        showError('路线规划失败: ' + error.message);
    }
}

/**
 * 显示路线规划结果
 */
function displayPlanResult(plan) {
    const resultContainer = document.getElementById('planResult');
    
    let html = `
        <div class="plan-header mb-4">
            <h4>${plan.destination} 旅游路线规划</h4>
            <p class="text-muted">${plan.start_date} 至 ${plan.end_date} (${plan.travel_days}天)</p>
        </div>
    `;
    
    // 费用统计
    if (plan.total_cost) {
        html += `
            <div class="cost-summary mb-4">
                <h6 class="mb-3">费用预算</h6>
                <div class="cost-item">
                    <span>门票费用</span>
                    <span>¥${plan.total_cost.tickets || 0}</span>
                </div>
                <div class="cost-item">
                    <span>餐饮费用</span>
                    <span>¥${plan.total_cost.meals || 0}</span>
                </div>
                <div class="cost-item">
                    <span>交通费用</span>
                    <span>¥${plan.total_cost.transport || 0}</span>
                </div>
                <div class="cost-item">
                    <span>住宿费用</span>
                    <span>¥${plan.total_cost.accommodation || 0}</span>
                </div>
                <div class="cost-total">
                    <span>总计</span>
                    <span>¥${plan.total_cost.total || 0}</span>
                </div>
            </div>
        `;
    }
    
    // 每日行程
    if (plan.daily_plans && plan.daily_plans.length > 0) {
        html += '<div class="daily-plans">';
        plan.daily_plans.forEach((day, index) => {
            html += `
                <div class="plan-day">
                    <h6>第${index + 1}天 - ${day.date}</h6>
                    <div class="spots-list">
            `;
            
            if (day.spots && day.spots.length > 0) {
                day.spots.forEach(spot => {
                    html += `
                        <div class="spot-item">
                            <div class="spot-info">
                                <div class="spot-name">${spot.name}</div>
                                <div class="spot-details">
                                    ${spot.description || ''} | 评分: ${spot.rating} | 门票: ¥${spot.ticket_price || 0}
                                </div>
                            </div>
                            <div class="spot-time">
                                ${spot.arrival_time} - ${spot.departure_time}
                            </div>
                        </div>
                    `;
                });
            } else {
                html += '<p class="text-muted">暂无景点安排</p>';
            }
            
            html += `
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    resultContainer.innerHTML = html;
    
    // 初始化地图
    if (plan.map_data) {
        initMap(plan.map_data);
    }
}

/**
 * 初始化地图
 */
function initMap(mapData) {
    const mapContainer = document.getElementById('mapContainer');
    mapContainer.style.display = 'block';
    
    if (map) {
        map.remove();
    }
    
    // 创建地图
    map = L.map('mapContainer').setView([39.9042, 116.4074], 10);
    
    // 添加地图图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // 添加景点标记
    if (mapData.spots) {
        mapData.spots.forEach(spot => {
            const marker = L.marker([spot.latitude, spot.longitude])
                .addTo(map)
                .bindPopup(`
                    <b>${spot.name}</b><br>
                    到达时间: ${spot.arrival_time}<br>
                    评分: ${spot.rating}
                `);
        });
    }
    
    // 添加路线
    if (mapData.routes) {
        mapData.routes.forEach(route => {
            if (route.coordinates && route.coordinates.length > 1) {
                L.polyline(route.coordinates, {
                    color: 'blue',
                    weight: 3,
                    opacity: 0.7
                }).addTo(map);
            }
        });
    }
    
    // 调整地图视图
    if (mapData.spots && mapData.spots.length > 0) {
        const group = new L.featureGroup(map._layers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * 显示地图视图
 */
function showMapView() {
    document.getElementById('mapContainer').style.display = 'block';
    document.getElementById('planResult').style.display = 'none';
    
    // 更新按钮状态
    document.getElementById('mapViewBtn').classList.add('active');
    document.getElementById('listViewBtn').classList.remove('active');
}

/**
 * 显示列表视图
 */
function showListView() {
    document.getElementById('mapContainer').style.display = 'none';
    document.getElementById('planResult').style.display = 'block';
    
    // 更新按钮状态
    document.getElementById('listViewBtn').classList.add('active');
    document.getElementById('mapViewBtn').classList.remove('active');
}

/**
 * 发送聊天消息
 */
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息到界面
    addMessageToChat('user', message);
    input.value = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken || ''}`
            },
            body: JSON.stringify({
                session_id: chatSessionId,
                content: message
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToChat('ai', data.content);
        } else {
            throw new Error(data.detail || '发送失败');
        }
    } catch (error) {
        addMessageToChat('ai', '抱歉，我暂时无法回复您的消息。请稍后再试。');
        console.error('发送消息失败:', error);
    }
}

/**
 * 添加消息到聊天界面
 */
function addMessageToChat(type, content) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-time">${timeString}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * 将选中的GPT内容导出为PDF
 */
function exportSelectionToPDF() {
    if (typeof html2pdf === 'undefined') {
        showError('PDF导出库加载失败，请刷新页面后重试');
        return;
    }

    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
        showError('请先选择要导出的GPT内容');
        return;
    }

    const range = selection.getRangeAt(0);
    const chatContainer = document.getElementById('chatMessages');
    const selectionContainer = range.commonAncestorContainer.nodeType === Node.TEXT_NODE
        ? range.commonAncestorContainer.parentNode
        : range.commonAncestorContainer;

    if (!chatContainer.contains(selectionContainer)) {
        showError('请选择AI助手区域的内容进行导出');
        return;
    }

    const selectedText = selection.toString().trim();
    if (!selectedText) {
        showError('所选内容为空，请重新选择');
        return;
    }

    const normalizedText = selectedText
        .replace(/\r\n/g, '\n')
        .replace(/\u00a0/g, ' ')
        .trim();

    const exportContainer = document.createElement('div');
    exportContainer.style.position = 'fixed';
    exportContainer.style.left = '-9999px';
    exportContainer.style.top = '0';
    exportContainer.style.width = '190mm';
    exportContainer.style.maxWidth = '190mm';
    exportContainer.style.boxSizing = 'border-box';
    exportContainer.style.padding = '24px 28px';
    exportContainer.style.backgroundColor = '#ffffff';
    exportContainer.style.color = '#212529';
    exportContainer.style.fontFamily = window.getComputedStyle(chatContainer).fontFamily || '"Microsoft YaHei", sans-serif';
    exportContainer.style.fontSize = '14px';
    exportContainer.style.lineHeight = '1.7';
    exportContainer.style.whiteSpace = 'pre-wrap';
    exportContainer.style.wordBreak = 'break-word';
    exportContainer.style.border = '1px solid #e9ecef';
    exportContainer.style.borderRadius = '8px';
    exportContainer.style.boxShadow = '0 12px 30px rgba(33, 37, 41, 0.12)';

    const title = document.createElement('h2');
    title.textContent = 'AI助手内容导出';
    title.style.margin = '0 0 12px';
    title.style.fontSize = '20px';
    title.style.color = '#0d6efd';

    const meta = document.createElement('p');
    meta.style.margin = '0 0 16px';
    meta.style.fontSize = '12px';
    meta.style.color = '#6c757d';
    const timestamp = new Date();
    const formattedTime = `${timestamp.getFullYear()}-${String(timestamp.getMonth() + 1).padStart(2, '0')}-${String(timestamp.getDate()).padStart(2, '0')} ${String(timestamp.getHours()).padStart(2, '0')}:${String(timestamp.getMinutes()).padStart(2, '0')}:${String(timestamp.getSeconds()).padStart(2, '0')}`;
    meta.textContent = `导出时间：${formattedTime}`;

    const content = document.createElement('div');
    content.style.padding = '16px';
    content.style.backgroundColor = '#f8f9fa';
    content.style.borderRadius = '6px';
    content.style.border = '1px solid #dee2e6';
    content.textContent = normalizedText;

    exportContainer.appendChild(title);
    exportContainer.appendChild(meta);
    exportContainer.appendChild(content);

    document.body.appendChild(exportContainer);

    const fileName = `gpt-content-${timestamp.getFullYear()}${String(timestamp.getMonth() + 1).padStart(2, '0')}${String(timestamp.getDate()).padStart(2, '0')}-${String(timestamp.getHours()).padStart(2, '0')}${String(timestamp.getMinutes()).padStart(2, '0')}${String(timestamp.getSeconds()).padStart(2, '0')}.pdf`;

    const options = {
        margin: [10, 10, 12, 10],
        filename: fileName,
        pagebreak: { mode: ['css', 'legacy'] },
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    showLoading();

    html2pdf()
        .set(options)
        .from(exportContainer)
        .save()
        .then(() => {
            showSuccess('选中内容已导出为PDF');
        })
        .catch(error => {
            console.error('PDF生成失败:', error);
            showError('生成PDF失败，请稍后再试');
        })
        .finally(() => {
            hideLoading();
            document.body.removeChild(exportContainer);
        });

    selection.removeAllRanges();
}

/**
 * 加载用户计划
 */
async function loadUserPlans() {
    if (!currentUser) {
        document.getElementById('plansList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-plus"></i>
                <p>请先登录查看您的旅游计划</p>
            </div>
        `;
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/plans`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        const plans = await response.json();
        
        if (plans && plans.length > 0) {
            displayUserPlans(plans);
        } else {
            document.getElementById('plansList').innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-calendar-plus"></i>
                    <p>暂无旅游计划，请先创建计划</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载计划失败:', error);
        document.getElementById('plansList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>加载计划失败，请稍后再试</p>
            </div>
        `;
    }
}

/**
 * 显示用户计划列表
 */
function displayUserPlans(plans) {
    const container = document.getElementById('plansList');
    
    let html = '<div class="card-grid">';
    
    plans.forEach(plan => {
        const startDate = new Date(plan.start_date).toLocaleDateString('zh-CN');
        const endDate = new Date(plan.end_date).toLocaleDateString('zh-CN');
        
        html += `
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">${plan.title}</h6>
                    <p class="card-text">
                        <i class="fas fa-map-marker-alt me-1"></i>${plan.destination}<br>
                        <i class="fas fa-calendar me-1"></i>${startDate} - ${endDate}<br>
                        <i class="fas fa-tag me-1"></i>${plan.travel_type || '未指定'}
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary">${plan.status}</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPlan(${plan.id})">
                            查看详情
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * 查看计划详情
 */
function viewPlan(planId) {
    // 这里可以实现查看计划详情的功能
    showSuccess('查看计划详情功能开发中...');
}

/**
 * 设置默认日期
 */
function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);
    
    document.getElementById('startDate').value = tomorrow.toISOString().split('T')[0];
    document.getElementById('endDate').value = nextWeek.toISOString().split('T')[0];
}

/**
 * 生成会话ID
 */
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9);
}

/**
 * 显示加载状态
 */
function showLoading() {
    const toast = new bootstrap.Toast(document.getElementById('loadingToast'));
    toast.show();
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    const toast = bootstrap.Toast.getInstance(document.getElementById('loadingToast'));
    if (toast) {
        toast.hide();
    }
}

/**
 * 显示成功消息
 */
function showSuccess(message) {
    showNotification(message, 'success');
}

/**
 * 显示错误消息
 */
function showError(message) {
    showNotification(message, 'danger');
}

/**
 * 显示通知
 */
function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 3000);
}