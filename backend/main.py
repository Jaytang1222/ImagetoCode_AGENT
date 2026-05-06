"""
FastAPI主应用入口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径（必须在所有其他导入之前）
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time

from backend.api import upload, pipeline, results, download, history
from backend.websocket.manager import manager
from backend.utils.logger import app_logger, log_request

# 创建FastAPI应用
app = FastAPI(
    title="多智能体图表复现系统API",
    description="基于阿里云DashScope的多智能体流水线API",
    version="1.0.0"
)

# CORS配置（必须在其他中间件之前注册）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    log_request(request.method, request.url.path, response.status_code, duration)
    return response

# 挂载静态文件目录
os.makedirs("storage/uploads", exist_ok=True)
os.makedirs("storage/outputs", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="storage/uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="storage/outputs"), name="outputs")

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["上传"])
app.include_router(pipeline.router, prefix="/api", tags=["流水线"])
app.include_router(results.router, prefix="/api", tags=["结果"])
app.include_router(download.router, prefix="/api", tags=["下载"])
app.include_router(history.router, prefix="/api", tags=["历史"])

# WebSocket路由
@app.websocket("/ws/{pipeline_id}")
async def websocket_endpoint(websocket: WebSocket, pipeline_id: str):
    await manager.connect(websocket, pipeline_id)
    try:
        while True:
            # 保持连接
            await websocket.receive_text()
    except Exception as e:
        # 忽略正常的客户端断开连接（错误码 1005, 1000, 1001）
        error_code = getattr(e, 'code', None)
        if error_code not in [1000, 1001, 1005]:
            app_logger.error(f"WebSocket错误 [{pipeline_id}]: {e}")
    finally:
        manager.disconnect(pipeline_id)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 根路径
@app.get("/")
async def root():
    return {
        "message": "多智能体图表复现系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    app_logger.info("=" * 50)
    app_logger.info("多智能体图表复现系统API启动")
    app_logger.info("API文档: http://localhost:8000/docs")
    app_logger.info("=" * 50)

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("API服务器关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
