# -*- coding: utf-8 -*-
"""ECharts 专用 Agent 流水线"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple

from Agents.agent1_code_generation import agent1_generate_code, extract_javascript_code
from Agents.agent2_visual_judgment import agent2_chart_evaluation_report
from Agents.agent3_code_evaluation import agent3_code_evaluation_report
from Agents.agent4_feedback_revision import agent4_feedback_optimize_code
from utils.echarts_render import render_echarts_sync  # 新增
from Authenticator.multidim_validator import multidimensional_validate


def run_echarts_pipeline(
    input_chart_image: str,
    out_dir: str = "outputs",
    max_loops: int = 5,
    threshold: float = 0.75,
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    ECharts 专用流水线。

    返回 (是否验证通过，最终 JS 代码路径，最终渲染 PNG 路径，说明摘要)
    """
    os.makedirs(out_dir, exist_ok=True)
    code_path = os.path.join(out_dir, "current_echarts.js")
    gen_png = os.path.join(out_dir, "generated_chart.png")

    last_summary = ""
    code: Optional[str] = None

    for loop in range(max_loops):
        print(f"\n{'='*20} 第 {loop + 1}/{max_loops} 轮 {'='*20}")

        if loop == 0:
            print("[Agent1] ECharts 代码生成（VLM）…")
            code = agent1_generate_code(
                input_chart_image_path=input_chart_image,
                output_format="echarts",
                extra_feedback=None,
            )
        else:
            print("[迭代] 在上一轮 Agent4 输出上继续优化…")

        # 保存代码
        Path(code_path).write_text(code, encoding="utf-8")

        # 渲染 ECharts 代码
        print(f"[渲染] 执行 ECharts 代码生成截图 → {gen_png}")
        png, error = render_echarts_sync(code, gen_png)
        if not png:
            msg = f"无法生成复现图 PNG。错误：{error}"
            print("[错误]", msg)
            last_summary = msg
            return False, code_path, None, last_summary

        # Agent2 视觉评估
        print("[Agent2] 视觉评判（双图 VLM）…")
        chart_report = agent2_chart_evaluation_report(input_chart_image, png)
        Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
            chart_report, encoding="utf-8"
        )

        # Agent3 代码评估
        print("[Agent3] 代码评判（LLM）…")
        code_report = agent3_code_evaluation_report(code, chart_report)
        Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
            code_report, encoding="utf-8"
        )

        # Agent4 反馈修订
        print("[Agent4] 反馈优化修订（LLM）…")
        code_new = agent4_feedback_optimize_code(code, code_report, chart_report)
        Path(
            os.path.join(out_dir, f"current_echarts_after_agent4_r{loop+1}.js")
        ).write_text(code_new, encoding="utf-8")

        # 再次渲染验证
        print("[渲染] Agent4 输出再截图…")
        png_final, error = render_echarts_sync(code_new, gen_png)
        if not png_final:
            last_summary = f"Agent4 后截图失败：{error}"
            return False, code_path, None, last_summary

        # 多维验证
        print("[多维验证器] 对比原图与复现图…")
        ok, score, last_summary = multidimensional_validate(
            input_chart_image, png_final, threshold=threshold
        )
        print(f"  → score={score:.4f} pass={ok} | {last_summary}")

        Path(os.path.join(out_dir, f"validator_round{loop+1}.txt")).write_text(
            f"pass={ok}\nscore={score}\n{last_summary}",
            encoding="utf-8",
        )

        if ok:
            Path(code_path).write_text(code_new, encoding="utf-8")
            print("[完成] 验证通过，最终代码已写入:", code_path)
            return True, code_path, png_final, last_summary

        code = code_new

    print("[结束] 未能在限定轮数内通过验证，返回最后一版 Agent4 代码。")
    Path(code_path).write_text(code, encoding="utf-8")
    return False, code_path, gen_png, last_summary