with open('frontend/rag.html', 'r') as f:
    content = f.read()

config_script = '<script src="js/config.js"></script>'
rag_script = '    <script src="js/config.js"></script>\n    <!-- 加载RAG页面主要JS功能 -->\n    <script src="js/rag.js"></script>'

modified_content = content.replace(config_script, rag_script)

with open('frontend/rag.html', 'w') as f:
    f.write(modified_content)

print("RAG.js 脚本已添加到 rag.html 文件中") 