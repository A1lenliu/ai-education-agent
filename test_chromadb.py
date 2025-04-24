#!/usr/bin/env python3
# 测试ChromaDB的基本功能

import os
import shutil
import logging
import chromadb
import numpy as np
from typing import List, Dict, Any, Optional, Union
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 使用sentence-transformers实现真正的语义嵌入函数
class SentenceTransformerEmbedding(EmbeddingFunction):
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化sentence-transformers嵌入函数
        
        Args:
            model_name: 要使用的模型名称，默认使用支持多语言的模型
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"加载模型: {model_name}")
        except ImportError:
            logger.error("请安装sentence-transformers包: pip install sentence-transformers")
            raise ImportError("请安装sentence-transformers包: pip install sentence-transformers")
    
    def __call__(self, input: Documents) -> Embeddings:
        """
        生成文本嵌入，符合ChromaDB的新接口要求
        
        Args:
            input: 文本或文本列表
            
        Returns:
            嵌入向量列表
        """
        if not input:
            return []
        
        # 确保input是列表
        texts = input if isinstance(input, list) else [input]
        
        # 生成嵌入
        embeddings = self.model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
        
        # 确保返回的是Python列表
        return embeddings.tolist()

# 备用：如果不想安装额外依赖，可以继续使用哈希嵌入函数
class SimpleEmbeddingFunction(EmbeddingFunction):
    def __init__(self, dimension=384):
        self.dimension = dimension
    
    def __call__(self, input: Documents) -> Embeddings:
        """按照ChromaDB的要求实现__call__方法，只接受input参数"""
        result = []
        
        # 确保input是一个列表
        texts = input if isinstance(input, list) else [input]
        
        for text in texts:
            # 对文本进行简单哈希处理并标准化
            hash_values = []
            for i in range(self.dimension):
                # 使用不同的种子值生成哈希
                seed = i + 1
                hash_val = 0
                for j, char in enumerate(text):
                    hash_val += (ord(char) * (seed + j)) % 1000
                hash_values.append(hash_val)
            
            # 标准化向量
            vec = np.array(hash_values, dtype=float)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            
            result.append(vec.tolist())
        
        return result

def test_chroma_db():
    """
    测试ChromaDB的基本功能
    """
    # 创建一个测试专用的目录
    test_dir = os.path.join(os.path.dirname(__file__), "test_knowledge_base")
    os.makedirs(test_dir, exist_ok=True)
    logger.info(f"创建测试目录: {test_dir}")
    
    # 初始化ChromaDB客户端
    client = chromadb.PersistentClient(path=test_dir)
    logger.info("初始化ChromaDB客户端")
    
    # 使用简单哈希嵌入
    embedding_function = SimpleEmbeddingFunction()
    logger.info("使用简单哈希嵌入函数")
    
    # 创建或获取集合
    collection_name = "test_collection"
    try:
        # 尝试获取已存在的集合
        collection = client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        logger.info(f"获取已存在的集合: {collection_name}")
    except Exception as e:
        # 如果集合不存在，创建新集合
        logger.info(f"创建新集合: {collection_name}")
        collection = client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    
    # 添加测试文档
    documents = [
        "人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它致力于研究和开发能够模拟、延伸和扩展人类智能的理论、方法和技术。",
        "机器学习是人工智能的一个子领域，它使用统计技术让计算机系统利用经验自动改进。",
        "深度学习是机器学习的一种特定方法，它使用多层神经网络来模拟人脑的结构和功能。"
    ]
    ids = ["doc1", "doc2", "doc3"]
    metadatas = [
        {"author": "AI教育团队", "topic": "AI概述"},
        {"author": "机器学习专家", "topic": "机器学习"},
        {"author": "深度学习研究员", "topic": "深度学习"}
    ]
    
    try:
        # 添加文档
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        logger.info("已添加测试文档")
        
        # 查询文档
        query_results = collection.query(
            query_texts=["什么是人工智能"],
            n_results=2
        )
        
        # 输出结果
        logger.info("查询结果:")
        if query_results.get("documents"):
            for i, doc in enumerate(query_results["documents"][0]):
                logger.info(f"结果 {i+1}: {doc}")
                if i < len(query_results.get("metadatas", [[]])[0]):
                    logger.info(f"元数据: {query_results['metadatas'][0][i]}")
        else:
            logger.info("未找到匹配的文档")
        
        # 测试成功
        logger.info("ChromaDB测试成功")
        
    except Exception as e:
        # 测试失败
        logger.error(f"ChromaDB测试失败: {str(e)}")

if __name__ == "__main__":
    test_chroma_db() 