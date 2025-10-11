"""
FastAPI 主应用入口
用于处理需求说明书生成的后端逻辑
"""
# 第一步：加载环境变量（必须在所有导入之前）
from dotenv import load_dotenv
load_dotenv()

# 第二步：导入其他模块
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import upload, generate, auth, admin, cache
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库
    """
    # 启动时执行
    print("🚀 启动应用...")
    init_db()
    print("✅ 数据库初始化完成")

    yield

    # 关闭时执行
    print("👋 关闭应用...")


app = FastAPI(
    title="需求说明书生成工具 API",
    description="自动化生成需求说明书的后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(generate.router, prefix="/api/generate", tags=["文档生成"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
app.include_router(cache.router, prefix="/api/cache", tags=["缓存管理"])


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "running",
        "message": "需求说明书生成工具 API 运行中"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # 默认运行在 8000 端口
    uvicorn.run(app, host="127.0.0.1", port=8000)
