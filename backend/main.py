from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, database
import os
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import httpx
import json
from typing import Optional, Dict, Any, List
from .routes import react_agent
import asyncio
from .react_agent.agent import ReActAgent
from .react_agent.llm_client import DeepSeekLLMClient
from .react_agent.tools import ToolSet

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建工具集实例
tool_set = ToolSet()

# 创建 LLM 客户端
llm_client = DeepSeekLLMClient()

# 创建 ReAct 智能体
agent = ReActAgent(llm_client)

# 注册所有工具
for tool_name, tool_info in tool_set.tools.items():
    agent.add_tool(
        name=tool_name,
        description=tool_info["description"],
        parameters=tool_info["parameters"],
        handler=tool_info["handler"]
    )

# 添加请求模型
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    tool_results: List[Dict[str, Any]] = []
    api_key: Optional[str] = None

class ToolRequest(BaseModel):
    parameters: Dict[str, Any]

# 初始化 FastAPI 应用
app = FastAPI()

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 ReAct 路由
app.include_router(react_agent.router, prefix="/react-agent", tags=["react-agent"])

# LLM 聊天路由
@app.post("/llm/chat")
async def chat(request: ChatRequest):
    """处理 LLM 聊天请求"""
    try:
        # 设置 API 密钥
        if request.api_key:
            llm_client.set_api_key(request.api_key)
        
        # 执行 ReAct 循环
        result = await agent.execute(request.message)
        
        return {
            "response": result["response"],
            "history": result["history"],
            "tool_results": result["tool_results"]  # 确保返回工具结果
        }
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 工具路由
@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, request: ToolRequest):
    """执行指定的工具"""
    try:
        logger.info(f"执行工具 {tool_name}，参数: {request.parameters}")
        result = await tool_set.execute_tool(tool_name, request.parameters)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"执行工具时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 获取数据库会话
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试路由
@app.get("/")
def read_root():
    return {"message": "欢迎来到 AI 教育智能体！"}

# 登录接口
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user is None or db_user.password != password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"message": "登录成功"}

# 注册接口
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 调用 create_user 函数，确保数据被插入
    new_user = crud.create_user(db=db, username=username, password=password)
    return {"message": "注册成功", "username": new_user.username}

# 设置 DeepSeek API Key
DEEPSEEK_API_KEY = "sk-3b20bd773e754d5889566ff5455a93ce"  # 请替换为你的实际API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 修改为完整的API端点

# 配置 OpenAI 兼容客户端
openai.api_key = DEEPSEEK_API_KEY
openai.api_base = "https://api.deepseek.com/v1"  # 基础URL
openai.api_type = "deepseek"  # 指定API类型

# 添加测试路由
@app.get("/test")
async def test():
    return {"message": "API 服务器正常运行"}

@app.get("/")
async def root():
    return {"message": "ReAct智能体API服务正在运行"}