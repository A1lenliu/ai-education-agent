from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..react_agent.agent import ReActAgent
from ..react_agent.tools import ToolSet
from ..react_agent.llm_client import DeepSeekLLMClient
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class QueryResponse(BaseModel):
    result: str
    conversation_history: List[Dict[str, str]]
    tool_results: List[Dict[str, Any]] = []

# 创建全局的ReAct智能体实例
logger.info("初始化 ReAct 智能体...")
tool_set = ToolSet()
llm_client = DeepSeekLLMClient(verify_ssl=False)
agent = ReActAgent(llm_client)

# 注册工具
logger.info("注册工具...")
for name, tool_info in tool_set.tools.items():
    agent.add_tool(
        name=name,
        description=tool_info["description"],
        parameters=tool_info["parameters"],
        handler=tool_info["handler"]
    )
logger.info("工具注册完成")

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """处理用户查询请求"""
    try:
        logger.info(f"收到查询请求: {request.query}")
        
        # 如果提供了新的API密钥，更新LLM客户端
        if request.api_key:
            logger.info("更新 API 密钥")
            llm_client.api_key = request.api_key
        
        # 运行ReAct智能体
        logger.info("开始运行 ReAct 智能体...")
        result = await agent.execute(request.query)
        logger.info(f"ReAct 智能体运行完成，结果: {result}")
        
        # 返回结果和对话历史
        response = QueryResponse(
            result=result["response"],
            conversation_history=[
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "type": msg.get("type", "unknown")
                }
                for msg in result["history"]
            ],
            tool_results=result.get("tool_results", [])
        )
        logger.info("准备返回响应")
        return response
        
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 