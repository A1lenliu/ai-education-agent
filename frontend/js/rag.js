// RAG页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    checkAuth();
    
    // 初始化页面事件
    initEvents();
    
    // 加载文档列表
    loadDocuments();
});

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// 检查认证状态
function checkAuth() {
    const username = localStorage.getItem('username');
    if (username) {
        document.getElementById('username').textContent = username;
    } else {
        window.location.href = 'login.html';
    }
}

// 初始化页面事件
function initEvents() {
    // 聊天发送按钮
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 文档上传表单
    const fileUploadForm = document.getElementById('file-upload-form');
    fileUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        uploadFile();
    });
    
    // 文本上传表单
    const textUploadForm = document.getElementById('text-upload-form');
    textUploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        uploadText();
    });
    
    // 刷新文档按钮
    const refreshDocsBtn = document.getElementById('refresh-docs-btn');
    refreshDocsBtn.addEventListener('click', loadDocuments);
    
    // 登出按钮
    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('username');
        window.location.href = 'login.html';
    });
}

// 发送消息
async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const useRagCheck = document.getElementById('use-rag-check');
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // 清空输入框
    chatInput.value = '';
    
    // 添加用户消息
    const userMessageEl = document.createElement('div');
    userMessageEl.className = 'message user-message';
    userMessageEl.innerHTML = `
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatMessages.appendChild(userMessageEl);
    
    // 添加加载指示器
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = `
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(loadingIndicator);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
        // 准备查询参数
        const queryParams = {
            query: message,
            use_rag: useRagCheck.checked
        };
        
        // 发送到服务器
        const response = await fetch(`${API_BASE_URL}/rag/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(queryParams)
        });
        
        const data = await response.json();
        
        // 删除加载指示器
        chatMessages.removeChild(loadingIndicator);
        
        if (data.status === 'success') {
            // 添加助手消息
            const assistantMessageEl = document.createElement('div');
            assistantMessageEl.className = 'message assistant-message';
            
            // 使用marked渲染Markdown
            const sanitizedHtml = DOMPurify.sanitize(marked.parse(data.answer));
            
            let messageContent = `
                <div class="message-content">${sanitizedHtml}</div>
            `;
            
            // 如果有上下文引用，添加引用部分
            if (data.contexts && data.contexts.length > 0) {
                let referencesHtml = `
                    <div class="references-container">
                        <div class="reference-title">参考内容：</div>
                `;
                
                data.contexts.forEach((context, index) => {
                    referencesHtml += `
                        <div class="reference-item">
                            <div class="reference-text">${escapeHtml(context.text.substring(0, 150))}${context.text.length > 150 ? '...' : ''}</div>
                        </div>
                    `;
                });
                
                referencesHtml += `</div>`;
                messageContent += referencesHtml;
            }
            
            assistantMessageEl.innerHTML = messageContent;
            chatMessages.appendChild(assistantMessageEl);
        } else {
            // 处理错误
            showError('获取回答时发生错误: ' + data.detail);
        }
    } catch (error) {
        console.error('发送消息时出错:', error);
        
        // 删除加载指示器
        chatMessages.removeChild(loadingIndicator);
        
        // 显示错误消息
        showError('发送消息时出错: ' + error.message);
    }
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 上传文件
async function uploadFile() {
    const fileInput = document.getElementById('document-file');
    const titleInput = document.getElementById('file-title');
    const authorInput = document.getElementById('file-author');
    const tagsInput = document.getElementById('file-tags');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showError('请选择要上传的文件');
        return;
    }
    
    const file = fileInput.files[0];
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();
    const tags = tagsInput.value.trim() ? tagsInput.value.split(',').map(tag => tag.trim()) : [];
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title || file.name);
        formData.append('author', author);
        formData.append('tags', JSON.stringify(tags));
        
        const response = await fetch(`${API_BASE_URL}/rag/document/upload/file`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 清空表单
            fileInput.value = '';
            titleInput.value = '';
            authorInput.value = '';
            tagsInput.value = '';
            
            // 显示成功消息
            showSuccess('文件上传成功');
            
            // 重新加载文档列表
            loadDocuments();
        } else {
            showError('上传文件失败: ' + data.detail);
        }
    } catch (error) {
        console.error('上传文件时出错:', error);
        showError('上传文件时出错: ' + error.message);
    }
}

// 上传文本
async function uploadText() {
    const textInput = document.getElementById('document-text');
    const titleInput = document.getElementById('text-title');
    const authorInput = document.getElementById('text-author');
    const tagsInput = document.getElementById('text-tags');
    
    const text = textInput.value.trim();
    if (!text) {
        showError('请输入文档内容');
        return;
    }
    
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();
    const tags = tagsInput.value.trim() ? tagsInput.value.split(',').map(tag => tag.trim()) : [];
    
    try {
        const response = await fetch(`${API_BASE_URL}/rag/document/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document: text,
                title: title || '未命名文档',
                author: author,
                tags: tags
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 清空表单
            textInput.value = '';
            titleInput.value = '';
            authorInput.value = '';
            tagsInput.value = '';
            
            // 显示成功消息
            showSuccess('文档保存成功');
            
            // 重新加载文档列表
            loadDocuments();
        } else {
            showError('保存文档失败: ' + data.detail);
        }
    } catch (error) {
        console.error('保存文档时出错:', error);
        showError('保存文档时出错: ' + error.message);
    }
}

// 加载文档列表
async function loadDocuments() {
    const documentsTable = document.getElementById('documents-table');
    
    try {
        const response = await fetch(`${API_BASE_URL}/rag/documents`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // 清空表格
            documentsTable.innerHTML = '';
            
            if (data.doc_ids && data.doc_ids.length > 0) {
                // 添加文档行
                data.doc_ids.forEach(docId => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${docId}</td>
                        <td>
                            <button class="btn btn-sm btn-danger delete-doc-btn" data-docid="${docId}">
                                <i class="bi bi-trash"></i> 删除
                            </button>
                        </td>
                    `;
                    documentsTable.appendChild(row);
                });
                
                // 添加删除按钮事件
                const deleteButtons = document.querySelectorAll('.delete-doc-btn');
                deleteButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const docId = this.getAttribute('data-docid');
                        deleteDocument(docId);
                    });
                });
            } else {
                // 没有文档
                documentsTable.innerHTML = `
                    <tr>
                        <td colspan="2" class="text-center">暂无文档</td>
                    </tr>
                `;
            }
        } else {
            showError('获取文档列表失败: ' + data.detail);
        }
    } catch (error) {
        console.error('加载文档列表时出错:', error);
        showError('加载文档列表时出错: ' + error.message);
    }
}

// 删除文档
async function deleteDocument(docId) {
    if (!confirm(`确定要删除文档 ${docId} 吗？此操作不可撤销。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/rag/document/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                doc_id: docId
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showSuccess(`文档 ${docId} 已成功删除`);
            loadDocuments();
        } else {
            showError('删除文档失败: ' + data.detail);
        }
    } catch (error) {
        console.error('删除文档时出错:', error);
        showError('删除文档时出错: ' + error.message);
    }
}

// 显示成功消息
function showSuccess(message) {
    alert(message); // 简单实现，可以替换为更漂亮的通知
}

// 显示错误消息
function showError(message) {
    alert('错误: ' + message); // 简单实现，可以替换为更漂亮的通知
}

// 显示系统消息
function showSystemMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    const systemMessageEl = document.createElement('div');
    systemMessageEl.className = 'system-message';
    systemMessageEl.innerHTML = `<p>${escapeHtml(message)}</p>`;
    chatMessages.appendChild(systemMessageEl);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// HTML转义
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
} 