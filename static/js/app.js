// 全局状态
let currentFile = null;
let currentOutDir = null;
let pollingInterval = null;

// DOM 元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadPreview = document.getElementById('uploadPreview');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeBtn');
const startBtn = document.getElementById('startBtn');
const maxLoopsSlider = document.getElementById('maxLoops');
const thresholdSlider = document.getElementById('threshold');
const maxLoopsValue = document.getElementById('maxLoopsValue');
const thresholdValue = document.getElementById('thresholdValue');

const uploadSection = document.getElementById('uploadSection');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');

const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const currentStep = document.getElementById('currentStep');
const logOutput = document.getElementById('logOutput');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initUploadHandlers();
    initSliders();
    initButtons();
});

// 上传处理
function initUploadHandlers() {
    // 点击上传
    uploadArea.addEventListener('click', (e) => {
        if (e.target !== removeBtn && !removeBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    // 文件选择
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileSelect(file);
        }
    });

    // 移除文件
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });
}

// 处理文件选择
function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        showNotification('请选择图片文件', 'error');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showNotification('文件大小不能超过 16MB', 'error');
        return;
    }

    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadPreview.style.display = 'flex';
        uploadArea.querySelector('.upload-placeholder').style.display = 'none';
        startBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// 清除文件
function clearFile() {
    currentFile = null;
    fileInput.value = '';
    uploadPreview.style.display = 'none';
    uploadArea.querySelector('.upload-placeholder').style.display = 'block';
    startBtn.disabled = true;
}

// 滑块处理
function initSliders() {
    maxLoopsSlider.addEventListener('input', (e) => {
        maxLoopsValue.textContent = e.target.value;
    });

    thresholdSlider.addEventListener('input', (e) => {
        thresholdValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
}

// 按钮处理
function initButtons() {
    startBtn.addEventListener('click', startTask);
    
    document.getElementById('copyCodeBtn')?.addEventListener('click', copyCode);
    document.getElementById('downloadCodeBtn')?.addEventListener('click', downloadCode);
    document.getElementById('newTaskBtn')?.addEventListener('click', resetToUpload);
}

// 开始任务
async function startTask() {
    if (!currentFile) {
        showNotification('请先上传图片', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('max_loops', maxLoopsSlider.value);
    formData.append('threshold', thresholdSlider.value);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentOutDir = data.out_dir;
            showProgressSection();
            startPolling();
        } else {
            showNotification(data.error || '上传失败', 'error');
        }
    } catch (error) {
        showNotification('网络错误: ' + error.message, 'error');
    }
}

// 显示进度区域
function showProgressSection() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    
    // 重置进度
    updateProgress(0, '准备中...');
    logOutput.innerHTML = '';
    
    // 重置智能体节点状态
    document.querySelectorAll('.agent-node').forEach(node => {
        node.classList.remove('active', 'completed');
    });
}

// 开始轮询状态
function startPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/status');
            const status = await response.json();
            
            updateUI(status);
            
            if (!status.running && status.result) {
                clearInterval(pollingInterval);
                setTimeout(() => showResults(status.result), 1000);
            }
        } catch (error) {
            console.error('轮询错误:', error);
        }
    }, 1000);
}

// 更新 UI
function updateUI(status) {
    // 更新进度条
    updateProgress(status.progress, status.current_step);
    
    // 更新日志
    updateLogs(status.logs);
    
    // 更新智能体节点状态
    updateAgentNodes(status.current_step);
}

// 更新进度
function updateProgress(progress, step) {
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `${Math.round(progress)}%`;
    currentStep.textContent = step;
}

