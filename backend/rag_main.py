from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from .rag_service import api as rag_api
from . import simple_auth

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(title="RAG 知识检索服务")

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost:8002", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 输出所有可用的路由用于调试
for route in rag_api.router.routes:
    logger.info(f"RAG API路由: {route.path} [{','.join(route.methods)}]")

# 注册 RAG 服务路由
app.include_router(rag_api.router, prefix="/rag", tags=["rag"])

# 输出所有可用的应用路由用于调试
@app.on_event("startup")
async def startup_event():
    logger.info("RAG服务启动完成，以下是所有可用的路由:")
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            logger.info(f"App路由: {route.path} [{','.join(route.methods)}]")

# 登录接口
@app.post("/login")
def login(username: str, password: str):
    """使用简单认证模块登录"""
    return simple_auth.login(username, password)

# 注册接口
@app.post("/register")
def register(username: str, password: str):
    """使用简单认证模块注册用户"""
    return simple_auth.register(username, password)

@app.get("/")
async def root():
    return {"message": "RAG 知识检索服务已启动"}

@app.get("/health")
async def health_check():
    """健康检查端点，用于前端检测服务是否正常运行"""
    return {"status": "healthy", "service": "rag"} 