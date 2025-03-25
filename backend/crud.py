# crud.py
from sqlalchemy.orm import Session
from .models import User


def create_user(db: Session, username: str, password: str):
    db_user = User(username=username, password=password)  # 直接使用 User
    db.add(db_user)  # 将用户对象添加到数据库会话
    db.commit()  # 提交事务
    db.refresh(db_user)  # 刷新 db_user 对象，确保获取到数据库中的最新数据
    return db_user

# 获取用户

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()