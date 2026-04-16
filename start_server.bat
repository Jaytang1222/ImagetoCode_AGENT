@echo off
chcp 65001 >nul
echo ============================================================
echo   多智能体图表复现系统 - Web 服务启动脚本
echo ============================================================
echo.

REM 检查 API Key
if not defined DASHSCOPE_API_KEY (
    echo [警告] 未检测到 DASHSCOPE_API_KEY 环境变量
    echo 请先设置 API Key，例如:
    echo   set DASHSCOPE_API_KEY=your_api_key
    echo.
    pause
    exit /b 1
)

echo [✓] API Key 已配置
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo.

REM 启动服务
echo 正在启动 Web 服务...
echo.
python main.py

pause
