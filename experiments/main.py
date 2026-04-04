# -*- coding: utf-8 -*-
"""
多智能体图表复现主入口：Agent1→2→3→4 + 多维验证器（见 agent_pipeline.py）。

使用前请设置环境变量 DASHSCOPE_API_KEY，并安装依赖：
  pip install -r requirements.txt
  playwright install chromium
"""
from __future__ import annotations

import argparse
import os
import sys

# 保证从项目根目录可导入本地模块
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from Agents.agent_pipeline import run_full_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="多智能体 ECharts 图表复现流水线")
    parser.add_argument(
        "-i",
        "--input",
        default="input.png",
        help="输入参考图表图片路径",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="outputs",
        help="输出目录（代码、HTML、截图、报告）",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=5,
        help="最大迭代轮数",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="验证器通过分数阈值（0~1）",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"未找到输入图片: {args.input}")
        print("请将参考图放在该路径，或使用 -i 指定。")
        sys.exit(1)

    ok, code_path, png_path, summary = run_full_pipeline(
        input_chart_image=args.input,
        out_dir=args.out,
        max_loops=args.max_loops,
        threshold=args.threshold,
    )
    print("\n--- 结果 ---")
    print("验证通过:", ok)
    print("代码文件:", code_path)
    print("渲染图:", png_path)
    print("摘要:", summary)


if __name__ == "__main__":
    main()
