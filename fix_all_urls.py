import re

def fix_rag_html():
    """修复rag.html中的URL问题"""
    with open('frontend/rag.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有API调用
    content = content.replace('API_BASE_URL + "/rag/', 'RAG_BASE_URL + "/rag/')
    content = content.replace("API_BASE_URL + '/rag/", "RAG_BASE_URL + '/rag/")
    content = content.replace('API_BASE_URL', 'RAG_BASE_URL')  # 最后替换所有剩余的引用
    
    # 直接替换确保每个URL使用8000端口
    if '8002/rag/' in content:
        content = content.replace('8002/rag/', '8000/rag/')
    
    # 确保设置了默认端口
    if 'window.RAG_BASE_URL = ' in content:
        content = re.sub(r'window\.RAG_BASE_URL = \'http://localhost:\d+\';', 
                         "window.RAG_BASE_URL = 'http://localhost:8000';", content)
    
    # 修复loadDocuments函数中的URL构建
    if '${API_BASE_URL}/rag/documents?' in content:
        content = content.replace('${API_BASE_URL}/rag/documents?', '${RAG_BASE_URL}/rag/documents?')
        
    # 保存更改
    with open('frontend/rag.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复rag.html中的所有URL引用")

def fix_inline_api_calls():
    """直接修改API调用函数内部的URL"""
    js_content = """
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
    """
    
    # 保存为修复脚本
    with open('frontend/js/fix_api_calls.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 向rag.html添加引用
    with open('frontend/rag.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    if '<script src="js/fix_api_calls.js"></script>' not in html_content:
        html_content = html_content.replace('</body>', 
                                          '    <script src="js/fix_api_calls.js"></script>\n</body>')
        
        with open('frontend/rag.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    print("已创建并添加修复API调用的JS脚本")

if __name__ == "__main__":
    fix_rag_html()
    fix_inline_api_calls()
    print("所有修复完成，请重启服务并清除浏览器缓存") 