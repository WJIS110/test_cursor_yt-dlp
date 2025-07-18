// 视频下载器前端应用
class VideoDownloaderApp {
    constructor() {
        this.jobs = new Map(); // 存储任务数据
        this.websocket = null;
        this.autoRefreshInterval = null;
        
        this.init();
    }

    init() {
        console.log('🚀 初始化视频下载器应用');
        
        // 绑定事件监听器
        this.bindEventListeners();
        
        // 连接 WebSocket
        this.connectWebSocket();
        
        // 加载初始任务列表
        this.loadJobs();
        
        // 开始自动刷新
        this.startAutoRefresh();
    }

    bindEventListeners() {
        // 下载表单提交
        const downloadForm = document.getElementById('downloadForm');
        downloadForm.addEventListener('submit', (e) => this.handleDownloadSubmit(e));

        // 刷新按钮
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.addEventListener('click', () => this.loadJobs());

        // 清理已完成按钮
        const clearCompletedBtn = document.getElementById('clearCompletedBtn');
        clearCompletedBtn.addEventListener('click', () => this.clearCompleted());

        // 模态框关闭
        const modal = document.getElementById('videoInfoModal');
        const closeBtn = modal.querySelector('.close');
        closeBtn.addEventListener('click', () => this.hideModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.hideModal();
        });
    }

    // WebSocket 连接
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('📡 WebSocket 连接已建立');
                this.showStatus('WebSocket 连接成功', 'success');
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                console.log('📡 WebSocket 连接已关闭');
                this.showStatus('WebSocket 连接断开，尝试重连...', 'error');
                
                // 5 秒后重连
                setTimeout(() => this.connectWebSocket(), 5000);
            };

            this.websocket.onerror = (error) => {
                console.error('📡 WebSocket 错误:', error);
                this.showStatus('WebSocket 连接错误', 'error');
            };
        } catch (error) {
            console.error('📡 WebSocket 连接失败:', error);
            this.showStatus('WebSocket 连接失败', 'error');
        }
    }

    // 处理 WebSocket 消息
    handleWebSocketMessage(data) {
        console.log('📨 收到 WebSocket 消息:', data);
        
        if (data.job_id) {
            // 更新任务状态
            this.jobs.set(data.job_id, data);
            this.updateJobDisplay(data);
        }
    }

    // 表单提交处理
    async handleDownloadSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const request = {
            url: formData.get('url'),
            format: formData.get('format'),
            audio_only: formData.has('audioOnly')
        };

        console.log('📥 提交下载请求:', request);

        try {
            // 显示加载状态
            const submitBtn = event.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '提交中...';
            submitBtn.disabled = true;

            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ 下载任务创建成功:', result);
                
                this.showStatus(`任务创建成功: ${result.job_id.slice(0, 8)}`, 'success');
                
                // 清空表单
                event.target.reset();
                
                // 刷新任务列表
                this.loadJobs();
            } else {
                const error = await response.json();
                console.error('❌ 下载任务创建失败:', error);
                this.showStatus(`创建失败: ${error.detail || '未知错误'}`, 'error');
            }
        } catch (error) {
            console.error('❌ 请求错误:', error);
            this.showStatus('网络错误，请检查连接', 'error');
        } finally {
            // 恢复按钮状态
            const submitBtn = event.target.querySelector('button[type="submit"]');
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    // 加载任务列表
    async loadJobs() {
        try {
            console.log('📋 加载任务列表...');
            
            const response = await fetch('/api/downloads');
            if (response.ok) {
                const jobs = await response.json();
                console.log('✅ 任务列表加载成功:', jobs);
                
                // 更新本地存储
                this.jobs.clear();
                jobs.forEach(job => {
                    this.jobs.set(job.job_id, job);
                });
                
                // 更新显示
                this.renderJobsList();
            } else {
                console.error('❌ 加载任务列表失败');
                this.showStatus('加载任务列表失败', 'error');
            }
        } catch (error) {
            console.error('❌ 加载任务列表错误:', error);
            this.showStatus('网络错误，无法加载任务列表', 'error');
        }
    }

    // 渲染任务列表
    renderJobsList() {
        const container = document.getElementById('jobsList');
        
        if (this.jobs.size === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">暂无下载任务</p>';
            return;
        }

        const jobsArray = Array.from(this.jobs.values());
        // 按创建时间倒序排列
        jobsArray.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        container.innerHTML = jobsArray.map(job => this.createJobHTML(job)).join('');
        
        // 绑定任务操作事件
        this.bindJobActions();
    }

    // 创建任务HTML
    createJobHTML(job) {
        const progress = job.progress || 0;
        const status = job.status;
        const title = job.title || '未知标题';
        const filename = job.filename || '';
        const speed = job.speed || '';
        const eta = job.eta || '';
        const errorMessage = job.error_message || '';

        return `
            <div class="job-item ${status}" data-job-id="${job.job_id}">
                <div class="job-header">
                    <div class="job-title">${this.escapeHtml(title)}</div>
                    <div class="job-status ${status}">${this.getStatusText(status)}</div>
                </div>
                
                <div class="job-url">${this.escapeHtml(job.url)}</div>
                
                ${progress > 0 || status === 'downloading' ? `
                    <div class="job-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <div class="progress-text">
                            <span>${progress.toFixed(1)}%</span>
                            <span>${speed} ${eta ? '• ' + eta : ''}</span>
                        </div>
                    </div>
                ` : ''}
                
                ${filename ? `<div class="job-filename">📄 ${this.escapeHtml(filename)}</div>` : ''}
                
                ${errorMessage ? `<div class="job-error" style="color: #dc3545; margin-top: 8px;">❌ ${this.escapeHtml(errorMessage)}</div>` : ''}
                
                <div class="job-actions">
                    ${status === 'downloading' ? `
                        <button class="btn-secondary cancel-btn" data-job-id="${job.job_id}">❌ 取消</button>
                    ` : ''}
                    
                    ${status === 'completed' && filename ? `
                        <button class="btn-secondary download-btn" data-job-id="${job.job_id}">📥 下载文件</button>
                    ` : ''}
                    
                    <button class="btn-secondary info-btn" data-job-id="${job.job_id}">ℹ️ 详情</button>
                    <button class="btn-secondary delete-btn" data-job-id="${job.job_id}">🗑️ 删除</button>
                </div>
            </div>
        `;
    }

    // 更新单个任务显示
    updateJobDisplay(job) {
        const existingElement = document.querySelector(`[data-job-id="${job.job_id}"]`);
        if (existingElement) {
            const newHTML = this.createJobHTML(job);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newHTML;
            const newElement = tempDiv.firstElementChild;
            
            existingElement.replaceWith(newElement);
            this.bindJobActionsForElement(newElement);
        } else {
            // 如果不存在，重新渲染整个列表
            this.renderJobsList();
        }
    }

    // 绑定任务操作事件
    bindJobActions() {
        const container = document.getElementById('jobsList');
        
        // 取消按钮
        container.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.cancelJob(e.target.dataset.jobId));
        });

        // 下载文件按钮
        container.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.downloadFile(e.target.dataset.jobId));
        });

        // 详情按钮
        container.querySelectorAll('.info-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.showJobInfo(e.target.dataset.jobId));
        });

        // 删除按钮
        container.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteJob(e.target.dataset.jobId));
        });
    }

    // 为单个元素绑定事件
    bindJobActionsForElement(element) {
        element.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.cancelJob(e.target.dataset.jobId));
        });

        element.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.downloadFile(e.target.dataset.jobId));
        });

        element.querySelectorAll('.info-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.showJobInfo(e.target.dataset.jobId));
        });

        element.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteJob(e.target.dataset.jobId));
        });
    }

    // 取消任务
    async cancelJob(jobId) {
        try {
            const response = await fetch(`/api/download/${jobId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showStatus('任务已取消', 'info');
                this.loadJobs();
            } else {
                this.showStatus('取消失败', 'error');
            }
        } catch (error) {
            console.error('取消任务错误:', error);
            this.showStatus('取消失败', 'error');
        }
    }

    // 下载文件
    downloadFile(jobId) {
        const url = `/api/download/${jobId}/file`;
        const link = document.createElement('a');
        link.href = url;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // 显示任务详情
    showJobInfo(jobId) {
        const job = this.jobs.get(jobId);
        if (!job) return;

        const content = document.getElementById('videoInfoContent');
        content.innerHTML = `
            <p><strong>任务ID:</strong> ${job.job_id}</p>
            <p><strong>链接:</strong> ${this.escapeHtml(job.url)}</p>
            <p><strong>状态:</strong> ${this.getStatusText(job.status)}</p>
            <p><strong>进度:</strong> ${job.progress || 0}%</p>
            <p><strong>创建时间:</strong> ${new Date(job.created_at).toLocaleString()}</p>
            <p><strong>更新时间:</strong> ${new Date(job.updated_at).toLocaleString()}</p>
            ${job.title ? `<p><strong>标题:</strong> ${this.escapeHtml(job.title)}</p>` : ''}
            ${job.filename ? `<p><strong>文件名:</strong> ${this.escapeHtml(job.filename)}</p>` : ''}
            ${job.speed ? `<p><strong>下载速度:</strong> ${job.speed}</p>` : ''}
            ${job.eta ? `<p><strong>预计剩余:</strong> ${job.eta}</p>` : ''}
            ${job.error_message ? `<p><strong>错误信息:</strong> <span style="color: #dc3545;">${this.escapeHtml(job.error_message)}</span></p>` : ''}
        `;

        this.showModal();
    }

    // 删除任务
    async deleteJob(jobId) {
        if (!confirm('确定要删除这个任务吗？')) return;

        try {
            const response = await fetch(`/api/download/${jobId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.jobs.delete(jobId);
                this.renderJobsList();
                this.showStatus('任务已删除', 'info');
            } else {
                this.showStatus('删除失败', 'error');
            }
        } catch (error) {
            console.error('删除任务错误:', error);
            this.showStatus('删除失败', 'error');
        }
    }

    // 清理已完成任务
    async clearCompleted() {
        const completedJobs = Array.from(this.jobs.values())
            .filter(job => job.status === 'completed' || job.status === 'failed');

        if (completedJobs.length === 0) {
            this.showStatus('没有已完成的任务', 'info');
            return;
        }

        if (!confirm(`确定要清理 ${completedJobs.length} 个已完成的任务吗？`)) return;

        const promises = completedJobs.map(job => 
            fetch(`/api/download/${job.job_id}`, { method: 'DELETE' })
        );

        try {
            await Promise.all(promises);
            this.loadJobs();
            this.showStatus('已完成任务已清理', 'success');
        } catch (error) {
            console.error('清理任务错误:', error);
            this.showStatus('清理失败', 'error');
        }
    }

    // 显示状态消息
    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusMessage');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;
        statusElement.classList.remove('hidden');

        // 3秒后隐藏
        setTimeout(() => {
            statusElement.classList.add('hidden');
        }, 3000);
    }

    // 显示模态框
    showModal() {
        const modal = document.getElementById('videoInfoModal');
        modal.classList.remove('hidden');
    }

    // 隐藏模态框
    hideModal() {
        const modal = document.getElementById('videoInfoModal');
        modal.classList.add('hidden');
    }

    // 开始自动刷新
    startAutoRefresh() {
        // 每10秒刷新一次任务列表
        this.autoRefreshInterval = setInterval(() => {
            this.loadJobs();
        }, 10000);
    }

    // 停止自动刷新
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    // 工具函数
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '等待中',
            'downloading': '下载中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VideoDownloaderApp();
});