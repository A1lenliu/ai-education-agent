// 强制修复脚本 - 拦截所有网络请求并修改URL
(function() {
    console.log('=== 强制修复脚本已加载 ===');
    
    // 1. 强制设置全局变量
    window.RAG_BASE_URL = 'http://localhost:8002';
    
    // 如果API_BASE_URL也被用于RAG请求，覆盖它
    if (window.API_BASE_URL && window.API_BASE_URL === 'http://localhost:8000') {
        console.log('检测到API_BASE_URL是8000端口，将为RAG请求覆盖它');
        
        // 保存原始API_BASE_URL
        window._ORIGINAL_API_BASE_URL = window.API_BASE_URL;
        
        // 重新定义API_BASE_URL的getter和setter
        Object.defineProperty(window, 'API_BASE_URL', {
            get: function() {
                // 获取调用栈
                const stack = new Error().stack || '';
                
                // 如果调用来自与RAG相关的代码（包含rag关键字），则返回RAG_BASE_URL
                if (stack.toLowerCase().includes('rag') || 
                    stack.toLowerCase().includes('document') || 
                    stack.toLowerCase().includes('load')) {
                    console.log('拦截API_BASE_URL访问，返回RAG端口8002');
                    return window.RAG_BASE_URL;
                }
                
                // 否则返回原始值
                return window._ORIGINAL_API_BASE_URL;
            },
            set: function(value) {
                console.log('拦截API_BASE_URL设置:', value);
                window._ORIGINAL_API_BASE_URL = value;
            },
            configurable: true
        });
    }
    
    // 2. 拦截所有fetch请求
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        let modifiedUrl = url;
        
        // 检查是否是RAG相关API调用
        if (typeof url === 'string' && url.includes('/rag/')) {
            // 如果URL包含localhost:8000，替换为localhost:8002
            if (url.includes('localhost:8000')) {
                modifiedUrl = url.replace('localhost:8000', 'localhost:8002');
                console.log('拦截到对8000端口的RAG请求，修改为:', modifiedUrl);
            } 
            // 如果URL是相对路径，确保使用RAG_BASE_URL
            else if (url.startsWith('/rag/')) {
                modifiedUrl = `${window.RAG_BASE_URL}${url}`;
                console.log('拦截到相对路径的RAG请求，修改为:', modifiedUrl);
            }
        }
        
        // 调用原始fetch
        return originalFetch.call(this, modifiedUrl, options);
    };
    
    // 3. 覆盖XMLHttpRequest
    const originalXhrOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        let modifiedUrl = url;
        
        // 检查是否是RAG相关API调用
        if (typeof url === 'string' && url.includes('/rag/')) {
            // 如果URL包含localhost:8000，替换为localhost:8002
            if (url.includes('localhost:8000')) {
                modifiedUrl = url.replace('localhost:8000', 'localhost:8002');
                console.log('拦截到XHR对8000端口的RAG请求，修改为:', modifiedUrl);
            } 
            // 如果URL是相对路径，确保使用RAG_BASE_URL
            else if (url.startsWith('/rag/')) {
                modifiedUrl = `${window.RAG_BASE_URL}${url}`;
                console.log('拦截到XHR相对路径的RAG请求，修改为:', modifiedUrl);
            }
        }
        
        // 调用原始open方法
        return originalXhrOpen.call(this, method, modifiedUrl, async, user, password);
    };
    
    // 4. 重写loadDocuments函数
    window.addEventListener('load', function() {
        // 间歇性检查和覆盖loadDocuments
        const checkAndOverride = function() {
            if (typeof window.loadDocuments === 'function') {
                console.log('覆盖loadDocuments函数');
                
                // 保存原始函数
                const originalLoadDocuments = window.loadDocuments;
                
                // 覆盖函数
                window.loadDocuments = function() {
                    console.log('调用强制修复后的loadDocuments函数');
                    
                    try {
                        const currentPage = window.currentPage || 1;
                        const searchQuery = window.searchQuery || '';
                        
                        // 直接使用硬编码的正确URL
                        const url = `http://localhost:8002/rag/documents?page=${currentPage}&search=${encodeURIComponent(searchQuery || '')}`;
                        console.log('强制使用正确的URL:', url);
                        
                        // 获取文档表格元素
                        const documentsTable = document.getElementById('documents-table');
                        if (!documentsTable) {
                            console.error('找不到documents-table元素');
                            return originalLoadDocuments.apply(this, arguments);
                        }
                        
                        documentsTable.innerHTML = '<tr><td colspan="5" class="text-center">加载中...</td></tr>';
                        
                        // 发送请求
                        fetch(url, { 
                            method: 'GET',
                            headers: { 'Accept': 'application/json' }
                        })
                        .then(response => {
                            console.log('文档列表响应状态:', response.status);
                            if (!response.ok) {
                                throw new Error(`HTTP错误! 状态: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('成功获取到文档数据');
                            
                            // 如果存在updateDocumentsList函数，调用它
                            if (typeof window.updateDocumentsList === 'function') {
                                window.updateDocumentsList(data);
                            } else {
                                console.log('找不到updateDocumentsList函数，尝试自行实现');
                                
                                // 清空表格
                                documentsTable.innerHTML = '';
                                
                                // 检查是否有文档
                                const documents = data.documents || data.doc_ids || [];
                                const emptyState = document.getElementById('empty-state');
                                
                                if (documents.length === 0) {
                                    // 显示空状态
                                    if (emptyState) emptyState.style.display = 'flex';
                                    documentsTable.innerHTML = '<tr><td colspan="5" class="text-center">暂无文档</td></tr>';
                                    return;
                                }
                                
                                // 隐藏空状态
                                if (emptyState) emptyState.style.display = 'none';
                                
                                // 遍历文档并添加行
                                documents.forEach(doc => {
                                    const docId = doc.id || doc;
                                    const title = doc.title || docId;
                                    const author = doc.author || '-';
                                    
                                    const row = document.createElement('tr');
                                    row.innerHTML = `
                                        <td>${docId}</td>
                                        <td>${title}</td>
                                        <td>${author}</td>
                                        <td>
                                            <button class="action-btn view-btn" data-id="${docId}">
                                                <i class="fas fa-eye"></i> 查看
                                            </button>
                                            <button class="action-btn delete-btn" data-id="${docId}">
                                                <i class="fas fa-trash"></i> 删除
                                            </button>
                                        </td>
                                    `;
                                    documentsTable.appendChild(row);
                                });
                                
                                // 添加事件监听器
                                documentsTable.querySelectorAll('.view-btn').forEach(btn => {
                                    btn.addEventListener('click', function() {
                                        const id = this.getAttribute('data-id');
                                        if (typeof window.viewDocument === 'function') {
                                            window.viewDocument(id);
                                        }
                                    });
                                });
                                
                                documentsTable.querySelectorAll('.delete-btn').forEach(btn => {
                                    btn.addEventListener('click', function() {
                                        const id = this.getAttribute('data-id');
                                        if (typeof window.deleteDocument === 'function') {
                                            window.deleteDocument(id);
                                        }
                                    });
                                });
                            }
                        })
                        .catch(error => {
                            console.error('获取文档列表失败:', error);
                            
                            // 显示错误消息
                            if (typeof window.showError === 'function') {
                                window.showError('无法加载文档列表: ' + error.message);
                            }
                            
                            documentsTable.innerHTML = `<tr><td colspan="5" class="text-center">加载失败: ${error.message}</td></tr>`;
                            
                            // 尝试回退到原始函数
                            console.log('尝试回退到原始loadDocuments函数');
                            return originalLoadDocuments.apply(this, arguments);
                        });
                    } catch (e) {
                        console.error('强制修复的loadDocuments函数出错:', e);
                        return originalLoadDocuments.apply(this, arguments);
                    }
                };
                
                // 300毫秒后自动调用
                setTimeout(function() {
                    console.log('自动调用修复后的loadDocuments函数');
                    window.loadDocuments();
                }, 300);
                
                // 停止检查
                clearInterval(checkInterval);
            }
        };
        
        // 每200毫秒检查一次，直到找到函数
        const checkInterval = setInterval(checkAndOverride, 200);
        
        // 最多检查10次
        setTimeout(function() {
            clearInterval(checkInterval);
        }, 2000);
    });
    
    console.log('=== 强制修复脚本已完成初始化 ===');
})(); 