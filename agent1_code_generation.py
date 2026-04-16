# -*- coding: utf-8 -*-
"""
Agent 1 — 代码生成（图二）
输入：参考图表图片（路径）
输出：ECharts 用 JS（浏览器内联，div#main，全局 echarts）
模型：VLM（qwen-vl-max）
"""
from __future__ import annotations

from typing import Optional

from dashscope_api import call_vlm, extract_javascript_code, strip_esm_imports

SYSTEM_AGENT1 = """你是数据可视化与 ECharts 专家。
用户会提供一张统计图表截图。你的任务是输出**一段可直接在浏览器中执行的 JavaScript**，
用 ECharts 尽可能复现该图（类型、系列、颜色趋势、图例与坐标轴大致一致）。

硬性要求（必须遵守）：
1. 页面已通过 CDN 引入全局变量 echarts，禁止使用 import / export。
2. 使用 document.getElementById('main') 获取容器，echarts.init(chartDom) 初始化。
3. 使用 myChart.setOption(option) 传入完整 option。
4. 只输出 JavaScript 代码本身；如需注释使用 // 或 /* */，不要用 Markdown。
5. 若图中文字为中文，请在 option 中保留中文标题/图例等。"""


def agent1_generate_code(
    input_chart_image_path: str,
    extra_feedback: Optional[str] = None,
    vlm_model: str = "qwen3.5-plus",
) -> str:
    """
    根据输入图表生成 ECharts 内联 JS。
    extra_feedback: 上一轮验证/评判失败时的补充说明，可注入到首轮之后的重试（由主流程传入）。
    """
    user_text = (
        "请阅读附图中的图表，并输出满足上述要求的完整 JavaScript 代码。"
    )
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
    code = extract_javascript_code(raw)
    code = strip_esm_imports(code)
    return code
