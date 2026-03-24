# -*- coding: utf-8 -*-
"""
Agent 3 — 代码评判 / 改进指导（流程图 + 图四）
输入：当前 ECharts 内联 JS + Agent2 的图表评估报告
输出：代码评判报告（可读性、模块化、可测试性等）+ 与视觉差异一致的代码改进建议
模型：LLM
"""
from __future__ import annotations

from dashscope_api import call_llm

SYSTEM_AGENT3 = """你是资深前端与数据可视化工程师，负责审查 ECharts 绘图代码。

请结合「图表评估报告」中的视觉差异，对下方 JavaScript 代码给出**代码评判报告**，必须包含：
- **可读性**：如命名、注释、结构是否清晰。
- **模块化**：数据与配置是否分离、是否便于维护。
- **可测试性**：是否便于抽取数据或做单元测试（可简要说明）。
- **与视觉报告的一致性**：指出代码层面可能导致的差异，并给出**具体的代码改进指导**（条目化）。

输出使用中文，条理清晰，便于下游 Agent 直接据此修改代码。"""


def agent3_code_evaluation_report(
    echarts_inline_js: str,
    chart_evaluation_report: str,
    llm_model: str = "qwen-plus",
) -> str:
    user = (
        "【图表评估报告（来自视觉 Agent）】\n"
        f"{chart_evaluation_report}\n\n"
        "【待评判的 ECharts 内联 JavaScript】\n"
        f"```javascript\n{echarts_inline_js}\n```\n\n"
        "请输出代码评判报告（含上述各维度）。"
    )
    messages = [
        {"role": "system", "content": SYSTEM_AGENT3},
        {"role": "user", "content": user},
    ]
    return call_llm(messages, model=llm_model)
