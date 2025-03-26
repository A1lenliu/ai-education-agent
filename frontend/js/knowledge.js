// DOM 元素
let uploadForm;
let knowledgeFile;
let uploadMessage;
let knowledgeCount;
let searchInput;
let knowledgePreview;
let backToDashboard;
let logoutBtn;

// 初始化 DOM 元素
function initializeDOMElements() {
    uploadForm = document.getElementById('uploadForm');
    knowledgeFile = document.getElementById('knowledgeFile');
    uploadMessage = document.getElementById('uploadMessage');
    knowledgeCount = document.getElementById('knowledgeCount');
    searchInput = document.getElementById('searchInput');
    knowledgePreview = document.getElementById('knowledgePreview');
    backToDashboard = document.getElementById('backToDashboard');
    logoutBtn = document.getElementById('logoutBtn');
}

// 文件选择处理
function handleFileSelect(e) {
    const fileName = e.target.files[0]?.name || '未选择文件';
    document.querySelector('.file-name').textContent = fileName;
}

// 文件上传处理
function handleFileUpload(e) {
    e.preventDefault();
    const file = knowledgeFile.files[0];

    if (!file) {
        showMessage('请选择要上传的文件', true);
        return;
    }

    if (!file.name.endsWith('.txt')) {
        showMessage('只支持上传 .txt 文件', true);
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch(`${API_BASE_URL}/api/rag/upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showMessage(data.message, false);
            knowledgeFile.value = ''; // 清空文件输入
            document.querySelector('.file-name').textContent = '未选择文件';
            updateKnowledgeCount(); // 更新知识库统计
            updateKnowledgePreview(); // 更新知识预览
        } else {
            showMessage(data.detail || '上传失败', true);
        }
    })
    .catch(error => {
        showMessage('服务器错误，请稍后重试', true);
    });
}

// 搜索处理
function handleSearch(e) {
    const query = e.target.value.trim();
    if (query) {
        updateKnowledgePreview(query);
    } else {
        updateKnowledgePreview();
    }
}

// 更新知识库统计
async function updateKnowledgeCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/stats`);
        const data = await response.json();
        if (response.ok && knowledgeCount) {
            knowledgeCount.textContent = data.count;
        }
    } catch (error) {
        console.error('获取知识库统计失败:', error);
    }
}

// 更新知识预览
async function updateKnowledgePreview(query = '') {
    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/retrieve?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (response.ok && knowledgePreview) {
            knowledgePreview.innerHTML = '';
            data.results.forEach((result, index) => {
                const previewItem = document.createElement('div');
                previewItem.className = 'preview-item';
                previewItem.innerHTML = `
                    <div class="content">${result}</div>
                    <div class="meta">段落 ${index + 1}</div>
                `;
                knowledgePreview.appendChild(previewItem);
            });
        }
    } catch (error) {
        console.error('获取知识预览失败:', error);
    }
}

// 显示消息
function showMessage(message, isError = false) {
    if (uploadMessage) {
        uploadMessage.textContent = message;
        uploadMessage.className = `message ${isError ? 'error' : 'success'}`;
        setTimeout(() => {
            uploadMessage.className = 'message';
        }, 3000);
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 导航处理
function handleNavigation() {
    if (backToDashboard) {
        backToDashboard.addEventListener('click', () => {
            window.location.href = 'dashboard.html';
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        });
    }
}

// 初始化事件监听器
function initializeEventListeners() {
    if (knowledgeFile) {
        knowledgeFile.addEventListener('change', handleFileSelect);
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    handleNavigation();
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM加载完成，开始初始化知识库管理页面');
    initializeDOMElements();
    initializeEventListeners();
    updateKnowledgeCount();
    updateKnowledgePreview();
}); 