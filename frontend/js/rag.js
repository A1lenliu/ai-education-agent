// RAG页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    checkAuth();
    
    // 初始化页面事件
    initEvents();
    
    // 加载文档列表
    loadDocuments();
    
    // 检查API连接
    if (typeof checkApiConnection === 'function') {
        checkApiConnection();
    }
});

// API基础URL - 从config.js中获取RAG服务的URL
// 如果RAG_BASE_URL未定义，则使用备用URL
const rag_api_url = typeof RAG_BASE_URL !== 'undefined' ? RAG_BASE_URL : 'http://localhost:8002';

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
    
    // 搜索文档按钮
    const searchDocsBtn = document.getElementById('search-docs-btn');
    const searchDocsInput = document.getElementById('search-docs-input');
    if (searchDocsBtn && searchDocsInput) {
        searchDocsBtn.addEventListener('click', function() {
            loadDocuments(1, searchDocsInput.value.trim());
        });
        
        searchDocsInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                loadDocuments(1, searchDocsInput.value.trim());
            }
        });
    }
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
        const response = await fetch(`${rag_api_url}/rag/query`, {
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
        
        const response = await fetch(`${rag_api_url}/rag/document/upload/file`, {
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
        const response = await fetch(`${rag_api_url}/rag/document/upload`, {
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
async function loadDocuments(page = 1, search = '') {
    const documentsTable = document.getElementById('documents-table');
    
    try {
        // 首先尝试使用分页API
        const pagedUrl = `${rag_api_url}/rag/documents/paged?page=${page}&limit=10${search ? '&search=' + encodeURIComponent(search) : ''}`;
        
        try {
            const response = await fetch(pagedUrl);
            if (response.ok) {
                const data = await response.json();
                
                if (data.status === 'success') {
                    // 清空表格
                    documentsTable.innerHTML = '';
                    
                    if (data.documents && data.documents.length > 0) {
                        // 添加文档行
                        data.documents.forEach(doc => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${doc.doc_id}</td>
                                <td>${doc.title || '未命名文档'}</td>
                                <td>${doc.author || '-'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-doc-btn" data-docid="${doc.doc_id}">
                                        <i class="fas fa-eye"></i> 查看
                                    </button>
                                    <button class="btn btn-sm btn-danger delete-doc-btn" data-docid="${doc.doc_id}">
                                        <i class="fas fa-trash"></i> 删除
                                    </button>
                                </td>
                            `;
                            documentsTable.appendChild(row);
                        });
                        
                        // 添加查看和删除按钮事件
                        const viewButtons = document.querySelectorAll('.view-doc-btn');
                        viewButtons.forEach(button => {
                            button.addEventListener('click', function() {
                                const docId = this.getAttribute('data-docid');
                                viewDocument(docId);
                            });
                        });
                        
                        const deleteButtons = document.querySelectorAll('.delete-doc-btn');
                        deleteButtons.forEach(button => {
                            button.addEventListener('click', function() {
                                const docId = this.getAttribute('data-docid');
                                deleteDocument(docId);
                            });
                        });
                        
                        // 添加分页控件
                        if (data.pagination) {
                            const { page, total_pages, total_docs } = data.pagination;
                            
                            // 创建分页控件
                            const paginationContainer = document.createElement('div');
                            paginationContainer.className = 'pagination-container';
                            paginationContainer.innerHTML = `
                                <div class="pagination-info">
                                    显示 ${total_docs} 个文档中的 ${Math.min(10, data.documents.length)}个 (第 ${page} 页 / 共 ${total_pages} 页)
                                </div>
                                <div class="pagination-controls">
                                    <button class="btn btn-sm ${page > 1 ? 'btn-primary' : 'btn-secondary'}" 
                                            ${page > 1 ? '' : 'disabled'}
                                            id="prev-page-btn">
                                        上一页
                                    </button>
                                    <button class="btn btn-sm ${page < total_pages ? 'btn-primary' : 'btn-secondary'}" 
                                            ${page < total_pages ? '' : 'disabled'}
                                            id="next-page-btn">
                                        下一页
                                    </button>
                                </div>
                            `;
                            
                            // 添加到表格下方
                            const tableContainer = documentsTable.parentNode;
                            if (tableContainer.querySelector('.pagination-container')) {
                                tableContainer.removeChild(tableContainer.querySelector('.pagination-container'));
                            }
                            tableContainer.appendChild(paginationContainer);
                            
                            // 添加分页事件
                            if (page > 1) {
                                document.getElementById('prev-page-btn').addEventListener('click', () => {
                                    loadDocuments(page - 1, search);
                                });
                            }
                            
                            if (page < total_pages) {
                                document.getElementById('next-page-btn').addEventListener('click', () => {
                                    loadDocuments(page + 1, search);
                                });
                            }
                        }
                    } else {
                        // 没有文档
                        documentsTable.innerHTML = `
                            <tr>
                                <td colspan="4" class="text-center">暂无文档</td>
                            </tr>
                        `;
                    }
                    
                    return; // 如果分页API成功，就不需要继续尝试旧的API
                }
            }
        } catch (error) {
            console.warn('分页API调用失败，尝试使用基础API:', error);
        }
        
        // 如果分页API失败，继续尝试使用基础API
        const response = await fetch(`${rag_api_url}/rag/documents`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // 清空表格
            documentsTable.innerHTML = '';
            
            if (data.doc_ids && data.doc_ids.length > 0) {
                // 添加文档行
                for (const docId of data.doc_ids) {
                    // 获取文档详情
                    try {
                        const detailResponse = await fetch(`${rag_api_url}/rag/document/content?doc_id=${docId}`);
                        const detailData = await detailResponse.json();
                        
                        if (detailData.status === 'success' && detailData.document) {
                            const doc = detailData.document;
                            
                            // 如果有搜索且不匹配，则跳过
                            if (search && !(
                                (doc.title && doc.title.toLowerCase().includes(search.toLowerCase())) ||
                                (doc.content && doc.content.toLowerCase().includes(search.toLowerCase()))
                            )) {
                                continue;
                            }
                            
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${docId}</td>
                                <td>${doc.title || '未命名文档'}</td>
                                <td>${doc.author || '-'}</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-doc-btn" data-docid="${docId}">
                                        <i class="fas fa-eye"></i> 查看
                                    </button>
                                    <button class="btn btn-sm btn-danger delete-doc-btn" data-docid="${docId}">
                                        <i class="fas fa-trash"></i> 删除
                                    </button>
                                </td>
                            `;
                            documentsTable.appendChild(row);
                        } else {
                            // 如果无法获取详情，使用简单的行
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${docId}</td>
                                <td colspan="2">-</td>
                                <td>
                                    <button class="btn btn-sm btn-primary view-doc-btn" data-docid="${docId}">
                                        <i class="fas fa-eye"></i> 查看
                                    </button>
                                    <button class="btn btn-sm btn-danger delete-doc-btn" data-docid="${docId}">
                                        <i class="fas fa-trash"></i> 删除
                                    </button>
                                </td>
                            `;
                            documentsTable.appendChild(row);
                        }
                    } catch (error) {
                        // 如果获取详情失败，使用简单的行
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${docId}</td>
                            <td colspan="2">-</td>
                            <td>
                                <button class="btn btn-sm btn-primary view-doc-btn" data-docid="${docId}">
                                    <i class="fas fa-eye"></i> 查看
                                </button>
                                <button class="btn btn-sm btn-danger delete-doc-btn" data-docid="${docId}">
                                    <i class="fas fa-trash"></i> 删除
                                </button>
                            </td>
                        `;
                        documentsTable.appendChild(row);
                    }
                }
                
                // 添加查看和删除按钮事件
                const viewButtons = document.querySelectorAll('.view-doc-btn');
                viewButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const docId = this.getAttribute('data-docid');
                        viewDocument(docId);
                    });
                });
                
                const deleteButtons = document.querySelectorAll('.delete-doc-btn');
                deleteButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const docId = this.getAttribute('data-docid');
                        deleteDocument(docId);
                    });
                });
                
                // 如果没有行，显示"暂无文档"
                if (documentsTable.children.length === 0) {
                    documentsTable.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">暂无符合条件的文档</td>
                        </tr>
                    `;
                }
            } else {
                // 没有文档
                documentsTable.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">暂无文档</td>
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

// 查看文档
function viewDocument(docId) {
    if (!docId) return;
    
    // 显示加载中...
    showLoading('正在加载文档内容...');
    
    fetch(`${rag_api_url}/rag/document/content?doc_id=${docId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            
            if (data.status === 'success' && data.document) {
                const doc = data.document;
                
                // 使用模态框显示文档内容
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = 'documentModal';
                modal.tabIndex = '-1';
                modal.setAttribute('aria-labelledby', 'documentModalLabel');
                modal.setAttribute('aria-hidden', 'true');
                
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="documentModalLabel">${doc.title || '未命名文档'}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="document-info">
                                    <p><strong>文档ID:</strong> ${doc.doc_id}</p>
                                    ${doc.author ? `<p><strong>作者:</strong> ${doc.author}</p>` : ''}
                                    ${doc.tags ? `<p><strong>标签:</strong> ${doc.tags}</p>` : ''}
                                </div>
                                <hr>
                                <div class="document-content">
                                    <pre>${doc.content}</pre>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // 添加到页面
                document.body.appendChild(modal);
                
                // 显示模态框
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
                
                // 模态框关闭后从DOM中移除
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
            } else {
                showError('无法加载文档内容: ' + (data.detail || '未知错误'));
            }
        })
        .catch(error => {
            hideLoading();
            showError('查看文档失败: ' + error.message);
        });
}

// 删除文档
async function deleteDocument(docId) {
    if (!docId) return;
    
    if (!confirm(`确定要删除文档 ${docId} 吗？此操作不可撤销。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${rag_api_url}/rag/document/delete`, {
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

// 显示加载中...
function showLoading(message = '正在加载...') {
    const loading = document.createElement('div');
    loading.className = 'global-loading';
    loading.innerHTML = `
        <div class="loading-spinner"></div>
        <div class="loading-message">${message}</div>
    `;
    document.body.appendChild(loading);
}

// 隐藏加载中...
function hideLoading() {
    const loading = document.querySelector('.global-loading');
    if (loading) {
        document.body.removeChild(loading);
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