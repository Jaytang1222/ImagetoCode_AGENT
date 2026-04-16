# -*- coding: utf-8 -*-
"""
完整 Agent 流程（图一）：Agent1 → Agent2 → Agent3 → Agent4 → 多维验证器 → 未通过则迭代。
首轮由 Agent1 根据输入图生成代码；之后每轮在上一版 Agent4 输出上继续优化。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple

from Agents.agent1_code_generation import Agent1Preset, agent1_generate_and_dispatch
from Agents.agent2_visual_judgment import agent2_chart_evaluation_report
from Agents.agent3_code_evaluation import agent3_code_evaluation_report
from Agents.agent4_feedback_revision import agent4_feedback_optimize_code
from utils.matplotlib_render import render_matplotlib_code_to_png
from Authenticator.multidim_validator import multidimensional_validate


def run_full_pipeline(
    input_chart_image: str,
    out_dir: str = "outputs",
    max_loops: int = 5,
    threshold: float = 0.75,
    strict_algorithm_mode: bool = True,
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    返回 (是否验证通过, 最终 JS 代码路径, 最终渲染 PNG 路径, 最后一轮说明摘要)。
    """
    os.makedirs(out_dir, exist_ok=True)
    code_path = os.path.join(out_dir, "current_matplotlib.py")
    gen_png = os.path.join(out_dir, "generated_chart.png")

    last_summary = ""
    code: Optional[str] = None

    for loop in range(max_loops):
        print(f"\n{'='*20} 第 {loop + 1}/{max_loops} 轮 {'='*20}")

        if strict_algorithm_mode:
            print("[Agent1] 代码生成 + 分发评审（严格流程）…")
            agent1_result = agent1_generate_and_dispatch(
                input_chart_image_path=input_chart_image,
                preset=Agent1Preset(out_dir=out_dir),
                extra_feedback=None,
            )
            code = agent1_result.generated_code
            chart_report = agent1_result.chart_report or ""
            code_report = agent1_result.code_report or ""
            code_new = agent1_result.optimized_code or code
            if not code or not chart_report or not code_report:
                last_summary = "严格模式下 Agent1 分发结果不完整"
                return False, code_path, None, last_summary
            Path(code_path).write_text(code, encoding="utf-8")
            Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                chart_report, encoding="utf-8"
            )
            Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                code_report, encoding="utf-8"
            )
            Path(
                os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
            ).write_text(code_new, encoding="utf-8")
        else:
            if loop == 0:
                print("[Agent1] 代码生成（VLM）…")
                # 兼容旧流程：仅首轮 Agent1，后续沿用 Agent4 输出迭代。
                agent1_result = agent1_generate_and_dispatch(
                    input_chart_image_path=input_chart_image,
                    preset=Agent1Preset(out_dir=out_dir, dispatch_to_agents=False),
                    extra_feedback=None,
                )
                code = agent1_result.generated_code
            else:
                print("[迭代] 在上一轮 Agent4 输出上继续优化…")

            Path(code_path).write_text(code, encoding="utf-8")
            print(f"[渲染] 执行 Matplotlib 代码生成截图 → {gen_png}")
            png, error = render_matplotlib_code_to_png(code, gen_png)
            if not png:
                msg = f"无法生成复现图 PNG。错误: {error}"
                print("[错误]", msg)
                last_summary = msg
                return False, code_path, None, last_summary

            print("[Agent2] 视觉评判（双图 VLM）…")
            chart_report = agent2_chart_evaluation_report(input_chart_image, png)
            Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                chart_report, encoding="utf-8"
            )

            print("[Agent3] 代码评判（LLM）…")
            code_report = agent3_code_evaluation_report(code, chart_report)
            Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                code_report, encoding="utf-8"
            )

            print("[Agent4] 反馈优化修订（LLM）…")
            code_new = agent4_feedback_optimize_code(code, code_report, chart_report)
            Path(
                os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
            ).write_text(code_new, encoding="utf-8")

        print("[渲染] Agent4 输出再截图…")
        png_final, error = render_matplotlib_code_to_png(code_new, gen_png)
        if not png_final:
            last_summary = f"Agent4 后截图失败: {error}"
            return False, code_path, None, last_summary

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
