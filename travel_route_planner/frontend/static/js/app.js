/**
 * AI旅游路线规划系统前端JavaScript
 */

// 全局变量
let currentUser = null;
let currentToken = null;
let map = null;
let chatSessionId = null;
let currentPlanId = null;
let comments = [];

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
    document.getElementById('commentForm').addEventListener('submit', handleCommentSubmit);
    
    // 聊天功能
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
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
async function viewPlan(planId) {
    currentPlanId = planId;
    showSection('plan-detail');
    await loadPlanDetail(planId);
    await loadPlanComments(planId);
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

/**
 * 查看计划详情
 */
async function viewPlan(planId) {
    currentPlanId = planId;
    showSection('plan-detail');
    await loadPlanDetail(planId);
    await loadPlanComments(planId);
}

/**
 * 加载计划详情
 */
async function loadPlanDetail(planId) {
    try {
        const response = await fetch(`${API_BASE_URL}/plans/${planId}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const plan = await response.json();
            displayPlanDetail(plan);
        } else {
            throw new Error('加载计划详情失败');
        }
    } catch (error) {
        console.error('加载计划详情失败:', error);
        showError('加载计划详情失败: ' + error.message);
    }
}

/**
 * 显示计划详情
 */
function displayPlanDetail(plan) {
    const content = document.getElementById('planDetailContent');
    const sidebar = document.getElementById('planSidebar');
    
    const startDate = new Date(plan.start_date).toLocaleDateString('zh-CN');
    const endDate = new Date(plan.end_date).toLocaleDateString('zh-CN');
    
    // 主要内容
    content.innerHTML = `
        <div class="plan-header mb-4">
            <h4>${plan.title}</h4>
            <p class="text-muted">
                <i class="fas fa-map-marker-alt me-1"></i>${plan.destination} | 
                <i class="fas fa-calendar me-1"></i>${startDate} - ${endDate} | 
                <i class="fas fa-tag me-1"></i>${plan.travel_type || '未指定'}
            </p>
        </div>
        <div class="plan-content">
            <p>${plan.preferences?.description || '暂无详细描述'}</p>
        </div>
    `;
    
    // 侧边栏
    sidebar.innerHTML = `
        <div class="plan-info">
            <h6>基本信息</h6>
            <ul class="list-unstyled">
                <li><strong>目的地:</strong> ${plan.destination}</li>
                <li><strong>开始日期:</strong> ${startDate}</li>
                <li><strong>结束日期:</strong> ${endDate}</li>
                <li><strong>旅行类型:</strong> ${plan.travel_type || '未指定'}</li>
                <li><strong>预算:</strong> ${plan.budget ? '¥' + plan.budget : '未设定'}</li>
                <li><strong>状态:</strong> <span class="badge bg-primary">${plan.status}</span></li>
            </ul>
        </div>
    `;
}

/**
 * 加载计划评论
 */
async function loadPlanComments(planId) {
    try {
        const response = await fetch(`${API_BASE_URL}/comments/plan/${planId}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            comments = await response.json();
            displayComments(comments);
        } else {
            throw new Error('加载评论失败');
        }
    } catch (error) {
        console.error('加载评论失败:', error);
        showError('加载评论失败: ' + error.message);
    }
}

/**
 * 显示评论列表
 */
function displayComments(commentsList) {
    const container = document.getElementById('commentsList');
    
    if (commentsList.length === 0) {
        container.innerHTML = `
            <div class="comment-empty">
                <i class="fas fa-comments"></i>
                <p>暂无评论，快来分享您的想法吧！</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    commentsList.forEach(comment => {
        html += renderComment(comment, 1);
    });
    
    container.innerHTML = html;
}

/**
 * 渲染单个评论
 */
function renderComment(comment, level) {
    const createdDate = new Date(comment.created_at).toLocaleString('zh-CN');
    const isOwner = currentUser && comment.user_id === currentUser.id;
    
    let html = `
        <div class="comment-item level-${level}" data-comment-id="${comment.id}">
            <div class="comment-header">
                <div class="comment-author">
                    <i class="fas fa-user-circle"></i>
                    <span>${comment.user?.username || '未知用户'}</span>
                </div>
                <div class="comment-time">${createdDate}</div>
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-actions">
                <button class="comment-like-btn ${comment.is_liked ? 'liked' : ''}" 
                        onclick="toggleCommentLike(${comment.id})">
                    <i class="fas fa-heart"></i>
                    <span>${comment.like_count}</span>
                </button>
                <button class="comment-reply-btn" onclick="toggleReplyForm(${comment.id})">
                    <i class="fas fa-reply"></i>
                    回复
                </button>
                ${isOwner ? `
                    <button class="comment-edit-btn" onclick="toggleEditForm(${comment.id})">
                        <i class="fas fa-edit"></i>
                        编辑
                    </button>
                    <button class="comment-delete-btn" onclick="deleteComment(${comment.id})">
                        <i class="fas fa-trash"></i>
                        删除
                    </button>
                ` : ''}
            </div>
            <div class="comment-edit-form" id="edit-form-${comment.id}">
                <textarea class="form-control" id="edit-content-${comment.id}" rows="3">${comment.content}</textarea>
                <div class="comment-edit-actions">
                    <button class="btn btn-sm btn-primary" onclick="saveCommentEdit(${comment.id})">保存</button>
                    <button class="btn btn-sm btn-secondary" onclick="cancelCommentEdit(${comment.id})">取消</button>
                </div>
            </div>
            <div class="comment-reply-form" id="reply-form-${comment.id}">
                <textarea class="form-control" id="reply-content-${comment.id}" rows="3" placeholder="写下您的回复..."></textarea>
                <div class="comment-edit-actions">
                    <button class="btn btn-sm btn-primary" onclick="submitReply(${comment.id})">回复</button>
                    <button class="btn btn-sm btn-secondary" onclick="cancelReply(${comment.id})">取消</button>
                </div>
            </div>
            <div class="comment-replies" id="replies-${comment.id}">
    `;
    
    // 渲染回复
    if (comment.replies && comment.replies.length > 0) {
        comment.replies.forEach(reply => {
            html += renderComment(reply, level + 1);
        });
    }
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

/**
 * 处理评论提交
 */
async function handleCommentSubmit(e) {
    e.preventDefault();
    
    if (!currentUser) {
        showError('请先登录');
        showLoginModal();
        return;
    }
    
    const content = document.getElementById('commentContent').value.trim();
    if (!content) {
        showError('请输入评论内容');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                content: content,
                plan_id: currentPlanId
            })
        });
        
        if (response.ok) {
            const newComment = await response.json();
            // 重新加载评论列表
            await loadPlanComments(currentPlanId);
            // 清空表单
            document.getElementById('commentContent').value = '';
            hideLoading();
            showSuccess('评论发表成功！');
        } else {
            const error = await response.json();
            throw new Error(error.detail || '发表评论失败');
        }
    } catch (error) {
        hideLoading();
        showError('发表评论失败: ' + error.message);
    }
}

/**
 * 切换评论点赞
 */
async function toggleCommentLike(commentId) {
    if (!currentUser) {
        showError('请先登录');
        showLoginModal();
        return;
    }
    
    try {
        const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
        const likeBtn = commentElement.querySelector('.comment-like-btn');
        const isLiked = likeBtn.classList.contains('liked');
        
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}/like`, {
            method: isLiked ? 'DELETE' : 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            // 更新UI
            if (isLiked) {
                likeBtn.classList.remove('liked');
                const countSpan = likeBtn.querySelector('span');
                const currentCount = parseInt(countSpan.textContent);
                countSpan.textContent = Math.max(0, currentCount - 1);
            } else {
                likeBtn.classList.add('liked');
                const countSpan = likeBtn.querySelector('span');
                const currentCount = parseInt(countSpan.textContent);
                countSpan.textContent = currentCount + 1;
            }
        } else {
            throw new Error('操作失败');
        }
    } catch (error) {
        showError('操作失败: ' + error.message);
    }
}

/**
 * 切换回复表单
 */
function toggleReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    const isVisible = replyForm.classList.contains('show');
    
    // 隐藏所有其他回复表单
    document.querySelectorAll('.comment-reply-form.show').forEach(form => {
        form.classList.remove('show');
    });
    
    if (!isVisible) {
        replyForm.classList.add('show');
        document.getElementById(`reply-content-${commentId}`).focus();
    }
}

