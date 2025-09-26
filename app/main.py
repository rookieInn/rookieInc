"""
旅游路线规划智能体主应用
基于FastAPI框架，提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router
from app.api.auth import router as auth_router
from app.core.security import verify_token

# 加载环境变量
load_dotenv()

# 安全认证
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源
    pass

# 创建FastAPI应用
app = FastAPI(
    title="旅游路线规划智能体",
    description="基于AI的个性化旅游路线规划系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

# 静态文件服务
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    """根路径重定向到Web界面"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")

@app.get("/api")
async def api_root():
    """API根路径"""
    return {
        "message": "旅游路线规划智能体系统运行中",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "travel-agent"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )