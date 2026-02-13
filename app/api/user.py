from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.security import get_password_hash, get_current_user
from app.models.user import User
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()

# 请求模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    role: str = Field(default="user", description="角色：user-普通用户，admin-管理员")

class UserListResponse(BaseModel):
    id: int
    username: str
    role: str
    create_time: Optional[str]
    update_time: Optional[str]

class UserListData(BaseModel):
    list: List[UserListResponse]
    total: int

class UserListResult(BaseModel):
    code: int
    msg: str
    data: UserListData

# 检查管理员权限
def check_admin_permission(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以管理用户"
        )
    return current_user

# 创建用户
@router.post("/create", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证角色
    if user_data.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色只能是 user 或 admin"
        )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "code": 200,
        "msg": "用户创建成功",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role
        }
    }

# 获取用户列表
@router.get("/list", response_model=UserListResult)
async def get_user_list(
    page_num: int = 1,
    page_size: int = 10,
    username: str = None,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 构建查询
    query = db.query(User)
    
    # 按用户名筛选
    if username:
        query = query.filter(User.username.contains(username))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    users = query.order_by(desc(User.create_time)).offset((page_num - 1) * page_size).limit(page_size).all()
    
    # 构建响应数据
    user_list = []
    for user in users:
        user_list.append(UserListResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            create_time=user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None,
            update_time=user.update_time.strftime("%Y-%m-%d %H:%M:%S") if user.update_time else None
        ))
    
    return UserListResult(
        code=200,
        msg="获取用户列表成功",
        data=UserListData(
            list=user_list,
            total=total
        )
    )

# 删除用户
@router.delete("/delete/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.username == current_user.get("username"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的用户"
        )
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {
        "code": 200,
        "msg": "用户删除成功",
        "data": None
    }

# 重置用户密码
@router.post("/reset-password/{user_id}", response_model=dict)
async def reset_password(
    user_id: int,
    new_password: str,
    current_user: dict = Depends(check_admin_permission),
    db: Session = Depends(get_db)
):
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {
        "code": 200,
        "msg": "密码重置成功",
        "data": None
    }
