#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务重启脚本 - 关闭现有服务并重新启动
简化版：使用端口检查和简单的进程终止
"""
import sys
import subprocess
import time
import platform
from pathlib import Path

# 确保项目根目录在 Python 路径中
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

def kill_processes_simple():
    """简单粗暴地终止可能的服务进程"""
    print("\n[步骤 1/3] 关闭运行中的服务...")
    
    system = platform.system()
    killed_any = False
    
    if system == "Windows":
        # Windows: 终止占用端口的进程
        try:
            # 查找占用 8000 端口的进程（后端）
            print("  - 检查后端端口 8000...")
            result = subprocess.run(
                'netstat -ano | findstr :8000',
                capture_output=True,
                text=True,
                shell=True,
                timeout=3
            )
            
            if result.stdout:
                # 提取 PID
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 5 and parts[1].endswith(':8000'):
                        pid = parts[-1]
                        print(f"    终止进程 PID {pid}")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True, timeout=3)
                        killed_any = True
        except Exception as e:
            print(f"    跳过（{e}）")
        
        # 查找占用 5173/5174 端口的进程（前端）
        try:
            print("  - 检查前端端口 5173/5174...")
            for port in [5173, 5174]:
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=3
                )
                
                if result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split()
                        if len(parts) >= 5 and parts[1].endswith(f':{port}'):
                            pid = parts[-1]
                            print(f"    终止进程 PID {pid}")
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True, timeout=3)
                            killed_any = True
        except Exception as e:
            print(f"    跳过（{e}）")
        
        # 额外：终止所有 node.exe 进程（前端开发服务器）
        try:
            print("  - 清理 Node.js 进程...")
            result = subprocess.run(
                'taskkill /F /IM node.exe /T',
                capture_output=True,
                text=True,
                shell=True,
                timeout=3
            )
            if 'SUCCESS' in result.stdout:
                killed_any = True
        except Exception:
            pass
    
    else:
        # Linux/Mac: 使用 lsof 或 fuser
        try:
            # 终止占用 8000 端口的进程
            print("  - 检查后端端口 8000...")
            subprocess.run('lsof -ti:8000 | xargs kill -9', shell=True, timeout=3)
            killed_any = True
        except Exception:
            pass
        
        try:
            # 终止占用 5173 端口的进程
            print("  - 检查前端端口 5173...")
            subprocess.run('lsof -ti:5173 | xargs kill -9', shell=True, timeout=3)
            killed_any = True
        except Exception:
            pass
    
    if killed_any:
        print("  ✓ 服务进程已关闭")
    else:
        print("  未找到运行中的服务（或端口未占用）")
    
    return killed_any

def start_services():
    """启动服务"""
    print("\n[步骤 3/3] 启动新服务...")
    
    start_script = ROOT_DIR / "scripts" / "start_service.py"
    
    try:
        # 使用当前 Python 解释器启动服务
        subprocess.Popen(
            [sys.executable, str(start_script)],
            cwd=str(ROOT_DIR)
        )
        print("  ✓ 服务启动命令已执行")
    except Exception as e:
        print(f"  ✗ 启动服务失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔄 多智能体图表复现系统 - 服务重启")
    print("=" * 60)
    
    try:
        # 1. 关闭现有服务
        killed_any = kill_processes_simple()
        
        # 2. 等待端口释放
        if killed_any:
            print("\n[步骤 2/3] 等待端口释放...")
            time.sleep(2)
        
        # 3. 启动新服务
        start_services()
        
        print("\n" + "=" * 60)
        print("✓ 重启完成")
        print("=" * 60)
        print("\n提示：")
        print("  - 后端服务: http://localhost:8000")
        print("  - 前端服务: http://localhost:5173 或 http://localhost:5174")
        print("  - API 文档: http://localhost:8000/docs")
        print("=" * 60 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ 重启失败: {e}")
        sys.exit(1)
