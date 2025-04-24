import os
import re
import json
import uuid
import logging
import chromadb
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
from nltk.tokenize import sent_tokenize
import nltk
from .rag_prompt import generate_rag_prompt

# 下载nltk的sentence tokenizer数据
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

logger = logging.getLogger(__name__)

# 创建自定义嵌入函数类，符合ChromaDB新接口
class SimpleEmbeddingFunction:
    def __init__(self, dimension=384):
        self.dimension = dimension
    
    def __call__(self, input):
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

class RAGEngine:
    """
    RAG（检索增强生成）引擎
    使用ChromaDB作为向量数据库，支持文档的存储、检索和问答
    """
    
    def __init__(self, collection_name: str = "default_collection", model_name: str = None, use_local_model: bool = True):
        """
        初始化RAG引擎
        
        Args:
            collection_name: 向量数据库集合名称
            model_name: 嵌入模型名称，如果为None则使用默认模型
            use_local_model: 是否使用本地轻量级模型，避免下载大型模型
        """
        # 创建向量数据库存储目录
        self.db_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                        "knowledge_base", "chroma_db")
        os.makedirs(self.db_directory, exist_ok=True)
        
        # 初始化Chroma客户端
        self.client = chromadb.PersistentClient(path=self.db_directory)
        
        # 设置嵌入函数
        if use_local_model:
            # 使用自定义嵌入函数类
            logger.info("使用本地嵌入函数，避免下载模型")
            self.embedding_function = SimpleEmbeddingFunction()
        else:
            # 设置默认的嵌入函数
            model_name = model_name or "paraphrase-multilingual-MiniLM-L12-v2"  # 支持中文的多语言模型
            logger.info(f"使用SentenceTransformer模型: {model_name}")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )
        
        # 获取或创建集合
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"已连接到现有集合: {collection_name}")
        except Exception as e:
            logger.info(f"创建新集合: {collection_name}")
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
    
    def _get_simple_embedding_function(self):
        """
        创建一个简单的本地嵌入函数，无需下载模型
        这个函数不如预训练模型性能好，但可以在无法下载模型时使用
        
        注意：此方法已弃用，保留是为了向后兼容。建议直接使用SimpleEmbeddingFunction类
        
        Returns:
            嵌入函数
        """
        # 创建并返回SimpleEmbeddingFunction的实例
        return SimpleEmbeddingFunction()
    
    def process_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        处理文本并分块
        
        Args:
            text: 输入文本
            chunk_size: 块大小（字符数）
            chunk_overlap: 块重叠（字符数）
            
        Returns:
            文本块列表
        """
        # 清理文本
        text = re.sub(r'\s+', ' ', text).strip()
        
        try:
            # 尝试使用NLTK进行句子分割
            sentences = sent_tokenize(text)
        except Exception as e:
            # 如果NLTK分割失败，使用简单的正则表达式进行分割
            logger.warning(f"NLTK句子分割失败: {str(e)}，使用简单的正则表达式替代")
            # 使用常见的句子结束符来分割文本
            sentences = re.split(r'(?<=[.!?。！？])\s+', text)
            if len(sentences) == 1:  # 如果没有找到句子边界，按固定长度分割
                sentences = [text[i:i+200] for i in range(0, len(text), 200)]
        
        # 创建块
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # 如果添加当前句子会超过块大小，并且当前块不为空，则保存当前块
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # 保留部分重叠
                current_chunk = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
            
            current_chunk += " " + sentence
        
        # 添加最后一块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def add_document(self, document: str, metadata: Dict[str, Any] = None, doc_id: str = None) -> str:
        """
        添加文档到向量数据库
        
        Args:
            document: 文档文本
            metadata: 文档元数据
            doc_id: 文档ID（如果未提供，将自动生成）
            
        Returns:
            文档ID
        """
        if doc_id is None:
            doc_id = str(uuid.uuid4())
            
        if metadata is None:
            metadata = {}
            
        # 处理文档
        chunks = self.process_text(document)
        
        # 为每个块添加唯一ID
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # 为每个块准备元数据
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "doc_id": doc_id,
                "chunk_id": i,
                "chunk_total": len(chunks)
            })
            metadatas.append(chunk_metadata)
        
        # 添加到向量数据库
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"已添加文档 {doc_id}，共 {len(chunks)} 个块")
        return doc_id
    
    def search(self, query: str, top_k: int = 5, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        搜索相关文档块
        
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
            filter_criteria: 过滤条件
            
        Returns:
            相关文档块列表
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_criteria
        )
        
        # 处理结果
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if i < len(results["metadatas"][0]) else {},
                    "id": results["ids"][0][i] if i < len(results["ids"][0]) else "",
                    "score": float(results["distances"][0][i]) if "distances" in results and i < len(results["distances"][0]) else 0.0
                })
        
        return formatted_results
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            # 删除所有与文档ID匹配的块
            self.collection.delete(
                where={"doc_id": doc_id}
            )
            logger.info(f"已删除文档: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False

    def get_document_ids(self) -> List[str]:
        """
        获取所有文档ID
        
        Returns:
            文档ID列表
        """
        try:
            # 查询所有元数据
            results = self.collection.get()
            
            # 提取唯一的文档ID
            doc_ids = set()
            if results and "metadatas" in results and results["metadatas"]:
                for metadata in results["metadatas"]:
                    if metadata and "doc_id" in metadata:
                        doc_ids.add(metadata["doc_id"])
            
            return list(doc_ids)
        except Exception as e:
            logger.error(f"获取文档ID失败: {str(e)}")
            return []
    
    def get_document_content(self, doc_id: str) -> Dict[str, Any]:
        """
        获取文档的完整内容
        
        Args:
            doc_id: 文档ID
            
        Returns:
            包含文档内容和元数据的字典
        """
        try:
            # 查询与文档ID匹配的所有块
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if not results or not results["documents"] or len(results["documents"]) == 0:
                logger.error(f"未找到文档: {doc_id}")
                return None
            
            # 按块ID排序
            chunks = []
            for i, doc in enumerate(results["documents"]):
                chunk_id = results["metadatas"][i].get("chunk_id", 0)
                chunks.append((chunk_id, doc, results["metadatas"][i]))
            
            chunks.sort(key=lambda x: x[0])
            
            # 合并所有块的内容
            content = " ".join([chunk[1] for chunk in chunks])
            
            # 获取第一个块的元数据作为文档元数据
            metadata = chunks[0][2] if chunks else {}
            
            # 从元数据中获取标题等信息
            title = metadata.get("title", "未命名文档")
            author = metadata.get("author", "")
            tags = metadata.get("tags", "")
            
            return {
                "doc_id": doc_id,
                "title": title,
                "author": author,
                "tags": tags,
                "content": content
            }
        except Exception as e:
            logger.error(f"获取文档内容失败: {str(e)}")
            return None
            
    def generate_prompt(self, query: str, context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        为RAG生成提示模板
        
        Args:
            query: 用户查询
            context: 检索的上下文
            
        Returns:
            提示消息列表
        """
        # 使用专用RAG提示模板
        return generate_rag_prompt(query, context) 