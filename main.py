from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import auth, root_word

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="词根管理工具 API",
    description="数据开发团队词根标准化管理工具",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(root_word.router, prefix="/api/root-word", tags=["词根管理"])

# 根路径
@app.get("/")
def read_root():
    return {"message": "词根管理工具 API", "version": "1.0.0"}

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}
