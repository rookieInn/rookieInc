class ChatApp {
    constructor() {
        this.currentUser = '用户';
        this.messages = [];
        this.userCounter = 1;
        
        this.initializeElements();
        this.bindEvents();
        this.loadMessages();
        this.updateUserDisplay();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.exportBtn = document.getElementById('export-btn');
        this.changeUserBtn = document.getElementById('change-user-btn');
        this.currentUserSpan = document.getElementById('current-user');
    }
    
    bindEvents() {
        // 发送消息事件
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 清空聊天
        this.clearBtn.addEventListener('click', () => this.clearMessages());
        
        // 导出聊天记录
        this.exportBtn.addEventListener('click', () => this.exportMessages());
        
        // 切换用户
        this.changeUserBtn.addEventListener('click', () => this.changeUser());
        
        // 输入框自动调整高度
        this.messageInput.addEventListener('input', () => this.adjustInputHeight());
    }
    
    sendMessage() {
        const messageText = this.messageInput.value.trim();
        if (!messageText) return;
        
        const message = {
            id: Date.now(),
            text: messageText,
            sender: this.currentUser,
            timestamp: new Date(),
            isOwn: true
        };
        
        this.addMessage(message);
        this.messages.push(message);
        this.saveMessages();
        
        this.messageInput.value = '';
        this.adjustInputHeight();
        
        // 模拟自动回复（可选）
        setTimeout(() => this.generateAutoReply(message), 1000 + Math.random() * 2000);
    }
    
    addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.isOwn ? 'own' : 'other'}`;
        messageElement.innerHTML = `
            <div class="message-content">${this.escapeHtml(message.text)}</div>
            <div class="message-info">
                <span class="message-sender">${message.sender}</span>
                <span class="message-time">${this.formatTime(message.timestamp)}</span>
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    generateAutoReply(originalMessage) {
        const replies = [
            '收到！',
            '好的，我明白了',
            '很有趣的观点',
            '让我想想...',
            '你说得对',
            '我同意你的看法',
            '这确实是个好问题',
            '谢谢分享',
            '我也有同样的想法',
            '很有道理'
        ];
        
        const reply = replies[Math.floor(Math.random() * replies.length)];
        const autoMessage = {
            id: Date.now(),
            text: reply,
            sender: 'AI助手',
            timestamp: new Date(),
            isOwn: false
        };
        
        this.addMessage(autoMessage);
        this.messages.push(autoMessage);
        this.saveMessages();
    }
    
    clearMessages() {
        if (confirm('确定要清空所有聊天记录吗？')) {
            this.messages = [];
            this.chatMessages.innerHTML = '<div class="empty-state">开始你的对话吧！</div>';
            this.saveMessages();
        }
    }
    
    exportMessages() {
        if (this.messages.length === 0) {
            alert('没有聊天记录可以导出');
            return;
        }
        
        const exportData = {
            exportTime: new Date().toISOString(),
            totalMessages: this.messages.length,
            messages: this.messages.map(msg => ({
                sender: msg.sender,
                text: msg.text,
                timestamp: msg.timestamp.toISOString()
            }))
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }
    
    changeUser() {
        const newUser = prompt('请输入新的用户名:', this.currentUser);
        if (newUser && newUser.trim()) {
            this.currentUser = newUser.trim();
            this.updateUserDisplay();
        }
    }
    
    updateUserDisplay() {
        this.currentUserSpan.textContent = this.currentUser;
    }
    
    loadMessages() {
        const saved = localStorage.getItem('chatMessages');
        if (saved) {
            try {
                this.messages = JSON.parse(saved).map(msg => ({
                    ...msg,
                    timestamp: new Date(msg.timestamp)
                }));
                this.renderMessages();
            } catch (e) {
                console.error('加载聊天记录失败:', e);
                this.messages = [];
            }
        }
        
        if (this.messages.length === 0) {
            this.chatMessages.innerHTML = '<div class="empty-state">开始你的对话吧！</div>';
        }
    }
    
    renderMessages() {
        this.chatMessages.innerHTML = '';
        this.messages.forEach(message => this.addMessage(message));
    }
    
    saveMessages() {
        localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    adjustInputHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    formatTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        
        if (diff < 60000) { // 1分钟内
            return '刚刚';
        } else if (diff < 3600000) { // 1小时内
            return `${Math.floor(diff / 60000)}分钟前`;
        } else if (diff < 86400000) { // 24小时内
            return time.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } else {
            return time.toLocaleDateString('zh-CN') + ' ' + 
                   time.toLocaleTimeString('zh-CN', { 
                       hour: '2-digit', 
                       minute: '2-digit' 
                   });
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 页面加载完成后初始化聊天应用
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// 添加一些实用功能
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter 快速发送
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const messageInput = document.getElementById('message-input');
        if (document.activeElement === messageInput) {
            e.preventDefault();
            document.getElementById('send-btn').click();
        }
    }
});

// 防止页面刷新时丢失焦点
window.addEventListener('beforeunload', () => {
    const messageInput = document.getElementById('message-input');
    if (messageInput.value.trim()) {
        return '您有未发送的消息，确定要离开吗？';
    }
});