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
import json

logger = logging.getLogger(__name__)


def validate_agent2_output(report: str) -> bool:
    """
    验证 Agent2 输出是否符合预期格式。
    检查必需的结构化部分是否存在（兼容新格式）。
    """
    required_sections = [
        "COLOR_SIMILARITY",
        "AXIS_TICK_ACCURACY", 
        "TEXT_CONSISTENCY",
        "GEOMETRY_TREND_CONSISTENCY",
        "OVERALL_ASSESSMENT"
    ]
    
    # 检查所有必需部分是否存在（宽松匹配，兼容新旧格式）
    missing_sections = [s for s in required_sections if s not in report]
    
    if missing_sections:
        logger.warning(f"Agent2 输出格式不完全符合预期，缺少部分: {missing_sections}")
        return False
    
    # 检查是否有评分（兼容新格式 SCORE: 85/100）
    score_pattern = r"(?:SCORE|Score|评分)[:：]\s*(\d+)"
    scores = re.findall(score_pattern, report, re.IGNORECASE)
    
    if len(scores) < 4:
        logger.warning(f"Agent2 输出缺少足够的评分，期望至少4个，实际{len(scores)}个")
        return False
    
    return True


def validate_agent3_output(report: str) -> bool:
    """
    验证 Agent3 输出是否符合预期格式。
    检查必需的结构化部分是否存在（兼容新格式）。
    """
    # 关键部分的核心关键词（宽松匹配）
    required_keywords = [
        "DIFF-TO-CODE MAPPING",  # 或 PART 1: DIFF-TO-CODE MAPPING
        "PRIORITIZED FIX INSTRUCTIONS",  # 或 PART 3: PRIORITIZED FIX INSTRUCTIONS
        "MUST-KEEP ELEMENTS",  # 或 PART 4: MUST-KEEP ELEMENTS
        "AGENT4_INPUT"  # 或 STRUCTURED_AGENT4_INPUT
    ]
    
    # 检查所有必需部分是否存在（宽松匹配）
    missing_sections = []
    for keyword in required_keywords:
        # 提取核心关键词进行匹配
        core_keyword = keyword.replace("DIFF-TO-CODE ", "").replace("PRIORITIZED FIX ", "").replace("MUST-KEEP ", "")
        
        # 检查是否包含核心关键词
        if keyword not in report and core_keyword not in report:
            # 特殊处理：AGENT4_INPUT 可能是 STRUCTURED_AGENT4_INPUT
            if "AGENT4_INPUT" in keyword and "STRUCTURED_AGENT4_INPUT" not in report:
                missing_sections.append(keyword)
            elif "AGENT4_INPUT" not in keyword:
                missing_sections.append(keyword)
    
    if missing_sections:
        logger.warning(f"Agent3 输出格式不完全符合预期，缺少部分: {missing_sections}")
        return False
    
    return True


def run_full_pipeline(
    input_chart_image: str,
    out_dir: str = "outputs",
    max_loops: int = 5,
    threshold: float = 0.75,
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

        if loop == 0:
            print("[Agent1] 代码生成（VLM）…")
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

        print("[多维验证器] 对比原图与复现图…")
        ok, score, last_summary, detailed_result = multidimensional_validate(
            input_chart_image, 
            png_final, 
            threshold=threshold,
            chart_report=chart_report,
            code_report=code_report,
        )
        print(f"  → score={score:.4f} pass={ok} | {last_summary}")

        # 保存结构化的验证结果
        validator_output = {
            "pass": ok,
            "final_score": score,
            "round": loop + 1,
            "summary": last_summary,
            "detailed_result": detailed_result
        }
        
        # 保存 JSON 格式
        Path(os.path.join(out_dir, f"validator_round{loop+1}.json")).write_text(
            json.dumps(validator_output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        
        # 同时保存文本格式以便人类阅读
        Path(os.path.join(out_dir, f"validator_round{loop+1}.txt")).write_text(
            f"pass={ok}\nfinal_score={score}\n{last_summary}",
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
