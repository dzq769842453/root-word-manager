from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.user import Token, UserResponse

router = APIRouter()

# 用户登录接口
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 查询用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    # 构建用户响应
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        create_time=user.create_time,
        update_time=user.update_time
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
