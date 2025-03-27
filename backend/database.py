from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL 连接配置
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost/education_system?charset=utf8mb4"

try:
    # 创建数据库引擎
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,  # 减小连接池大小
        max_overflow=10,  # 减小最大连接数
        echo=True,  # 开启 SQL 语句日志（调试用）
        pool_pre_ping=True  # 添加连接检查
    )
    
    # 测试数据库连接
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功！")
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")
    raise

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础 ORM 类
Base = declarative_base()
