from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/root_word_manager"

# 创建数据库引擎 - 添加连接池优化
engine = create_engine(
    DATABASE_URL,
    pool_size=10,              # 连接池大小
    max_overflow=20,           # 最大溢出连接数
    pool_pre_ping=True,        # 连接前ping测试
    pool_recycle=3600,         # 连接回收时间（1小时）
    echo=False                 # 关闭SQL日志输出
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
