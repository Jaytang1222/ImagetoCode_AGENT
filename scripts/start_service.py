#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务启动脚本 - 同时启动后端和前端服务
确保所有模块导入路径正确
"""
import sys
import subprocess
import threading
import time
from pathlib import Path

# 确保项目根目录在 Python 路径中
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def start_backend():
    """启动后端服务"""
    import uvicorn
    from backend.main import app
    
    print("=" * 60)
    print("🚀 后端服务启动中...")
    print("=" * 60)
    print(f"📁 项目根目录: {ROOT_DIR}")
    print(f"🌐 API 文档: http://localhost:8001/docs")
    print(f"🔗 健康检查: http://localhost:8001/health")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)

def start_frontend():
    """启动前端服务"""
    frontend_dir = ROOT_DIR / "frontend"
    
    print("=" * 60)
    print("🎨 前端服务启动中...")
    print("=" * 60)
    print(f"📁 前端目录: {frontend_dir}")
    print(f"🌐 前端地址: http://localhost:5174")
    print("=" * 60)
    
    # 使用 npm run dev 启动前端开发服务器
    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=str(frontend_dir),
            shell=True
        )
    except KeyboardInterrupt:
        print("\n前端服务已停止")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 多智能体图表复现系统 - 全栈服务启动")
    print("=" * 60)
    print("正在启动后端和前端服务...")
    print("按 Ctrl+C 停止所有服务")
    print("=" * 60 + "\n")
    
    # 在单独的线程中启动后端
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 等待后端启动
    time.sleep(2)
    
    # 在主线程中启动前端（这样可以捕获 Ctrl+C）
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 正在停止所有服务...")
        print("=" * 60)
        sys.exit(0)
