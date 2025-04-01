// API基础URL配置
const API_BASE_URL = 'http://localhost:8000';

// RAG API路径
const RAG_API = {
    upload: `${API_BASE_URL}/rag/document/upload/file`,
    documents: `${API_BASE_URL}/rag/documents`,
    document: (id) => `${API_BASE_URL}/rag/document/${id}`,
    query: `${API_BASE_URL}/rag/query`,
    documentContent: `${API_BASE_URL}/rag/document/content`,
    deleteDocument: `${API_BASE_URL}/rag/document/delete`
};

// 检查是否可以连接到API
function checkApiConnection() {
    console.log('正在检查API连接...');
    
    // 使用documents端点替代不存在的health端点
    fetch(`${API_BASE_URL}/rag/documents`, { method: 'GET' })
        .then(response => {
            if (response.ok) {
                console.log('✅ API服务正常');
                return response.json();
            }
            throw new Error('API连接失败');
        })
        .then(data => {
            console.log('API状态信息:', data);
        })
        .catch(error => {
            console.error('❌ API连接检查失败:', error);
            console.warn('请确保后端服务已启动并运行在正确的端口上');
        });
} 