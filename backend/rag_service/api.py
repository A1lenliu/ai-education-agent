from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import json
import os
import asyncio
from .rag_engine import RAGEngine
from ..react_agent.llm_client import DeepSeekLLMClient

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 初始化RAG引擎
rag_engine = RAGEngine(collection_name="ai_education")

# 初始化独立的LLM客户端，专用于RAG服务
rag_llm_client = DeepSeekLLMClient(
    api_key="sk-3b20bd773e754d5889566ff5455a93ce",  # 使用与主应用相同的API密钥或设置新的密钥
    verify_ssl=False
)
logger.info("已创建专用于RAG服务的DeepSeek LLM客户端")

# 定义请求模型
class DocumentUploadRequest(BaseModel):
    document: str
    title: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    
class DeleteDocumentRequest(BaseModel):
    doc_id: str

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    use_rag: Optional[bool] = True

# 获取RAG引擎实例
def get_rag_engine():
    return rag_engine

# 封装LLM调用的辅助函数，处理新的消息格式
async def query_llm_with_messages(messages: List[Dict[str, str]]) -> str:
    """
    使用消息列表格式查询LLM
    
    Args:
        messages: 消息列表
        
    Returns:
        LLM响应文本
    """
    try:
        # 转换为DeepSeek LLM客户端需要的格式
        response = await rag_llm_client.chat_completion(messages=messages)
        return response
    except Exception as e:
        logger.error(f"查询LLM时出错: {str(e)}")
        raise e

# API端点
@router.post("/document/upload")
async def upload_document(request: DocumentUploadRequest):
    """
    上传文档到知识库
    """
    try:
        # 处理标签列表
        tags_str = ", ".join(request.tags) if request.tags else ""
        
        # 准备元数据，确保所有值都是ChromaDB支持的类型
        metadata = {
            "title": str(request.title or "未命名文档"),
            "author": str(request.author) if request.author else "",
            "tags": tags_str
        }
        
        # 过滤掉所有空值
        metadata = {k: v for k, v in metadata.items() if v}
        
        # 添加文档
        doc_id = rag_engine.add_document(request.document, metadata)
        
        return {"status": "success", "message": "文档已成功添加", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"上传文档时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传文档失败: {str(e)}")

@router.post("/document/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(None),
    author: str = Form(None),
    tags: str = Form(None)
):
    """
    上传文件到知识库
    """
    try:
        # 读取文件内容
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # 解析标签
        tag_list = json.loads(tags) if tags else []
        # 将标签列表转换为字符串，避免使用列表类型
        tags_str = ", ".join(tag_list) if tag_list else ""
        
        # 准备元数据，确保所有值都是ChromaDB支持的类型（字符串、整数、浮点数或布尔值）
        metadata = {
            "title": str(title or file.filename),
            "author": str(author) if author else "",
            "tags": tags_str,  # 使用字符串而不是列表
            "filename": str(file.filename)
        }
        
        # 过滤掉所有空值
        metadata = {k: v for k, v in metadata.items() if v}
        
        # 添加文档
        doc_id = rag_engine.add_document(text_content, metadata)
        
        return {"status": "success", "message": "文件已成功添加", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"上传文件时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")

@router.post("/search")
async def search_documents(request: QueryRequest):
    """
    搜索文档
    """
    try:
        results = rag_engine.search(request.query, top_k=request.top_k)
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"搜索文档时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.post("/document/delete")
async def delete_document(request: DeleteDocumentRequest):
    """
    删除文档
    """
    try:
        success = rag_engine.delete_document(request.doc_id)
        if success:
            return {"status": "success", "message": f"文档 {request.doc_id} 已成功删除"}
        else:
            raise HTTPException(status_code=404, detail=f"删除文档 {request.doc_id} 失败")
    except Exception as e:
        logger.error(f"删除文档时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.get("/documents")
async def get_documents():
    """
    获取所有文档ID
    """
    try:
        doc_ids = rag_engine.get_document_ids()
        return {"status": "success", "doc_ids": doc_ids}
    except Exception as e:
        logger.error(f"获取文档列表时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@router.get("/document/content")
async def get_document_content(doc_id: str):
    """
    获取指定文档的内容
    """
    try:
        document = rag_engine.get_document_content(doc_id)
        if document:
            return {"status": "success", "document": document}
        else:
            raise HTTPException(status_code=404, detail=f"未找到文档 {doc_id}")
    except Exception as e:
        logger.error(f"获取文档内容时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档内容失败: {str(e)}")

@router.post("/query")
async def query_rag(request: RAGQueryRequest):
    """
    RAG问答查询
    """
    try:
        # 准备基本的系统消息
        system_message = {
            "role": "system", 
            "content": "你是一个专业的知识库问答助手，请用简体中文回答用户的问题。"
        }
        
        # 如果启用RAG，先检索相关内容
        if request.use_rag:
            # 检索相关文档
            contexts = rag_engine.search(request.query, top_k=request.top_k)
            
            # 如果没有找到任何相关内容，直接将查询发送给模型
            if not contexts:
                logger.info("未找到相关文档，直接查询RAG专用LLM")
                
                # 构建简单的消息
                messages = [
                    system_message,
                    {"role": "user", "content": f"我在知识库中没有找到与'{request.query}'相关的信息。请提供一个礼貌的回应，说明无法从知识库中找到相关内容。"}
                ]
                
                # 查询LLM
                response = await query_llm_with_messages(messages)
                return {"status": "success", "answer": response, "contexts": []}
            
            # 构建RAG提示
            messages = rag_engine.generate_prompt(request.query, contexts)
            
            # 查询LLM
            logger.info("使用RAG专用LLM执行查询")
            response = await query_llm_with_messages(messages)
        else:
            # 不使用RAG，直接查询LLM
            logger.info("不使用RAG，直接查询RAG专用LLM")
            
            # 构建简单的消息
            messages = [
                system_message,
                {"role": "user", "content": request.query}
            ]
            
            # 查询LLM
            response = await query_llm_with_messages(messages)
            contexts = []
        
        return {
            "status": "success", 
            "answer": response, 
            "contexts": contexts if request.use_rag else []
        }
    except Exception as e:
        logger.error(f"RAG查询时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}") 