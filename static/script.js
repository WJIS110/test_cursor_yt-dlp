/**
 * Video Downloader 前端邏輯
 * 處理表單提交、API 調用和 UI 更新
 */

// DOM 元素
const downloadForm = document.getElementById('downloadForm');
const videoUrlInput = document.getElementById('videoUrl');
const formatTypeSelect = document.getElementById('formatType');
const infoBtn = document.getElementById('infoBtn');
const downloadBtn = document.getElementById('downloadBtn');
const statusMessage = document.getElementById('statusMessage');
const infoSection = document.getElementById('infoSection');
const videoInfo = document.getElementById('videoInfo');
const filesList = document.getElementById('filesList');
const refreshFilesBtn = document.getElementById('refreshFilesBtn');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('Video Downloader 前端已載入');
    loadFilesList();
    
    // 綁定事件監聽器
    downloadForm.addEventListener('submit', handleDownload);
    infoBtn.addEventListener('click', handleGetInfo);
    refreshFilesBtn.addEventListener('click', loadFilesList);
});

/**
 * 顯示狀態訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 ('success', 'error', 'info')
 */
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-${type}`;
}

/**
 * 設定按鈕載入狀態
 * @param {HTMLButtonElement} button - 按鈕元素
 * @param {boolean} loading - 是否為載入狀態
 * @param {string} loadingText - 載入時顯示的文字
 */
function setButtonLoading(button, loading, loadingText = '處理中...') {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = loadingText;
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

/**
 * 處理下載請求
 * @param {Event} event - 表單提交事件
 */
async function handleDownload(event) {
    event.preventDefault();
    
    const url = videoUrlInput.value.trim();
    const formatType = formatTypeSelect.value;
    
    if (!url) {
        showStatus('請輸入有效的影片連結', 'error');
        return;
    }
    
    setButtonLoading(downloadBtn, true, '下載中...');
    showStatus('開始下載影片...', 'info');
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                format_type: formatType
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showStatus(`下載成功！檔案: ${result.title}`, 'success');
            // 重新載入檔案列表
            loadFilesList();
            // 清空表單
            videoUrlInput.value = '';
        } else {
            showStatus(`下載失敗: ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error('下載錯誤:', error);
        showStatus('下載過程中發生錯誤，請稍後再試', 'error');
    } finally {
        setButtonLoading(downloadBtn, false);
    }
}

/**
 * 處理獲取影片資訊請求
 */
async function handleGetInfo() {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        showStatus('請輸入有效的影片連結', 'error');
        return;
    }
    
    setButtonLoading(infoBtn, true, '獲取中...');
    showStatus('正在獲取影片資訊...', 'info');
    
    try {
        const response = await fetch('/info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayVideoInfo(result);
            showStatus('影片資訊獲取成功', 'success');
        } else {
            showStatus(`獲取資訊失敗: ${result.message}`, 'error');
            hideVideoInfo();
        }
        
    } catch (error) {
        console.error('獲取資訊錯誤:', error);
        showStatus('獲取影片資訊時發生錯誤', 'error');
        hideVideoInfo();
    } finally {
        setButtonLoading(infoBtn, false);
    }
}

/**
 * 顯示影片資訊
 * @param {Object} info - 影片資訊物件
 */
function displayVideoInfo(info) {
    const infoHtml = `
        <div class="info-item">
            <span class="info-label">標題:</span> ${info.title || 'N/A'}
        </div>
        <div class="info-item">
            <span class="info-label">上傳者:</span> ${info.uploader || 'N/A'}
        </div>
        <div class="info-item">
            <span class="info-label">時長:</span> ${formatDuration(info.duration) || 'N/A'}
        </div>
        <div class="info-item">
            <span class="info-label">觀看次數:</span> ${formatNumber(info.view_count) || 'N/A'}
        </div>
        <div class="info-item">
            <span class="info-label">上傳日期:</span> ${formatDate(info.upload_date) || 'N/A'}
        </div>
    `;
    
    videoInfo.innerHTML = infoHtml;
    infoSection.style.display = 'block';
}

/**
 * 隱藏影片資訊
 */
function hideVideoInfo() {
    infoSection.style.display = 'none';
}

/**
 * 載入已下載檔案列表
 */
async function loadFilesList() {
    try {
        const response = await fetch('/files');
        const result = await response.json();
        
        if (result.files && result.files.length > 0) {
            displayFilesList(result.files);
        } else {
            filesList.innerHTML = '<p style="padding: 20px; text-align: center; color: #7f8c8d;">尚無下載檔案</p>';
        }
        
    } catch (error) {
        console.error('載入檔案列表錯誤:', error);
        filesList.innerHTML = '<p style="padding: 20px; text-align: center; color: #e74c3c;">載入檔案列表失敗</p>';
    }
}

/**
 * 顯示檔案列表
 * @param {Array} files - 檔案陣列
 */
function displayFilesList(files) {
    const filesHtml = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.name)}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <div class="file-actions">
                <a href="${file.download_url}" class="download-link" download>下載</a>
            </div>
        </div>
    `).join('');
    
    filesList.innerHTML = filesHtml;
}

/**
 * 格式化檔案大小
 * @param {number} bytes - 位元組大小
 * @returns {string} 格式化後的大小字串
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化時長（秒轉為時:分:秒）
 * @param {number} seconds - 秒數
 * @returns {string} 格式化後的時長
 */
function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

/**
 * 格式化數字（添加千分位符號）
 * @param {number} num - 數字
 * @returns {string} 格式化後的數字字串
 */
function formatNumber(num) {
    if (!num) return 'N/A';
    return num.toLocaleString();
}

/**
 * 格式化日期
 * @param {string} dateStr - 日期字串 (YYYYMMDD 格式)
 * @returns {string} 格式化後的日期
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    
    return `${year}-${month}-${day}`;
}

/**
 * HTML 特殊字元轉義
 * @param {string} text - 原始文字
 * @returns {string} 轉義後的文字
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}