
// 确保全局定义RAG API服务器地址
if (typeof RAG_BASE_URL === 'undefined') {
    console.warn('RAG_BASE_URL未定义！设置为默认值');
    window.RAG_BASE_URL = 'http://localhost:8000';
}

// 重新定义API调用函数
window.loadDocuments = function() {
    console.log('使用修复后的loadDocuments函数');
    console.log('当前RAG_BASE_URL:', RAG_BASE_URL);
    
    const documentsTable = document.getElementById('documents-table');
    const emptyState = document.getElementById('empty-state');
    
    if (!documentsTable || !emptyState) return;
    
    documentsTable.innerHTML = '<tr><td colspan="5" class="text-center">加载中...</td></tr>';
    emptyState.style.display = 'none';
    
    // 使用正确的端口
    const url = `${RAG_BASE_URL}/rag/documents?page=${currentPage || 1}&search=${encodeURIComponent(searchQuery || '')}`;
    console.log('请求文档列表URL:', url);
    
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
        console.log('获取到文档数据:', data);
        updateDocumentsList(data);
    })
    .catch(error => {
        console.error('获取文档列表失败:', error);
        showError('无法加载文档列表: ' + error.message);
        
        documentsTable.innerHTML = '';
        emptyState.style.display = 'flex';
    });
};
    