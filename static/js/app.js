// 全局变量
let rooms = [];
let bookings = [];
let logs = [];
let currentAccessRoomId = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadRooms();
    loadBookings();
    loadLogs();
    
    // 每30秒自动刷新数据
    setInterval(() => {
        loadRooms();
        loadBookings();
        loadLogs();
    }, 30000);
});

// 加载房间数据
async function loadRooms() {
    try {
        const response = await fetch('/api/rooms');
        rooms = await response.json();
        renderRooms();
        updateRoomSelect();
    } catch (error) {
        console.error('加载房间数据失败:', error);
        showAlert('加载房间数据失败', 'danger');
    }
}

// 渲染房间状态
function renderRooms() {
    const container = document.getElementById('rooms-container');
    container.innerHTML = '';
    
    rooms.forEach(room => {
        const roomCard = document.createElement('div');
        roomCard.className = `col-md-4 mb-3`;
        roomCard.innerHTML = `
            <div class="card room-card ${room.is_locked ? 'locked' : 'unlocked'}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="card-title mb-1">${room.name}</h6>
                            <span class="badge ${room.is_locked ? 'bg-danger' : 'bg-success'}">
                                ${room.is_locked ? '已锁定' : '已解锁'}
                            </span>
                        </div>
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="openAccessModal(${room.id})">
                                <i class="fas fa-key"></i> 门禁
                            </button>
                            <button class="btn btn-sm ${room.is_locked ? 'btn-success' : 'btn-warning'}" 
                                    onclick="toggleDoor(${room.id}, ${!room.is_locked})">
                                <i class="fas fa-${room.is_locked ? 'unlock' : 'lock'}"></i>
                                ${room.is_locked ? '解锁' : '锁定'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(roomCard);
    });
}

// 更新房间选择下拉框
function updateRoomSelect() {
    const select = document.getElementById('room-select');
    select.innerHTML = '<option value="">请选择房间</option>';
    
    rooms.forEach(room => {
        const option = document.createElement('option');
        option.value = room.id;
        option.textContent = room.name;
        select.appendChild(option);
    });
}

// 加载预约数据
async function loadBookings() {
    try {
        const response = await fetch('/api/bookings');
        bookings = await response.json();
        renderBookings();
    } catch (error) {
        console.error('加载预约数据失败:', error);
        showAlert('加载预约数据失败', 'danger');
    }
}

// 渲染预约列表
function renderBookings() {
    const tbody = document.getElementById('bookings-table');
    tbody.innerHTML = '';
    
    bookings.forEach(booking => {
        const row = document.createElement('tr');
        const room = rooms.find(r => r.id === booking.room_id);
        const roomName = room ? room.name : '未知房间';
        
        row.innerHTML = `
            <td>${roomName}</td>
            <td>${booking.user_name}</td>
            <td>${booking.user_phone}</td>
            <td>${formatDateTime(booking.start_time)}</td>
            <td>${formatDateTime(booking.end_time)}</td>
            <td><span class="badge status-${booking.status}">${getStatusText(booking.status)}</span></td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    ${booking.status === 'pending' ? `
                        <button class="btn btn-outline-success" onclick="updateBookingStatus(${booking.id}, 'active')">
                            <i class="fas fa-play"></i> 开始
                        </button>
                        <button class="btn btn-outline-danger" onclick="updateBookingStatus(${booking.id}, 'cancelled')">
                            <i class="fas fa-times"></i> 取消
                        </button>
                    ` : ''}
                    ${booking.status === 'active' ? `
                        <button class="btn btn-outline-warning" onclick="updateBookingStatus(${booking.id}, 'completed')">
                            <i class="fas fa-stop"></i> 结束
                        </button>
                    ` : ''}
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 加载访问日志
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        logs = await response.json();
        renderLogs();
    } catch (error) {
        console.error('加载日志数据失败:', error);
    }
}

// 渲染访问日志
function renderLogs() {
    const tbody = document.getElementById('logs-table');
    tbody.innerHTML = '';
    
    logs.forEach(log => {
        const row = document.createElement('tr');
        const room = rooms.find(r => r.id === log.room_id);
        const roomName = room ? room.name : '未知房间';
        
        row.innerHTML = `
            <td>${formatDateTime(log.timestamp)}</td>
            <td>${roomName}</td>
            <td><span class="badge action-${log.action}">${getActionText(log.action)}</span></td>
            <td>${log.reason || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// 创建预约
async function createBooking() {
    const form = document.getElementById('booking-form');
    const formData = new FormData(form);
    
    const bookingData = {
        room_id: parseInt(document.getElementById('room-select').value),
        user_name: document.getElementById('user-name').value,
        user_phone: document.getElementById('user-phone').value,
        start_time: document.getElementById('start-time').value,
        end_time: document.getElementById('end-time').value
    };
    
    // 验证时间
    if (new Date(bookingData.start_time) >= new Date(bookingData.end_time)) {
        showAlert('结束时间必须晚于开始时间', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/api/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        if (response.ok) {
            showAlert('预约创建成功', 'success');
            form.reset();
            bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide();
            loadBookings();
        } else {
            const error = await response.json();
            showAlert(error.error || '创建预约失败', 'danger');
        }
    } catch (error) {
        console.error('创建预约失败:', error);
        showAlert('创建预约失败', 'danger');
    }
}

// 更新预约状态
async function updateBookingStatus(bookingId, status) {
    try {
        const response = await fetch(`/api/bookings/${bookingId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        });
        
        if (response.ok) {
            showAlert('状态更新成功', 'success');
            loadBookings();
            loadRooms();
        } else {
            showAlert('状态更新失败', 'danger');
        }
    } catch (error) {
        console.error('更新状态失败:', error);
        showAlert('更新状态失败', 'danger');
    }
}

// 切换门禁状态
async function toggleDoor(roomId, shouldLock) {
    const action = shouldLock ? 'lock' : 'unlock';
    
    try {
        const response = await fetch(`/api/door/${roomId}/${action}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadRooms();
            loadLogs();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('门禁操作失败:', error);
        showAlert('门禁操作失败', 'danger');
    }
}

// 打开门禁控制模态框
function openAccessModal(roomId) {
    currentAccessRoomId = roomId;
    document.getElementById('access-phone').value = '';
    document.getElementById('access-result').style.display = 'none';
    new bootstrap.Modal(document.getElementById('accessModal')).show();
}

// 检查访问权限
async function checkAccess() {
    const phone = document.getElementById('access-phone').value;
    const resultDiv = document.getElementById('access-result');
    
    if (!phone) {
        showAlert('请输入手机号', 'danger', resultDiv);
        return;
    }
    
    try {
        const response = await fetch(`/api/access/${currentAccessRoomId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_phone: phone })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success', resultDiv);
            loadRooms();
            loadLogs();
        } else {
            showAlert(result.message, 'danger', resultDiv);
        }
    } catch (error) {
        console.error('访问验证失败:', error);
        showAlert('访问验证失败', 'danger', resultDiv);
    }
}

// 刷新数据
function refreshData() {
    loadRooms();
    loadBookings();
    loadLogs();
    showAlert('数据已刷新', 'info');
}

// 显示提示信息
function showAlert(message, type, container = null) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    if (container) {
        container.innerHTML = '';
        container.appendChild(alertDiv);
        container.style.display = 'block';
    } else {
        // 在页面顶部显示
        const topAlert = document.getElementById('top-alert') || createTopAlert();
        topAlert.innerHTML = '';
        topAlert.appendChild(alertDiv);
    }
}

// 创建顶部提示区域
function createTopAlert() {
    const alertDiv = document.createElement('div');
    alertDiv.id = 'top-alert';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.maxWidth = '400px';
    document.body.appendChild(alertDiv);
    return alertDiv;
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': '待开始',
        'active': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}

// 获取操作文本
function getActionText(action) {
    const actionMap = {
        'unlock': '解锁',
        'lock': '锁定',
        'access_granted': '允许访问',
        'access_denied': '拒绝访问'
    };
    return actionMap[action] || action;
}