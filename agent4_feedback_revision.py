# -*- coding: utf-8 -*-
"""
Agent 4 — 修订评判 / 反馈优化（流程图 + 图五）
输入：当前 ECharts 代码 + Agent3 的代码评估报告 + Agent2 的图表评估报告
输出：综合两份报告后的**完整修改后 JavaScript**（仍须满足 div#main、全局 echarts、无 import/export）
模型：LLM
"""
from __future__ import annotations

from dashscope_api import call_llm, extract_javascript_code, strip_esm_imports

SYSTEM_AGENT4 = """你是 ECharts 专家。你会收到：
1. 当前的 ECharts 内联 JavaScript；
2. 「代码评估报告」；
3. 「图表评估报告」。

请根据两份报告中的**可执行建议**，输出**一份完整、可直接替换**的修改后 JavaScript，
使图表更贴近原始参考图、并改善代码质量。

硬性要求：
- 仅使用全局 echarts，禁止 import/export。
- 使用 document.getElementById('main') 与 echarts.init。
- 输出只能是 JavaScript 代码，不要 Markdown 说明。"""


def agent4_feedback_optimize_code(
    echarts_inline_js: str,
    code_evaluation_report: str,
    chart_evaluation_report: str,
    llm_model: str = "qwen-plus",
) -> str:
    user = (
        "【代码评估报告】\n"
        f"{code_evaluation_report}\n\n"
        "【图表评估报告】\n"
        f"{chart_evaluation_report}\n\n"
        "【当前代码】\n"
        f"```javascript\n{echarts_inline_js}\n```\n\n"
        "请输出修改后的完整 JavaScript。"
    )
    messages = [
        {"role": "system", "content": SYSTEM_AGENT4},
        {"role": "user", "content": user},
    ]
    raw = call_llm(messages, model=llm_model)
    code = extract_javascript_code(raw)
    return strip_esm_imports(code)
