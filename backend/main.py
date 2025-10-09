"""
后端服务启动入口
用于直接运行或通过 uv run 启动
"""
import uvicorn

def main():
    """启动 FastAPI 服务器"""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True  # 开发模式启用热重载
    )


if __name__ == "__main__":
    main()