/**
 * 取消回复
 */
function cancelReply(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    replyForm.classList.remove('show');
    document.getElementById(`reply-content-${commentId}`).value = '';
}

/**
 * 提交回复
 */
async function submitReply(commentId) {
    const content = document.getElementById(`reply-content-${commentId}`).value.trim();
    if (!content) {
        showError('请输入回复内容');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                content: content,
                plan_id: currentPlanId,
                parent_id: commentId
            })
        });
        
        if (response.ok) {
            // 重新加载评论列表
            await loadPlanComments(currentPlanId);
            hideLoading();
            showSuccess('回复发表成功！');
        } else {
            const error = await response.json();
            throw new Error(error.detail || '发表回复失败');
        }
    } catch (error) {
        hideLoading();
        showError('发表回复失败: ' + error.message);
    }
}

/**
 * 切换编辑表单
 */
function toggleEditForm(commentId) {
    const editForm = document.getElementById(`edit-form-${commentId}`);
    const isVisible = editForm.classList.contains('show');
    
    // 隐藏所有其他编辑表单
    document.querySelectorAll('.comment-edit-form.show').forEach(form => {
        form.classList.remove('show');
    });
    
    if (!isVisible) {
        editForm.classList.add('show');
        document.getElementById(`edit-content-${commentId}`).focus();
    }
}

/**
 * 取消编辑
 */
function cancelCommentEdit(commentId) {
    const editForm = document.getElementById(`edit-form-${commentId}`);
    editForm.classList.remove('show');
}

/**
 * 保存评论编辑
 */
async function saveCommentEdit(commentId) {
    const content = document.getElementById(`edit-content-${commentId}`).value.trim();
    if (!content) {
        showError('请输入评论内容');
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                content: content
            })
        });
        
        if (response.ok) {
            // 重新加载评论列表
            await loadPlanComments(currentPlanId);
            hideLoading();
            showSuccess('评论更新成功！');
        } else {
            const error = await response.json();
            throw new Error(error.detail || '更新评论失败');
        }
    } catch (error) {
        hideLoading();
        showError('更新评论失败: ' + error.message);
    }
}

/**
 * 删除评论
 */
async function deleteComment(commentId) {
    if (!confirm('确定要删除这条评论吗？')) {
        return;
    }
    
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/comments/${commentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            // 重新加载评论列表
            await loadPlanComments(currentPlanId);
            hideLoading();
            showSuccess('评论删除成功！');
        } else {
            const error = await response.json();
            throw new Error(error.detail || '删除评论失败');
        }
    } catch (error) {
        hideLoading();
        showError('删除评论失败: ' + error.message);
    }
}