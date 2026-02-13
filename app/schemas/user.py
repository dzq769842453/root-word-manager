from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 用户登录请求模型
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名", min_length=1, max_length=32)
    password: str = Field(..., description="密码", min_length=1)

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

# 令牌响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 令牌数据模型
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
