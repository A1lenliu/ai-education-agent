
// URL修复脚本 - 强制所有RAG API调用使用正确的端口
(function() {
    console.log('加载URL修复脚本');
    
    // 强制设置RAG URL
    window.RAG_BASE_URL = 'http://localhost:8002';
    console.log('已强制设置RAG_BASE_URL =', RAG_BASE_URL);
    
    // 监听页面完全加载
    window.addEventListener('load', function() {
        console.log('页面加载完成，准备修复API调用');
        
        // 覆盖loadDocuments函数
        if (typeof window.loadDocuments === 'function') {
            console.log('修复loadDocuments函数');
            
            // 保存原始函数
            const originalLoadDocuments = window.loadDocuments;
            
            // 覆盖函数
            window.loadDocuments = function() {
                console.log('调用修复后的loadDocuments函数');
                
                try {
                    // 尝试直接调用URL获取文档
                    const currentPage = window.currentPage || 1;
                    const searchQuery = window.searchQuery || '';
                    
                    const documentsTable = document.getElementById('documents-table');
                    if (!documentsTable) {
                        console.error('找不到documents-table元素');
                        return originalLoadDocuments();
                    }
                    
                    documentsTable.innerHTML = '<tr><td colspan="5" class="text-center">加载中...</td></tr>';
                    
                    // 直接使用正确的URL
                    const url = `${RAG_BASE_URL}/rag/documents?page=${currentPage}&search=${encodeURIComponent(searchQuery)}`;
                    console.log('直接请求正确的URL:', url);
                    
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
                        if (typeof window.updateDocumentsList === 'function') {
                            window.updateDocumentsList(data);
                        } else {
                            console.error('找不到updateDocumentsList函数');
                            documentsTable.innerHTML = '<tr><td colspan="5">无法显示文档列表</td></tr>';
                        }
                    })
                    .catch(error => {
                        console.error('获取文档列表失败:', error);
                        if (typeof window.showError === 'function') {
                            window.showError('无法加载文档列表: ' + error.message);
                        }
                        documentsTable.innerHTML = '<tr><td colspan="5">加载文档失败</td></tr>';
                    });
                } catch (e) {
                    console.error('运行修复的loadDocuments时出错:', e);
                    // 如果有错误，回退到原始函数
                    return originalLoadDocuments();
                }
            };
            
            // 立即调用一次
            setTimeout(function() {
                console.log('自动调用修复后的loadDocuments');
                window.loadDocuments();
            }, 1000);
        }
    });
})();
