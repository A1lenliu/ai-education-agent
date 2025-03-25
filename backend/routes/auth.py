from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.crud import create_user, get_user_by_username
from backend.database import SessionLocal
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

# 创建 APIRouter 实例
router = APIRouter()

# 请求体模型
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# 生成 JWT 令牌
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 注册新用户
@router.post("/register")
def register(user: UserCreate):
    db = SessionLocal()
    # 检查用户名是否存在
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建新用户
    new_user = create_user(db, user.username, user.password)
    
    return {"message": "注册成功"}

# 用户登录
@router.post("/login")
def login(user: UserLogin):
    db = SessionLocal()
    # 查询用户
    db_user = get_user_by_username(db, user.username)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 创建 JWT 令牌
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
