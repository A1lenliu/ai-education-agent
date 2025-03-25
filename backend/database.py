from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 连接配置
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost/education_system?charset=utf8mb4"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出连接池的最大连接数
    echo=True  # 开启 SQL 语句日志（调试用）
)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础 ORM 类
Base = declarative_base()
