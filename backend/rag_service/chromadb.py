import chromadb
from chromadb.config import Settings
import os

# 确保知识库目录存在
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

# 初始化 ChromaDB 客户端
chroma_client = chromadb.Client(Settings(
    persist_directory=KNOWLEDGE_BASE_DIR,
    anonymized_telemetry=False
))

# 创建或获取集合
collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

def store_document(document_id: str, content: str):
    """
    存储文档到 ChromaDB
    :param document_id: 文档ID
    :param content: 文档内容
    """
    try:
        collection.add(
            documents=[content],
            ids=[document_id],
            metadatas=[{"source": "upload"}]
        )
        return True
    except Exception as e:
        print(f"存储文档时出错: {str(e)}")
        return False

def retrieve_document(query: str, n_results: int = 5):
    """
    从 ChromaDB 检索相关文档
    :param query: 查询文本
    :param n_results: 返回结果数量
    :return: 相关文档列表
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]
    except Exception as e:
        print(f"检索文档时出错: {str(e)}")
        return []

def delete_document(document_id: str):
    """
    从 ChromaDB 删除文档
    :param document_id: 文档ID
    """
    try:
        collection.delete(ids=[document_id])
        return True
    except Exception as e:
        print(f"删除文档时出错: {str(e)}")
        return False

def get_collection_stats():
    """
    获取集合统计信息
    :return: 集合中的文档数量
    """
    try:
        return collection.count()
    except Exception as e:
        print(f"获取集合统计信息时出错: {str(e)}")
        return 0