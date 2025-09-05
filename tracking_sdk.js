/**
 * 页面埋点JavaScript SDK
 * 用于收集用户行为数据并发送到后端API
 */

class TrackingSDK {
    constructor(config = {}) {
        // 默认配置
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:5000/api',
            apiKey: config.apiKey || '',
            userId: config.userId || null,
            sessionId: config.sessionId || this.generateSessionId(),
            debug: config.debug || false,
            autoTrack: config.autoTrack !== false, // 默认启用自动跟踪
            batchSize: config.batchSize || 10, // 批量发送大小
            flushInterval: config.flushInterval || 5000, // 批量发送间隔（毫秒）
            ...config
        };
        
        // 事件队列
        this.eventQueue = [];
        this.pageViewStartTime = Date.now();
        this.scrollDepth = 0;
        this.maxScrollDepth = 0;
        
        // 初始化
        this.init();
    }
    
    /**
     * 生成会话ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * 初始化SDK
     */
    init() {
        if (this.config.debug) {
            console.log('🔍 TrackingSDK 初始化', this.config);
        }
        
        // 设置页面可见性变化监听
        this.setupVisibilityChange();
        
        // 设置页面卸载监听
        this.setupBeforeUnload();
        
        // 设置滚动监听
        this.setupScrollTracking();
        
        // 设置点击监听
        this.setupClickTracking();
        
        // 设置表单提交监听
        this.setupFormTracking();
        
        // 自动跟踪页面访问
        if (this.config.autoTrack) {
            this.trackPageView();
        }
        
        // 启动批量发送定时器
        this.startBatchTimer();
    }
    
    /**
     * 设置页面可见性变化监听
     */
    setupVisibilityChange() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.trackEvent('page_hide', {
                    duration: Date.now() - this.pageViewStartTime
                });
            } else {
                this.pageViewStartTime = Date.now();
                this.trackEvent('page_show');
            }
        });
    }
    
    /**
     * 设置页面卸载监听
     */
    setupBeforeUnload() {
        window.addEventListener('beforeunload', () => {
            this.trackEvent('page_unload', {
                duration: Date.now() - this.pageViewStartTime
            });
            this.flush(); // 立即发送所有待发送的事件
        });
    }
    
    /**
     * 设置滚动监听
     */
    setupScrollTracking() {
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.updateScrollDepth();
            }, 100);
        });
    }
    
    /**
     * 更新滚动深度
     */
    updateScrollDepth() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollDepth = documentHeight > 0 ? (scrollTop / documentHeight) * 100 : 0;
        
        this.scrollDepth = Math.min(scrollDepth, 100);
        this.maxScrollDepth = Math.max(this.maxScrollDepth, this.scrollDepth);
        
        // 每25%滚动深度记录一次事件
        const milestones = [25, 50, 75, 100];
        const currentMilestone = milestones.find(m => 
            this.scrollDepth >= m && this.scrollDepth < m + 25
        );
        
        if (currentMilestone && this.scrollDepth === this.maxScrollDepth) {
            this.trackEvent('scroll', {
                scroll_depth: this.scrollDepth,
                milestone: currentMilestone
            });
        }
    }
    
    /**
     * 设置点击监听
     */
    setupClickTracking() {
        document.addEventListener('click', (event) => {
            const element = event.target;
            const rect = element.getBoundingClientRect();
            
            this.trackEvent('click', {
                element_id: element.id || null,
                element_class: element.className || null,
                element_tag: element.tagName.toLowerCase(),
                element_text: this.getElementText(element),
                x_position: Math.round(event.clientX),
                y_position: Math.round(event.clientY),
                page_x: Math.round(event.pageX),
                page_y: Math.round(event.pageY)
            });
        });
    }
    
    /**
     * 设置表单监听
     */
    setupFormTracking() {
        // 表单提交
        document.addEventListener('submit', (event) => {
            const form = event.target;
            this.trackEvent('form_submit', {
                form_id: form.id || null,
                form_class: form.className || null,
                form_action: form.action || null,
                form_method: form.method || 'get'
            });
        });
        
        // 表单字段聚焦
        document.addEventListener('focus', (event) => {
            const element = event.target;
            if (['input', 'textarea', 'select'].includes(element.tagName.toLowerCase())) {
                this.trackEvent('form_focus', {
                    field_name: element.name || null,
                    field_type: element.type || null,
                    field_id: element.id || null
                });
            }
        }, true);
    }
    
    /**
     * 获取元素文本内容
     */
    getElementText(element) {
        if (element.textContent) {
            return element.textContent.trim().substring(0, 100);
        }
        if (element.value) {
            return element.value.trim().substring(0, 100);
        }
        if (element.alt) {
            return element.alt.trim().substring(0, 100);
        }
        if (element.title) {
            return element.title.trim().substring(0, 100);
        }
        return null;
    }
    
    /**
     * 跟踪页面访问
     */
    trackPageView(customData = {}) {
        const pageData = {
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer || null,
            screen_resolution: `${screen.width}x${screen.height}`,
            viewport_size: `${window.innerWidth}x${window.innerHeight}`,
            load_time: performance.timing ? 
                performance.timing.loadEventEnd - performance.timing.navigationStart : null,
            ...customData
        };
        
        this.sendToAPI('/track/pageview', pageData);
    }
    
    /**
     * 跟踪自定义事件
     */
    trackEvent(eventType, customData = {}) {
        const eventData = {
            event_type: eventType,
            page_url: window.location.href,
            page_title: document.title,
            scroll_depth: this.scrollDepth,
            ...customData
        };
        
        this.addToQueue(eventData);
    }
    
    /**
     * 添加事件到队列
     */
    addToQueue(eventData) {
        this.eventQueue.push({
            ...eventData,
            timestamp: new Date().toISOString(),
            user_id: this.config.userId,
            session_id: this.config.sessionId
        });
        
        if (this.config.debug) {
            console.log('📊 事件已添加到队列:', eventData);
        }
        
        // 如果队列达到批量大小，立即发送
        if (this.eventQueue.length >= this.config.batchSize) {
            this.flush();
        }
    }
    
    /**
     * 发送数据到API
     */
    async sendToAPI(endpoint, data) {
        try {
            const response = await fetch(this.config.apiUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.config.apiKey && { 'X-API-Key': this.config.apiKey })
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (this.config.debug) {
                console.log('✅ 数据发送成功:', result);
            }
            
            return result;
        } catch (error) {
            console.error('❌ 数据发送失败:', error);
            return null;
        }
    }
    
    /**
     * 批量发送事件
     */
    async flush() {
        if (this.eventQueue.length === 0) {
            return;
        }
        
        const events = [...this.eventQueue];
        this.eventQueue = [];
        
        try {
            const result = await this.sendToAPI('/track/batch', { events });
            
            if (this.config.debug) {
                console.log('📦 批量事件发送完成:', result);
            }
        } catch (error) {
            console.error('❌ 批量事件发送失败:', error);
            // 发送失败的事件重新加入队列
            this.eventQueue.unshift(...events);
        }
    }
    
    /**
     * 启动批量发送定时器
     */
    startBatchTimer() {
        setInterval(() => {
            this.flush();
        }, this.config.flushInterval);
    }
    
    /**
     * 设置用户ID
     */
    setUserId(userId) {
        this.config.userId = userId;
    }
    
    /**
     * 获取会话ID
     */
    getSessionId() {
        return this.config.sessionId;
    }
    
    /**
     * 获取队列长度
     */
    getQueueLength() {
        return this.eventQueue.length;
    }
    
    /**
     * 手动发送所有待发送事件
     */
    forceFlush() {
        this.flush();
    }
    
    /**
     * 销毁SDK
     */
    destroy() {
        this.flush();
        // 清理事件监听器等资源
        // 这里可以根据需要添加清理逻辑
    }
}

// 全局实例
let trackingInstance = null;

/**
 * 初始化埋点SDK
 */
function initTracking(config = {}) {
    if (trackingInstance) {
        console.warn('⚠️ TrackingSDK 已经初始化');
        return trackingInstance;
    }
    
    trackingInstance = new TrackingSDK(config);
    return trackingInstance;
}

/**
 * 获取埋点实例
 */
function getTracking() {
    if (!trackingInstance) {
        console.warn('⚠️ TrackingSDK 未初始化，请先调用 initTracking()');
        return null;
    }
    return trackingInstance;
}

// 导出到全局作用域
if (typeof window !== 'undefined') {
    window.TrackingSDK = TrackingSDK;
    window.initTracking = initTracking;
    window.getTracking = getTracking;
}

// 如果是模块环境，导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        TrackingSDK,
        initTracking,
        getTracking
    };
}