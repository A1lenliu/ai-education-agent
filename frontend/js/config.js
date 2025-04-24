// API基础URL配置
const API_BASE_URL = 'http://localhost:8002';  // 认证服务
const RAG_BASE_URL = 'http://localhost:8000';  // RAG服务

// 输出配置信息到控制台
console.log('CONFIG.JS: API_BASE_URL =', API_BASE_URL);
console.log('CONFIG.JS: RAG_BASE_URL =', RAG_BASE_URL);

// RAG API路径
const RAG_API = {
    upload: `${RAG_BASE_URL}/rag/document/upload/file`,
    documents: `${RAG_BASE_URL}/rag/documents`,
    documentsPaged: `${RAG_BASE_URL}/rag/documents/paged`,
    document: (id) => `${RAG_BASE_URL}/rag/document/${id}`,
    query: `${RAG_BASE_URL}/rag/query`,
    documentContent: `${RAG_BASE_URL}/rag/document/content`,
    deleteDocument: `${RAG_BASE_URL}/rag/document/delete`
};

// 输出RAG_API配置到控制台
console.log('CONFIG.JS: RAG_API =', RAG_API);

// 检查是否可以连接到API
function checkApiConnection() {
    console.log('正在检查API连接...');
    
    // 检查认证服务
    console.log('检查认证服务...');
    fetch(`${API_BASE_URL}/health`, { method: 'GET' })
        .then(response => {
            if (response.ok) {
                console.log('✅ 认证服务正常');
                return response.json();
            }
            throw new Error('认证服务连接失败');
        })
        .catch(error => {
            console.error('❌ 认证服务检查失败:', error);
        });
    
    // 检查RAG服务
    console.log('检查RAG服务...');
    fetch(`${RAG_BASE_URL}/health`, { method: 'GET' })
        .then(response => {
            if (response.ok) {
                console.log('✅ RAG服务正常');
                return response.json();
            }
            throw new Error('RAG服务连接失败');
        })
        .catch(error => {
            console.error('❌ RAG服务检查失败:', error);
            console.warn('请确保后端服务已启动并运行在正确的端口上');
        });
}

console.log("RAG_BASE_URL:", RAG_BASE_URL);
console.log("RAG_API:", RAG_API);

if (typeof RAG_API === 'undefined') {
    console.warn('RAG_API未在全局定义，创建默认配置');
    window.RAG_API = {
        upload: 'http://localhost:8000/rag/document/upload/file',
        documents: 'http://localhost:8000/rag/documents',
        document: function(id) { return `http://localhost:8000/rag/document/${id}`; },
        query: 'http://localhost:8000/rag/query',
        documentContent: 'http://localhost:8000/rag/document/content',
        deleteDocument: 'http://localhost:8000/rag/document/delete'
    };
} 