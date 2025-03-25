from sqlalchemy import Column, Integer, String
from backend.database import Base

# 定义 User 模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # 明文密码

    def verify_password(self, password: str):
        return self.password == password
