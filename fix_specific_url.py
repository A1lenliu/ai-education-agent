#!/usr/bin/env python3
# 专门修复loadDocuments函数中的URL构建

import re

def fix_rag_html_url():
    print("开始修复rag.html中的文档列表URL...")
    
    with open('frontend/rag.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换硬编码的端口
    if 'http://localhost:8000/rag/documents' in content:
        content = content.replace('http://localhost:8000/rag/documents', 
                                 'http://localhost:8002/rag/documents')
        print("- 修复了硬编码的URL")
    
    # 查找URL构建模式并替换
    patterns = [
        (r'const url = [`\'"]http://localhost:8000/rag/documents', 
         r'const url = `http://localhost:8002/rag/documents'),
        (r'const url = [`\'"]\${API_BASE_URL}/rag/documents', 
         r'const url = `${RAG_BASE_URL}/rag/documents'),
        (r'url: API_BASE_URL \+ ["\']?/rag/documents["\']?', 
         r'url: RAG_BASE_URL + "/rag/documents"'),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print(f"- 修复了模式: {pattern}")
    
    # 特定函数修复
    if "function loadDocuments() {" in content:
        load_docs_pattern = r'function loadDocuments\(\) \{(.*?)const url = [`\'"](.+?)\/rag\/documents\?page='
        matches = re.findall(load_docs_pattern, content, re.DOTALL)
        
        if matches:
            for match in matches:
                if "API_BASE_URL" in match[1] or "localhost:8000" in match[1]:
                    old_url = match[1]
                    if "API_BASE_URL" in old_url:
                        new_content = content.replace(
                            f'const url = `${old_url}/rag/documents?page=',
                            f'const url = `${RAG_BASE_URL}/rag/documents?page='
                        )
                    else:
                        new_content = content.replace(
                            f'const url = `{old_url}/rag/documents?page=',
                            f'const url = `http://localhost:8002/rag/documents?page='
                        )
                    
                    if new_content != content:
                        content = new_content
                        print(f"- 修复了loadDocuments函数中的URL: {old_url}")
    
    # 替换所有直接引用8000端口的RAG URL
    content = content.replace(':8000/rag/', ':8002/rag/')
    
    # 保存文件
    with open('frontend/rag.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("rag.html文件中的文档列表URL修复完成")

def fix_override_js():
    """创建覆盖RAG URL的JS文件"""
    js_content = """
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
"""
    
    # 保存为修复脚本
    with open('frontend/js/url_override.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # 向rag.html添加引用(头部优先加载)
    with open('frontend/rag.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    if '<script src="js/url_override.js"></script>' not in html_content:
        html_content = html_content.replace('<script src="js/config.js"></script>', 
                                          '<script src="js/config.js"></script>\n    <script src="js/url_override.js"></script>')
        
        with open('frontend/rag.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    print("URL覆盖脚本已创建并添加到rag.html")

if __name__ == "__main__":
    fix_rag_html_url()
    fix_override_js()
    print("所有修复完成，请重启服务并强制刷新浏览器(Ctrl+F5)或清除缓存") 