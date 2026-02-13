import pymysql
from sqlalchemy import create_engine
from app.database import Base, engine
from app.models import root_word, operation_log, user
from app.security import get_password_hash

# 创建数据库
def create_database():
    # 连接到 MySQL 服务器
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='123456',
        port=3306
    )
    
    try:
        with conn.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute("CREATE DATABASE IF NOT EXISTS root_word_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("数据库创建成功")
    finally:
        conn.close()

# 初始化表结构
def init_tables():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("表结构初始化成功")

# 初始化管理员用户
def init_admin_user():
    from sqlalchemy.orm import sessionmaker
    from app.database import SessionLocal
    from app.models.user import User
    
    db = SessionLocal()
    try:
        # 检查管理员用户是否存在
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建管理员用户
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("管理员用户初始化成功：admin/admin123")
        else:
            print("管理员用户已存在")
    finally:
        db.close()

# 主函数
if __name__ == "__main__":
    create_database()
    init_tables()
    init_admin_user()
    print("数据库初始化完成")
