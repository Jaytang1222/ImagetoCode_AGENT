# -*- coding: utf-8 -*-
"""
Agent 2 — 视觉评判（流程图 + 图三风格）
输入：两张图片路径（原始参考图、根据 Matplotlib 代码生成的复现图）
输出：图像评判 / 图表评估报告（对比差异、趋势与指标解读）
模型：VLM
"""
from __future__ import annotations

from utils.dashscope_api import call_vlm

SYSTEM_AGENT2 = """你是严谨的图表视觉评测专家。
你会收到两张图片：第一张为「原始参考图（即代码生成智能体 Agent1 的输入图）」，
第二张为「根据 Matplotlib Python 代码渲染的复现图」。

请基于这两张图输出结构化「视觉差异评估报告」，并确保该报告可直接作为
代码评估智能体（Agent3）与修订优化智能体（Agent4）的输入。

输出必须包含以下维度（每项都要给出"结论 + 证据 + 改进建议"）：
1. 颜色相似度（Color Similarity）
   - 比较背景色、主色调、系列颜色、图例颜色映射是否一致。
   - 给出 0~100 分的相似度评分。
   - 改进建议应具体到 Matplotlib 参数（如 color='#1f77b4'）。
2. 坐标轴精度与刻度匹配度（Axis & Tick Accuracy）
   - 比较 x/y 轴范围、刻度间隔、刻度数量、标签格式（如百分比/小数位）是否匹配。
   - 给出 0~100 分的匹配度评分。
   - 改进建议应具体到函数调用（如 plt.xticks(range(0, 11, 2))）。
3. 文本一致性（Text Consistency）
   - 比较标题、副标题、坐标轴名称、图例文本、数据标签文本是否一致。
   - 给出 0~100 分的一致性评分。
   - 改进建议应具体到函数调用（如 plt.title('标题')）。
4. 图形结构与趋势一致性（Geometry & Trend Consistency）
   - 比较图表类型、系列数量、线条/柱形相对位置、峰谷趋势与排序关系是否一致。
   - 给出 0~100 分的一致性评分。
   - 改进建议应具体到绘图函数（如 plt.plot() 的 linestyle、marker 参数）。

最后必须输出：
- OverallScore（0~100）
- TopIssues（最多 5 条，按严重程度排序）
- ActionableFixes（可直接指导 Matplotlib 代码修改的要点列表，面向 Agent3/Agent4）

要求：语言简洁、条目清晰、避免空泛描述。改进建议应具体到 Matplotlib 函数和参数级别。"""


def agent2_chart_evaluation_report(
    original_image_path: str,
    generated_image_path: str,
    vlm_model: str = "qwen3.6-plus",
) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_AGENT2},
        {
            "role": "user",
            "content": [
                {"image": original_image_path},
                {"image": generated_image_path},
                {
                    "text": (
                        "第一张为 Agent1 的输入原图，第二张为复现图。"
                        "请严格按系统要求输出视觉差异评估报告，"
                        "报告将直接提供给 Agent3 与 Agent4。"
                    )
                },
            ],
        },
    ]
    return call_vlm(messages, model=vlm_model)
