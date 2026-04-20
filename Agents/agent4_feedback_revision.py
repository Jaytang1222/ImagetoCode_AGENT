# -*- coding: utf-8 -*-
"""
Agent 4 — 修订评判 / 反馈优化（流程图 + 图五）
输入：当前 Matplotlib Python 代码 + Agent3 的代码评估报告 + Agent2 的图表评估报告
输出：综合两份报告后的**完整修改后 Python 代码**（必须包含 import 和 plt.savefig(output_path)）
模型：LLM
"""
from __future__ import annotations

from utils.dashscope_api import call_llm, extract_python_code

SYSTEM_AGENT4 = """你是 Matplotlib 修订优化智能体。你会收到：
1. 当前的 Matplotlib Python 代码；
2. 来自代码审查智能体（Agent3）的代码评估与修正指导；
3. 来自视觉审查智能体（Agent2）的结构化视觉差异报告。

你的任务是整合"视觉维度 + 代码维度"的异构反馈，执行渐进式修正并输出下一轮候选代码。
所谓渐进式修正：优先修复高优先级且可验证的差异（P0/P1），保留已正确部分，避免无关大改。

修订策略（必须遵守）：
1) 先处理视觉关键差异：颜色相似度、坐标轴精度/刻度、文本一致性、结构/趋势一致性。
2) 再处理代码质量问题：可读性、变量命名（以不破坏视觉修复为前提）。
3) 若 Agent3 报告中存在 Agent4_Input / PriorityFixes / MustKeep / PatchHints，必须优先采用。
4) 修改需可被验证器在下一轮评估：避免随机行为、避免与目标图无关的样式改动。

输出要求：
- 只输出一份完整、可直接执行的 Python 代码
- 必须包含所有必要的 import 语句（import matplotlib.pyplot as plt, import numpy as np）
- 必须调用 plt.savefig(output_path, dpi=100, bbox_inches='tight')
- 不要调用 plt.show()（非交互环境）
- 如果有中文，必须设置字体：plt.rcParams['font.sans-serif'] = ['SimHei']
- 使用 ```python 代码块包裹
- 保持代码可执行且结构清晰
- output_path 变量会由外部传入，不要硬编码路径

代码结构示例：
```python
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（如果需要）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(figsize=(9, 6))

# 数据
x = np.array([...])
y = np.array([...])

# 绘图（根据反馈修正颜色、线型、标记等）
ax.plot(x, y, color='#1f77b4', linewidth=2, marker='o', label='系列1')

# 设置标签和标题（根据反馈修正文本）
ax.set_xlabel('X轴', fontsize=12)
ax.set_ylabel('Y轴', fontsize=12)
ax.set_title('标题', fontsize=14)

# 坐标轴范围和刻度（根据反馈修正）
ax.set_xlim(0, 10)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 11, 2))

# 图例
ax.legend(loc='upper right')

# 网格
ax.grid(True, alpha=0.3)

# 保存
plt.tight_layout()
plt.savefig(output_path, dpi=100, bbox_inches='tight')
```"""


def agent4_feedback_optimize_code(
    echarts_inline_js: str,
    code_evaluation_report: str,
    chart_evaluation_report: str,
    llm_model: str = "qwen-plus",
) -> str:
    user = (
        "【代码审查智能体输出（Agent3）】\n"
        f"{code_evaluation_report}\n\n"
        "【视觉审查智能体输出（Agent2）】\n"
        f"{chart_evaluation_report}\n\n"
        "【当前代码】\n"
        f"``python\n{echarts_inline_js}\n```\n\n"
        "请融合两类反馈进行渐进式修正，输出可进入验证器下一轮评估的完整 Python 代码。"
    )
    messages = [
        {"role": "system", "content": SYSTEM_AGENT4},
        {"role": "user", "content": user},
    ]
    raw = call_llm(messages, model=llm_model)
    code = extract_python_code(raw)
    return code
