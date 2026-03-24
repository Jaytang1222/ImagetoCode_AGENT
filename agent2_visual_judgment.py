# -*- coding: utf-8 -*-
"""
Agent 2 — 视觉评判（流程图 + 图三风格）
输入：两张图片路径（原始参考图、根据代码生成的复现图）
输出：图像评判 / 图表评估报告（对比差异、趋势与指标解读）
模型：VLM
"""
from __future__ import annotations

from dashscope_api import call_vlm

SYSTEM_AGENT2 = """你是严谨的图表视觉评测专家。
你会收到两张图片：第一张为「原始参考图」，第二张为「根据代码渲染的复现图」。

请输出一份结构化的「图表评估报告」**，至少包含**：
1. 整体相似度（主观描述即可）。
2. 图表类型、坐标轴、图例、配色是否一致或存在差异。
3. 数据趋势或柱状/折线相对关系是否一致（若可辨认）。
4. 若图中涉及不同算法/系列（如 A/B/C/D），请对比其相对表现（如延迟、开销等），使用简短英文或中文要点均可。
5. 给出可操作的改进建议，便于后续修改绘图代码。

使用简洁的小标题与列表，便于下游 Agent 解析。"""


def agent2_chart_evaluation_report(
    original_image_path: str,
    generated_image_path: str,
    vlm_model: str = "qwen3.5-plus",
) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_AGENT2},
        {
            "role": "user",
            "content": [
                {"image": original_image_path},
                {"image": generated_image_path},
                {"text": "第一张为原始参考图，第二张为复现图。请按系统说明输出图表评估报告。"},
            ],
        },
    ]
    return call_vlm(messages, model=vlm_model)
