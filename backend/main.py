from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, database

# 初始化 FastAPI 应用
app = FastAPI()

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