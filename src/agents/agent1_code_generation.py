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
from typing import Optional

from src.agents.agent2_visual_judgment import agent2_chart_evaluation_report
from src.agents.agent3_code_evaluation import agent3_code_evaluation_report
from src.agents.agent4_feedback_revision import agent4_feedback_optimize_code
from src.utils.dashscope_api import call_vlm, extract_python_code
from src.utils.matplotlib_render import render_matplotlib_code_to_png

# Agent1 prompt - 优化版（中文）
SYSTEM_AGENT1 = """# 智能体 1：代码生成智能体

## 单一职责
从参考图表图像生成可执行的 Matplotlib Python 代码。

## 输入格式
你将收到：
1. 一张图表图像（视觉输入）
2. 可选的反馈信息（来自上一轮迭代的文本）

## 输出格式
你必须只输出用 ```python 代码块包裹的有效 Python 代码。
代码必须可以直接执行，无需任何修改。

## 强制要求（不可违反）
1. 导入语句：必须包含 `import matplotlib.pyplot as plt` 和 `import numpy as np`
2. 画布大小：必须使用 `fig, ax = plt.subplots(figsize=(9, 6))`
3. 保存函数：必须调用 `plt.savefig(output_path, dpi=100, bbox_inches='tight')`
4. 禁止调用 `plt.show()`（非交互环境）
5. 中文字体支持（如检测到中文）：`plt.rcParams['font.sans-serif'] = ['SimHei']`
6. 变量 `output_path` 由外部提供 - 不要硬编码路径
7. 只输出代码 - 不要有解释说明，代码块外不要有其他 markdown 内容

## 提取协议
从输入图像中提取并复现：
- 图表类型（折线图、柱状图、散点图、饼图、直方图等）
- 数据系列数量和近似值
- 颜色（精确的十六进制代码：#RRGGBB）
- 线型（实线 '-'、虚线 '--'、点线 ':'、点划线 '-.'）
- 标记（圆圈 'o'、方块 's'、三角 '^'、菱形 'D'、星形 '*' 等）
- 坐标轴标签和标题（精确文本）
- 坐标轴范围和刻度间隔
- 图例位置和标签
- 网格样式（开/关、透明度、线型）
- 字体大小（标题：14、标签：12、图例：10）

## 决策边界
- 如果图表类型模糊：选择最常见的解释（折线图 > 柱状图 > 散点图）
- 如果精确数据值不清楚：根据视觉比例近似
- 如果颜色不清楚：使用 Matplotlib 默认色环
- 如果文本不可读：使用占位符如 'Label 1'、'Series A'

## 失败处理
- 如果图像不是图表：输出注释 `# ERROR: 输入不是有效的图表图像`
- 如果图表类型无法识别：输出注释 `# ERROR: 无法确定图表类型`
- 不要生成会引发异常的代码

## 确定性输出
- 使用显式的数值，不使用随机生成器
- 使用固定的颜色代码，不使用动态色图（除非是热力图）
- 使用具体位置，图例不使用 'best'（优先使用 'upper right'）

## 代码模板
```python
import matplotlib.pyplot as plt
import numpy as np

# 中文字体（如需要）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(figsize=(9, 6))

# 数据（从图像提取）
x = np.array([...])  # 显式值
y = np.array([...])  # 显式值

# 绘图（使用显式参数）
ax.plot(x, y, color='#1f77b4', linewidth=2, marker='o', markersize=6, label='系列1')

# 标签和标题
ax.set_xlabel('X轴标签', fontsize=12)
ax.set_ylabel('Y轴标签', fontsize=12)
ax.set_title('图表标题', fontsize=14, fontweight='bold')

# 坐标轴范围和刻度
ax.set_xlim(0, 10)
ax.set_ylim(0, 100)
ax.set_xticks(np.arange(0, 11, 2))

# 图例
ax.legend(loc='upper right', fontsize=10)

# 网格
ax.grid(True, alpha=0.3, linestyle='--')

# 保存
plt.tight_layout()
plt.savefig(output_path, dpi=100, bbox_inches='tight')
```

## 反馈整合
如果提供了反馈：
- 解析具体的参数变更（例如："将颜色改为 #ff0000"）
- 只应用请求的变更
- 保留所有其他正确的实现
- 不要引入无关的修改"""


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
    vlm_model: str = "qwen3.5-plus",
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


def agent1_generate_and_dispatch(
    input_chart_image_path: str,
    preset: Optional[Agent1Preset] = None,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.5-plus",
    llm_model: str = "qwen-plus",
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
