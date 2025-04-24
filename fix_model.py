#!/usr/bin/env python3
# 修复SentenceTransformer模型

import os
print("开始下载和修复SentenceTransformer模型...")

try:
    from sentence_transformers import SentenceTransformer
    
    # 尝试加载模型（会自动下载）
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    print(f"正在下载模型: {model_name}")
    model = SentenceTransformer(model_name)
    
    # 测试模型
    embeddings = model.encode(["这是一个测试句子，看看能否正常工作。"])
    print("模型加载成功，生成的嵌入向量形状:", embeddings.shape)
    print("模型修复完成!")
    
except Exception as e:
    print(f"下载模型时出错: {str(e)}")
    print("请尝试使用以下命令手动安装:")
    print("pip install -U sentence-transformers") 