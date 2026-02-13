from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

# 用户模型
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), nullable=False, unique=True, comment="用户名")
    password_hash = Column(String(256), nullable=False, comment="密码哈希")
    role = Column(String(16), nullable=False, default="user", comment="角色：user-普通用户，admin-管理员")
    create_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
