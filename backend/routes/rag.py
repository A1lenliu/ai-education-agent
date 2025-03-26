from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import json
from backend.rag_service.chromadb import store_document, retrieve_document, get_collection_stats

router = APIRouter()

@router.post("/api/rag/upload")
async def upload_knowledge(file: UploadFile = File(...)):
    try:
        # 读取上传的文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 将内容按段落分割
        paragraphs = [p.strip() for p in content_str.split('\n\n') if p.strip()]
        
        # 存储每个段落
        for i, paragraph in enumerate(paragraphs):
            doc_id = f"{file.filename}_{i}"
            store_document(doc_id, paragraph)
        
        return {"message": f"成功上传 {len(paragraphs)} 个知识段落"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/rag/retrieve")
async def retrieve_knowledge(query: str):
    try:
        results = retrieve_document(query)
        # 如果没有找到相关文档，返回空列表而不是错误
        if not results:
            return {"results": []}
        return {"results": results}
    except Exception as e:
        # 发生错误时也返回空列表，而不是抛出错误
        return {"results": []}

@router.get("/api/rag/stats")
async def get_stats():
    try:
        count = get_collection_stats()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))