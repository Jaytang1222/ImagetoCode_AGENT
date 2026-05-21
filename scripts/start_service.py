#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务启动脚本 - 同时启动后端和前端服务
Ctrl+C 可同时停止两个服务
"""
import sys
import subprocess
import time
from pathlib import Path

# 确保项目根目录在 Python 路径中
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Conda 环境名（确保后端在正确的环境中运行）
CONDA_ENV = "Py313"


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 多智能体图表复现系统 - 全栈服务启动")
    print("=" * 60)
    print("正在启动后端和前端服务...")
    print("按 Ctrl+C 停止所有服务")
    print("=" * 60 + "\n")

    # --- 后端：通过 conda run 在 Py313 环境中启动 uvicorn ---
    print("=" * 60)
    print("🚀 后端服务启动中...")
    print("=" * 60)
    print(f"📁 项目根目录: {ROOT_DIR}")
    print(f"🌐 API 文档: http://localhost:8001/docs")
    print(f"🔗 健康检查: http://localhost:8001/health")
    print("=" * 60)

    backend_proc = subprocess.Popen(
        ["conda", "run", "-n", CONDA_ENV, "--no-capture-output",
         "python", "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8001"],
        cwd=str(ROOT_DIR)
    )
    time.sleep(2)

    # --- 前端：通过 cmd /c 调用 npm ---
    frontend_dir = ROOT_DIR / "frontend"
    print("=" * 60)
    print("🎨 前端服务启动中...")
    print("=" * 60)
    print(f"📁 前端目录: {frontend_dir}")
    print(f"🌐 前端地址: http://localhost:5174")
    print("=" * 60)

    try:
        subprocess.run(["cmd", "/c", "npm run dev"], cwd=str(frontend_dir))
    except KeyboardInterrupt:
        pass
    finally:
        print("\n\n" + "=" * 60)
        print("🛑 正在停止所有服务...")
        print("=" * 60)

        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_proc.kill()
            backend_proc.wait()

        print("✅ 所有服务已停止")