// 更新日志
function updateLogs(logs) {
    if (!logs || logs.length === 0) return;
    
    const currentLogCount = logOutput.children.length;
    
    if (logs.length > currentLogCount) {
        for (let i = currentLogCount; i < logs.length; i++) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-time">${logs[i].time}</span>
                <span class="log-message">${logs[i].message}</span>
            `;
            logOutput.appendChild(logEntry);
        }
        
        // 滚动到底部
        logOutput.scrollTop = logOutput.scrollHeight;
    }
}

// 更新智能体节点
function updateAgentNodes(currentStep) {
    const nodes = document.querySelectorAll('.agent-node');
    
    nodes.forEach((node, index) => {
        const agentNum = index + 1;
        
        if (currentStep.includes(`Agent${agentNum}`) || 
            currentStep.includes(`A${agentNum}`)) {
            node.classList.add('active');
            node.classList.remove('completed');
        } else if (isAgentCompleted(currentStep, agentNum)) {
            node.classList.add('completed');
            node.classList.remove('active');
        }
    });
}

// 判断智能体是否完成
function isAgentCompleted(currentStep, agentNum) {
    const steps = [
        'Agent1', '代码生成',
        'Agent2', '视觉评判',
        'Agent3', '代码评估',
        'Agent4', '反馈优化',
        '验证器'
    ];
    
    const currentIndex = steps.findIndex(s => currentStep.includes(s));
    const agentIndex = (agentNum - 1) * 2;
    
    return currentIndex > agentIndex + 1;
}

// 显示结果
function showResults(result) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // 设置结果徽章
    const badge = document.getElementById('resultBadge');
    if (result.success) {
        badge.textContent = '✅ 成功';
        badge.className = 'result-badge success';
    } else {
        badge.textContent = '❌ 失败';
        badge.className = 'result-badge error';
    }
    
    // 设置图片
    if (result.png_path) {
        const pngFilename = result.png_path.split(/[\\/]/).pop();
        document.getElementById('generatedImage').src = `/results/${pngFilename}`;
    }
    
    // 如果有原图，也显示
    const uploadImgSrc = previewImage.src;
    if (uploadImgSrc && uploadImgSrc.startsWith('data:')) {
        document.getElementById('originalImage').src = uploadImgSrc;
    }
    
    // 设置结果信息
    document.getElementById('validationStatus').textContent = result.success ? '通过' : '未通过';
    document.getElementById('similarityScore').textContent = result.summary ? 
        extractScore(result.summary) : '-';
    document.getElementById('summaryText').textContent = result.summary || '无摘要';
    
    // 加载代码
    if (result.code_path) {
        const codeFilename = result.code_path.split(/[\\/]/).pop();
        loadCode(codeFilename);
    }
}

// 提取分数
function extractScore(summary) {
    const match = summary.match(/score[=:]\s*([\d.]+)/i);
    return match ? parseFloat(match[1]).toFixed(4) : '-';
}

// 加载代码
async function loadCode(filename) {
    try {
        const response = await fetch(`/code/${filename}`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('codeContent').textContent = data.content;
        }
    } catch (error) {
        console.error('加载代码失败:', error);
    }
}

// 复制代码
function copyCode() {
    const codeContent = document.getElementById('codeContent').textContent;
    
    navigator.clipboard.writeText(codeContent).then(() => {
        showNotification('代码已复制到剪贴板', 'success');
    }).catch(err => {
        showNotification('复制失败: ' + err, 'error');
    });
}

// 下载代码
function downloadCode() {
    const codeContent = document.getElementById('codeContent').textContent;
    const blob = new Blob([codeContent], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'echarts_chart.js';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('代码下载成功', 'success');
}

// 重置到上传界面
function resetToUpload() {
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    
    clearFile();
    
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // 添加样式
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 25px',
        borderRadius: '12px',
        color: 'white',
        fontWeight: '600',
        fontSize: '14px',
        zIndex: '10000',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
        animation: 'slideIn 0.3s ease',
        background: type === 'success' ? 
            'linear-gradient(135deg, #10b981, #059669)' :
            type === 'error' ? 
            'linear-gradient(135deg, #ef4444, #dc2626)' :
            'linear-gradient(135deg, #6366f1, #8b5cf6)'
    });
    
    document.body.appendChild(notification);
    
    // 3秒后移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
