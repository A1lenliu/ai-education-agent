with open('frontend/rag.html', 'r') as f:
    content = f.read()

# 替换各种硬编码的URL
content = content.replace('this.value = API_BASE_URL + \'/rag/documents\';', 
                         'this.value = RAG_BASE_URL + \'/rag/documents\';')

# 替换loadDocuments函数中构建的URL
if 'const url = `${API_BASE_URL}/rag/documents?' in content:
    content = content.replace('const url = `${API_BASE_URL}/rag/documents?', 
                             'const url = `${RAG_BASE_URL}/rag/documents?')

# 替换其他可能的API调用
content = content.replace('API_BASE_URL + fullUrl', 'RAG_BASE_URL + fullUrl')
content = content.replace('API_BASE_URL + \'/rag/', 'RAG_BASE_URL + \'/rag/')

with open('frontend/rag.html', 'w') as f:
    f.write(content)

print("rag.html 文件中的API URL已更新，API_BASE_URL已替换为RAG_BASE_URL")