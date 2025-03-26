from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, models, database
import os
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import httpx  # 用于发送HTTP请求
import json
from typing import Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加请求模型
class ChatRequest(BaseModel):
    message: str

# 初始化 FastAPI 应用
app = FastAPI()

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

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
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 配置 OpenAI 兼容客户端
openai.api_key = DEEPSEEK_API_KEY
openai.api_base = DEEPSEEK_API_URL

# 定义请求数据格式
class LLMRequest(BaseModel):
    query: str  # 用户输入的问题
    history: list = []  # 聊天历史（可选）

# LLM 处理端点
@app.post("/llm/chat")
async def chat(request: ChatRequest):
    logger.info(f"收到聊天请求: {request.message}")
    
    try:
        # 准备请求数据
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": request.message}
            ]
        }

        logger.info(f"准备发送到 DeepSeek API 的数据: {json.dumps(data, ensure_ascii=False)}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=data
                )
                
                logger.info(f"DeepSeek API 响应状态码: {response.status_code}")
                logger.info(f"DeepSeek API 响应内容: {response.text}")

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                    return {"response": ai_response}
                else:
                    error_msg = f"DeepSeek API 错误: {response.text}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=response.status_code, detail=error_msg)
                    
            except httpx.RequestError as e:
                error_msg = f"请求 DeepSeek API 时发生错误: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
                
    except Exception as e:
        error_msg = f"处理请求时发生错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# 添加测试路由
@app.get("/test")
async def test():
    return {"message": "API 服务器正常运行"}