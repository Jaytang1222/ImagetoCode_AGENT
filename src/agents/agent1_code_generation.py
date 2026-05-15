# -*- coding: utf-8 -*-
"""
Agent 1 — 代码生成（图二）
输入：参考图表图片（路径）
输出：ECharts 用 JS（浏览器内联，div#main，全局 echarts）
模型：VLM（qwen-vl-max）
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from src.agents.agent2_visual_judgment import agent2_chart_evaluation_report
from src.agents.agent3_code_evaluation import agent3_code_evaluation_report
from src.agents.agent4_feedback_revision import agent4_feedback_optimize_code
from src.utils.dashscope_api import call_vlm, extract_python_code
from src.utils.matplotlib_render import render_matplotlib_code_to_png

# Agent1 prompt - 优化版（中文）
SYSTEM_AGENT1 = """# 代码生成智能体

从参考图表图像生成可执行的 Matplotlib Python 代码。

## 输出格式
只输出 ```python 代码块包裹的有效 Python 代码，代码可直接执行。

## 强制要求
1. 必须包含 `import matplotlib.pyplot as plt` 和 `import numpy as np`
2. 必须使用 `fig, ax = plt.subplots(figsize=(9, 6))`
3. 必须调用 `plt.savefig(output_path, dpi=100, bbox_inches='tight')`
4. 禁止 `plt.show()`（非交互环境）
5. 如有中文：`plt.rcParams['font.sans-serif'] = ['SimHei']`
6. 变量 `output_path` 由外部提供，不要硬编码路径
7. 所有数据使用显式数组（np.array([...])），禁止 np.random
8. 所有颜色使用十六进制（#RRGGBB），禁止颜色名（'blue'）
9. 图例位置使用具体值（'upper right'），禁止 'best'
10. 必须包含 `plt.tight_layout()`

## 常见错误禁止
- 禁止 np.random / 颜色名 / 中文变量名 / plt.figure() / plt.subplot()
- 直方图优先用 `ax.hist()`，不要手动调用 `np.histogram()`（只返回2个值）
- 不要使用无效的 rcParams（如 font.kerning）

## 提取优先级
P0 关键：图表类型、系列数量、轴标签/标题/图例文本
P1 高精度：颜色(#RRGGBB)、坐标轴范围(xlim/ylim)、刻度间隔、数据近似值
P2 中精度：线型(-/--/:/-.)、标记(o/s/^/D/*)、图例位置、网格样式
P3 美观：字体大小(标题14/标签12/图例10)、线宽、标记大小

## 决策
- 图表类型模糊 → 折线图 > 柱状图 > 散点图
- 数据/颜色不清 → 根据视觉比例近似 / 用默认色环(#1f77b4,#ff7f0e,#2ca02c,#d62728)
- 文本不可读 → 用占位符并在注释说明

## 反馈整合
如提供反馈：只应用明确请求的变更，优先处理高优先级项(P0>P1>P2)，保留正确实现。"""


@dataclass
class Agent1Preset:
    """
    Agent1 预设参数：
    - 是否生成代码图像；
    - 是否将图像/代码分发给后续智能体；
    - 各阶段输出目录与文件名。
    """

    generate_chart_image: bool = True
    dispatch_to_agents: bool = True  # 分发agent
    out_dir: str = "../outputs"
    generated_code_filename: str = "agent1_generated_matplotlib.py"
    generated_chart_filename: str = "agent1_generated_chart.png"
    save_reports: bool = True


@dataclass
class Agent1DispatchResult:
    """
    Agent1 增强流程结果：
    - generated_code: Agent1 生成代码
    - optimized_code: Agent4 修订代码（若执行了分发）
    - generated_chart_path: 由 Agent1 代码渲染出的图像路径
    - chart_report: Agent2 视觉评估报告
    - code_report: Agent3 代码评估报告
    """

    generated_code: str
    optimized_code: Optional[str]
    generated_chart_path: Optional[str]
    chart_report: Optional[str]
    code_report: Optional[str]


def agent1_generate_code(
    input_chart_image_path: str,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.6-plus",
) -> str:
    """
    根据输入图表生成 Matplotlib Python 代码。
    extra_feedback: 上一轮验证/评判失败时的补充说明，可注入到首轮之后的重试（由主流程传入）。
    """
    user_text = (
        "请阅读附图中的图表，并输出满足上述要求的完整 Python 代码。"
    ) # 用户prompt
    if extra_feedback:
        user_text += "\n\n【上一轮反馈与需改进点】\n" + extra_feedback.strip()

    messages = [
        {"role": "system", "content": SYSTEM_AGENT1},
        {
            "role": "user",
            "content": [
                {"image": input_chart_image_path},
                {"text": user_text},
            ],
        },
    ]
    raw = call_vlm(messages, model=vlm_model)
    code = extract_python_code(raw)
    return code


def agent1_generate_code_with_render(
    input_chart_image_path: str,
    out_dir: str,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.6-plus",
) -> Tuple[str, str]:
    """
    Agent1 简化版：仅生成代码并渲染图像，不调用其他Agent。
    专门为 Web 服务的显式编排设计。
    
    参数:
        input_chart_image_path: 输入图表图像路径
        out_dir: 输出目录
        extra_feedback: 可选的反馈信息
        vlm_model: VLM 模型名称
    
    返回:
        Tuple[str, str]: (生成的代码, 渲染的图像路径)
    
    异常:
        RuntimeError: 如果代码渲染失败
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # 生成代码
    code = agent1_generate_code(
        input_chart_image_path=input_chart_image_path,
        extra_feedback=extra_feedback,
        vlm_model=vlm_model,
    )
    
    # 保存代码
    code_path = os.path.join(out_dir, "agent1_generated_matplotlib.py")
    Path(code_path).write_text(code, encoding="utf-8")
    
    # 渲染图像
    png_path = os.path.join(out_dir, "agent1_generated_chart.png")
    rendered_path, error = render_matplotlib_code_to_png(code, png_path)
    
    if error:
        raise RuntimeError(f"Agent1 代码渲染失败: {error}")
    
    return code, rendered_path


def agent1_generate_and_dispatch(
    input_chart_image_path: str,
    preset: Optional[Agent1Preset] = None,
    extra_feedback: Optional[str] = None,
    vlm_model: Optional[str] = "qwen3.6-plus",
    llm_model: Optional[str] = None,
) -> Agent1DispatchResult:
    """
    Agent1 增强版能力：
    1) 根据输入图像生成代码；
    2) 根据预设渲染代码图像；
    3) 将生成图像输入 Agent2（视觉评估）；
    4) 将生成代码输入 Agent3（代码评估）与 Agent4（修订优化）。

    该函数不会改变现有流水线行为；仅在调用本函数时启用上述编排能力。
    """
    cfg = preset or Agent1Preset()
    os.makedirs(cfg.out_dir, exist_ok=True)

    generated_code = agent1_generate_code(
        input_chart_image_path=input_chart_image_path,
        extra_feedback=extra_feedback,
        vlm_model=vlm_model,
    )
    code_path = os.path.join(cfg.out_dir, cfg.generated_code_filename)
    Path(code_path).write_text(generated_code, encoding="utf-8")

    generated_chart_path: Optional[str] = None
    chart_report: Optional[str] = None
    code_report: Optional[str] = None
    optimized_code: Optional[str] = None

    if cfg.generate_chart_image:
        out_png = os.path.join(cfg.out_dir, cfg.generated_chart_filename)
        generated_chart_path, error = render_matplotlib_code_to_png(generated_code, out_png)
        if error:
            raise RuntimeError(f"Agent1 代码渲染失败: {error}")

    if cfg.dispatch_to_agents:
        if not generated_chart_path:
            raise RuntimeError(
                "Agent1 已启用分发，但未生成可用图像。请检查 Playwright 与渲染环境。"
            )

        # 生成图像 -> 视觉评估智能体
        chart_report = agent2_chart_evaluation_report(
            original_image_path=input_chart_image_path,
            generated_image_path=generated_chart_path,
            vlm_model=vlm_model,
        )
        # 生成代码 -> 代码评估智能体
        code_report = agent3_code_evaluation_report(
            echarts_inline_js=generated_code,
            chart_evaluation_report=chart_report,
            llm_model=llm_model,
        )
        # 生成代码 + 评估报告 -> 修订优化智能体
        optimized_code = agent4_feedback_optimize_code(
            echarts_inline_js=generated_code,
            code_evaluation_report=code_report,
            chart_evaluation_report=chart_report,
            llm_model=llm_model,
        )

        if cfg.save_reports:
            Path(os.path.join(cfg.out_dir, "agent1_dispatch_report_agent2.txt")).write_text(
                chart_report, encoding="utf-8"
            )
            Path(os.path.join(cfg.out_dir, "agent1_dispatch_report_agent3.txt")).write_text(
                code_report, encoding="utf-8"
            )
            Path(os.path.join(cfg.out_dir, "agent1_dispatch_code_agent4.py")).write_text(
                optimized_code, encoding="utf-8"
            )

    return Agent1DispatchResult(
        generated_code=generated_code,
        optimized_code=optimized_code,
        generated_chart_path=generated_chart_path,
        chart_report=chart_report,
        code_report=code_report,
    )
