#!/bin/bash

echo "============================================================"
echo "  多智能体图表复现系统 - Web 服务启动脚本"
echo "============================================================"
echo ""

# 检查 API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "[警告] 未检测到 DASHSCOPE_API_KEY 环境变量"
    echo "请先设置 API Key，例如:"
    echo "  export DASHSCOPE_API_KEY=your_api_key"
    echo ""
    exit 1
fi

echo "[✓] API Key 已配置"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

echo "[✓] Python 已安装"
echo ""

# 启动服务
echo "正在启动 Web 服务..."
echo ""
python3 main.py
