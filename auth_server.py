"""
独立的简单认证服务器
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="认证服务")

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 用户数据
users = {
    "admin": "admin123",
    "test": "test123",
    "buluga1sy": "123"
}

@app.post("/login")
def login(username: str, password: str):
    """登录接口"""
    if username in users and users[username] == password:
        return {"message": "登录成功"}
    raise HTTPException(status_code=400, detail="用户名或密码错误")

@app.post("/register")
def register(username: str, password: str):
    """注册接口"""
    if username in users:
        raise HTTPException(status_code=400, detail="用户名已存在")
    users[username] = password
    return {"message": "注册成功", "username": username}

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "auth"}

@app.get("/")
def root():
    """根路径接口"""
    return {"message": "认证服务已启动"}

if __name__ == "__main__":
    print("启动认证服务器，端口 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002) 