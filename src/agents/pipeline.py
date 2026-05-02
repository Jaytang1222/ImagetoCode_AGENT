# -*- coding: utf-8 -*-
"""
完整 Agent 流程（图一）：Agent1 → Agent2 → Agent3 → Agent4 → 多维验证器 → 未通过则迭代。
首轮由 Agent1 根据输入图生成代码；之后每轮在上一版 Agent4 输出上继续优化。
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional, Tuple
import logging

from src.agents.agent1_code_generation import Agent1Preset, agent1_generate_and_dispatch
from src.agents.agent2_visual_judgment import agent2_chart_evaluation_report
from src.agents.agent3_code_evaluation import agent3_code_evaluation_report
from src.agents.agent4_feedback_revision import agent4_feedback_optimize_code
from src.utils.matplotlib_render import render_matplotlib_code_to_png
from src.validators.multidim_validator import multidimensional_validate

logger = logging.getLogger(__name__)


def validate_agent2_output(report: str) -> bool:
    """
    验证 Agent2 输出是否符合预期格式。
    检查必需的结构化部分是否存在。
    """
    required_sections = [
        "COLOR_SIMILARITY",
        "AXIS_TICK_ACCURACY", 
        "TEXT_CONSISTENCY",
        "GEOMETRY_TREND_CONSISTENCY",
        "OVERALL_ASSESSMENT"
    ]
    
    # 检查所有必需部分是否存在
    missing_sections = [s for s in required_sections if s not in report]
    
    if missing_sections:
        logger.warning(f"Agent2 输出格式不完全符合预期，缺少部分: {missing_sections}")
        return False
    
    # 检查是否有评分
    score_pattern = r"(?:Score|评分)[:：]\s*(\d+)"
    scores = re.findall(score_pattern, report, re.IGNORECASE)
    
    if len(scores) < 4:
        logger.warning(f"Agent2 输出缺少足够的评分，期望4个，实际{len(scores)}个")
        return False
    
    return True


def validate_agent3_output(report: str) -> bool:
    """
    验证 Agent3 输出是否符合预期格式。
    检查必需的结构化部分是否存在。
    """
    required_sections = [
        "DIFF-TO-CODE MAPPING",
        "PRIORITIZED FIX INSTRUCTIONS",
        "MUST-KEEP ELEMENTS",
        "AGENT4_INPUT"
    ]
    
    # 检查所有必需部分是否存在（支持中英文）
    missing_sections = []
    for section in required_sections:
        # 支持中文版本的部分名称
        if section not in report and not any([
            "差异-根因映射" in report and "MAPPING" in section,
            "优先级修复指令" in report and "PRIORITIZED" in section,
            "必须保留" in report and "MUST-KEEP" in section,
            "AGENT4_INPUT" in report
        ]):
            missing_sections.append(section)
    
    if missing_sections:
        logger.warning(f"Agent3 输出格式不完全符合预期，缺少部分: {missing_sections}")
        return False
    
    return True


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
            initial_chart_report = agent1_result.chart_report or ""
            initial_code_report = agent1_result.code_report or ""
            code_new = agent1_result.optimized_code or code
            if not code or not initial_chart_report or not initial_code_report:
                last_summary = "严格模式下 Agent1 分发结果不完整"
                return False, code_path, None, last_summary
            Path(code_path).write_text(code, encoding="utf-8")
            Path(os.path.join(out_dir, f"report_agent2_initial_round{loop+1}.txt")).write_text(
                initial_chart_report, encoding="utf-8"
            )
            Path(os.path.join(out_dir, f"report_agent3_initial_round{loop+1}.txt")).write_text(
                initial_code_report, encoding="utf-8"
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
            
            # 验证 Agent2 输出格式
            if not validate_agent2_output(chart_report):
                logger.warning("Agent2 输出格式验证失败，但仍作为文本继续处理")
            
            Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
                chart_report, encoding="utf-8"
            )

            print("[Agent3] 代码评判（LLM）…")
            code_report = agent3_code_evaluation_report(code, chart_report)
            
            # 验证 Agent3 输出格式
            if not validate_agent3_output(code_report):
                logger.warning("Agent3 输出格式验证失败，但仍作为文本继续处理")
            
            Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
                code_report, encoding="utf-8"
            )

            print("[Agent4] 反馈优化修订（LLM）…")
            code_new = agent4_feedback_optimize_code(code, code_report, chart_report)
            Path(
                os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
            ).write_text(code_new, encoding="utf-8")

        # 渲染 Agent4 优化后的代码
        print("[渲染] Agent4 输出再截图…")
        png_final, error = render_matplotlib_code_to_png(code_new, gen_png)
        if not png_final:
            last_summary = f"Agent4 后截图失败: {error}"
            return False, code_path, None, last_summary

        # 针对 Agent4 优化后的代码重新生成评判报告（用于验证器）
        print("[Agent2] 对 Agent4 优化后的图进行视觉评判…")
        chart_report_final = agent2_chart_evaluation_report(input_chart_image, png_final)
        
        # 验证 Agent2 输出格式
        if not validate_agent2_output(chart_report_final):
            logger.warning("Agent2 最终输出格式验证失败，但仍作为文本继续处理")
        
        Path(os.path.join(out_dir, f"report_agent2_final_round{loop+1}.txt")).write_text(
            chart_report_final, encoding="utf-8"
        )

        print("[Agent3] 对 Agent4 优化后的代码进行评判…")
        code_report_final = agent3_code_evaluation_report(code_new, chart_report_final)
        
        # 验证 Agent3 输出格式
        if not validate_agent3_output(code_report_final):
            logger.warning("Agent3 最终输出格式验证失败，但仍作为文本继续处理")
        
        Path(os.path.join(out_dir, f"report_agent3_final_round{loop+1}.txt")).write_text(
            code_report_final, encoding="utf-8"
        )

        print("[多维验证器] 对比原图与复现图…")
        ok, score, last_summary = multidimensional_validate(
            input_chart_image, 
            png_final, 
            threshold=threshold,
            chart_report=chart_report_final,
            code_report=code_report_final,
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
