# 词根管理工具部署说明

## 1. 环境要求

### 1.1 后端环境
- Python 3.9+
- MySQL 5.7+

### 1.2 前端环境
- Node.js 16+
- npm 7+

## 2. 后端部署

### 2.1 安装依赖

```bash
# 进入项目根目录
cd root-word-manager

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置数据库

1. 确保 MySQL 服务器已启动
2. 运行数据库初始化脚本

```bash
# 运行数据库初始化脚本
python init_db.py
```

### 2.3 启动后端服务

```bash
# 启动后端服务（开发模式）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 或使用启动脚本
python start_backend.py
```

## 3. 前端部署

### 3.1 安装依赖

```bash
# 进入项目根目录
cd root-word-manager

# 安装依赖
npm install
```

### 3.2 构建前端项目

```bash
# 构建前端项目
npm run build
```

### 3.3 启动前端开发服务器

```bash
# 启动前端开发服务器
npm run dev
```

## 4. 生产环境部署

### 4.1 后端部署

1. 使用 Gunicorn 作为 WSGI 服务器
2. 使用 Nginx 作为反向代理

```bash
# 安装 Gunicorn
pip install gunicorn

# 使用 Gunicorn 启动服务
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 4.2 前端部署

1. 将构建后的静态文件部署到 Nginx 或其他静态文件服务器
2. 配置 Nginx 反向代理后端 API

## 5. 访问方式

### 5.1 前端页面

- 开发模式：http://localhost:8080
- 生产模式：根据部署配置的域名或 IP 访问

### 5.2 后端 API

- API 基础路径：http://localhost:8000/api
- API 文档：http://localhost:8000/docs

## 6. 默认账号

- 管理员账号：admin/admin123
- 普通用户账号：需通过管理员创建

## 7. 项目结构

```
root-word-manager/
├── app/
│   ├── api/             # API 路由
│   ├── models/          # 数据库模型
│   ├── schemas/         # Pydantic 模型
│   ├── services/        # 业务逻辑
│   ├── utils/           # 工具函数
│   ├── database.py      # 数据库配置
│   └── security.py      # 安全认证
├── src/                 # 前端代码
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   ├── views/           # 页面
│   ├── router/          # 路由
│   ├── api/             # API 调用
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── tests/               # 测试文件
├── main.py              # 后端入口
├── init_db.py           # 数据库初始化
├── package.json         # 前端依赖
├── requirements.txt     # 后端依赖
└── deployment.md        # 部署说明
```

## 8. 常见问题

### 8.1 数据库连接失败

- 检查 MySQL 服务器是否已启动
- 检查数据库连接配置是否正确
- 检查数据库用户权限是否足够

### 8.2 前端无法访问后端 API

- 检查后端服务是否已启动
- 检查前端代理配置是否正确
- 检查 CORS 配置是否正确

### 8.3 登录失败

- 检查用户名和密码是否正确
- 检查数据库中用户是否存在
- 检查 JWT 密钥配置是否正确

## 9. 技术支持

如遇到问题，请联系开发团队。
