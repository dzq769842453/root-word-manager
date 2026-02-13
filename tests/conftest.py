import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine, get_db
from app.models.user import User
from app.security import get_password_hash
from main import app

# 创建测试数据库表
@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 创建测试客户端
@pytest.fixture
def client(test_db):
    # 创建测试用户
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # 创建管理员用户
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin_user)
    
    # 创建普通用户
    normal_user = User(
        username="user",
        password_hash=get_password_hash("user123"),
        role="user"
    )
    db.add(normal_user)
    
    db.commit()
    db.close()
    
    return TestClient(app)

# 获取管理员 token
@pytest.fixture
def admin_token(client):
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    return response.json()["access_token"]

# 获取普通用户 token
@pytest.fixture
def user_token(client):
    response = client.post("/api/auth/login", data={
        "username": "user",
        "password": "user123"
    })
    return response.json()["access_token"]
