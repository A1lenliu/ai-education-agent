import re

# 读取原始文件内容
with open('frontend/rag.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 直接替换端口号
modified_content = content.replace(':8000/rag/', ':8002/rag/')

# 替换其他可能的引用
pattern = r'API_BASE_URL \+ [\'"]\/rag\/'
replacement = 'RAG_BASE_URL + "/rag/'
modified_content = re.sub(pattern, replacement, modified_content)

# 替换URL构建
modified_content = modified_content.replace('${API_BASE_URL}/rag/', '${RAG_BASE_URL}/rag/')

# 替换变量引用
pattern = r'const url = `\${API_BASE_URL}\/rag\/'
replacement = 'const url = `${RAG_BASE_URL}/rag/'
modified_content = re.sub(pattern, replacement, modified_content)

# 写回文件
with open('frontend/rag.html', 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("已更新rag.html中所有端口引用")