# -*- coding: utf-8 -*-
"""
完整 Agent 流程（图一）：Agent1 → Agent2 → Agent3 → Agent4 → 多维验证器 → 未通过则迭代。
首轮由 Agent1 根据输入图生成代码；之后每轮在上一版 Agent4 输出上继续优化。

性能优化（v3.0）：
  - 优先 D：渲染图哈希缓存 —— 图片不变则跳过 Agent2/Agent3
  - 优先 E：Agent2 高分早期退出 —— overall ≥ 95 直接通过
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

from src.agents.agent1_code_generation import agent1_generate_code_with_render
from src.agents.agent2_visual_judgment import agent2_chart_evaluation_report
from src.agents.agent3_code_evaluation import agent3_code_evaluation_report
from src.agents.agent4_feedback_revision import agent4_feedback_optimize_code
from src.utils.matplotlib_render import render_matplotlib_code_to_png
from src.validators.multidim_validator import multidimensional_validate

logger = logging.getLogger(__name__)

# Agent2 高分阈值：超过此值直接判定通过，跳过 Agent3/Agent4/验证器
_AGENT2_HIGH_SCORE_THRESHOLD = 95


def _parse_agent2_overall_score(report: str) -> float:
    """从 Agent2 报告中提取"总体评分"（0-100）。"""
    for line in report.splitlines():
        m = re.search(r"总体评分[：:]\s*(\d+)", line)
        if m:
            return float(m.group(1))
    m = re.search(r"总体评分[：:][^\d]*(\d+)", report)
    if m:
        return float(m.group(1))
    return 0.0


def _png_hash(png_path: str) -> str:
    """计算 PNG 文件的 MD5 哈希（用于变更检测）。"""
    with open(png_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def validate_agent2_output(report: str) -> bool:
    """验证 Agent2 输出是否包含必需的章节。"""
    required = [
        "COLOR_SIMILARITY",
        "AXIS_TICK_ACCURACY",
        "TEXT_CONSISTENCY",
        "GEOMETRY_TREND_CONSISTENCY",
        "OVERALL_ASSESSMENT",
    ]
    missing = [s for s in required if s not in report]
    if missing:
        logger.warning(f"Agent2 输出缺少部分: {missing}")
        return False
    scores = re.findall(r"(?:SCORE|Score|评分)[:：]\s*(\d+)", report, re.IGNORECASE)
    if len(scores) < 4:
        logger.warning(f"Agent2 输出评分不足，期望≥4，实际{len(scores)}")
        return False
    return True


def validate_agent3_output(report: str) -> bool:
    """验证 Agent3 输出是否包含必需的章节。"""
    kw_list = ["DIFF-TO-CODE", "PRIORITIZED FIX", "MUST-KEEP", "AGENT4_INPUT"]
    missing = [kw for kw in kw_list if kw not in report]
    if missing:
        logger.warning(f"Agent3 输出缺少部分: {missing}")
        return False
    return True


def run_full_pipeline(
    input_chart_image: str,
    out_dir: str = "outputs",
    max_loops: int = 5,
    threshold: float = 0.75,
    vlm_model: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[str], str]:
    """
    运行完整的多智能体流水线。

    返回:
        (是否验证通过, 最终代码路径, 最终渲染 PNG 路径, 最后一轮说明摘要)
    """
    os.makedirs(out_dir, exist_ok=True)
    code_path = os.path.join(out_dir, "current_matplotlib.py")
    gen_png = os.path.join(out_dir, "generated_chart.png")

    last_summary = ""
    code: str = ""
    prev_png_hash: Optional[str] = None
    chart_report: str = ""
    code_report: str = ""
    png_cached: bool = False

    for loop in range(max_loops):
        print(f"\n{'='*20} 第 {loop + 1}/{max_loops} 轮 {'='*20}")

        # ────────────────────────────────────────────────────────────────
        # 阶段 1：代码生成（仅首轮）或复用上一轮 Agent4 输出
        # ────────────────────────────────────────────────────────────────
        if loop == 0:
            print("[Agent1] 代码生成（VLM）…")
            code, _ = agent1_generate_code_with_render(
                input_chart_image_path=input_chart_image,
                out_dir=out_dir,
                vlm_model=vlm_model,
            )
        else:
            print("[迭代] 在上一轮 Agent4 输出上继续优化…")

        Path(code_path).write_text(code, encoding="utf-8")

        # step1 渲染
        print(f"[渲染] 执行 Matplotlib 代码生成截图 → {gen_png}")
        png, error = render_matplotlib_code_to_png(code, gen_png)
        if not png:
            msg = f"无法生成复现图 PNG。错误: {error}"
            print("[错误]", msg)
            return False, code_path, None, msg

        # ────────────────────────────────────────────────────────────────
        # 优先 D：检测 PNG 是否与上一轮相同，相同则跳过 Agent2
        # ────────────────────────────────────────────────────────────────
        cur_hash = _png_hash(png)
        png_cached = (
            prev_png_hash is not None and cur_hash == prev_png_hash and loop > 0
        )
        if png_cached:
            print("[缓存] PNG 与上一轮一致，复用 Agent2 报告")
            chart_report = Path(
                os.path.join(out_dir, f"report_agent2_round{loop}.txt")
            ).read_text(encoding="utf-8")
        else:
            prev_png_hash = cur_hash

            # ────────────────────────────────────────────────────────────
            # 阶段 2：Agent2 视觉评估（VLM）
            # ────────────────────────────────────────────────────────────
            print("[Agent2] 视觉评估（VLM）…")
            chart_report = agent2_chart_evaluation_report(
                input_chart_image, png,
                **(dict(vlm_model=vlm_model) if vlm_model else {}),
            )
            validate_agent2_output(chart_report)

        # ────────────────────────────────────────────────────────────────
        # 优先 E：Agent2 高分早期退出
        # ────────────────────────────────────────────────────────────────
        overall = _parse_agent2_overall_score(chart_report)
        if overall >= _AGENT2_HIGH_SCORE_THRESHOLD and loop == 0:
            print(
                f"[早期退出] Agent2 总体评分 {overall} ≥ "
                f"{_AGENT2_HIGH_SCORE_THRESHOLD}，直接判定通过，"
                f"跳过 Agent3/Agent4/验证器"
            )
            return True, code_path, png, f"EarlyPass: Agent2 overall={overall}/100"

        # 保存 Agent2 报告
        Path(os.path.join(out_dir, f"report_agent2_round{loop+1}.txt")).write_text(
            chart_report, encoding="utf-8"
        )

        # ────────────────────────────────────────────────────────────────
        # 阶段 3：Agent3 代码评判 —— 基于本轮 Agent2 报告
        # ────────────────────────────────────────────────────────────────
        if png_cached and loop > 0:
            print("[Agent3] PNG 未变，复用上一轮代码评判报告")
            code_report = Path(
                os.path.join(out_dir, f"report_agent3_round{loop}.txt")
            ).read_text(encoding="utf-8")
        else:
            print("[Agent3] 代码评判（LLM）…")
            code_report = agent3_code_evaluation_report(
                code, chart_report,
                **(dict(llm_model=llm_model) if llm_model else {}),
            )
        validate_agent3_output(code_report)

        Path(os.path.join(out_dir, f"report_agent3_round{loop+1}.txt")).write_text(
            code_report, encoding="utf-8"
        )

        # ────────────────────────────────────────────────────────────────
        # 阶段 4：Agent4 反馈修订
        # ────────────────────────────────────────────────────────────────
        print("[Agent4] 反馈优化修订（LLM）…")
        code_new = agent4_feedback_optimize_code(
            code, code_report, chart_report,
            **(dict(llm_model=llm_model) if llm_model else {}),
        )
        Path(
            os.path.join(out_dir, f"current_matplotlib_after_agent4_r{loop+1}.py")
        ).write_text(code_new, encoding="utf-8")

        # ────────────────────────────────────────────────────────────────
        # 阶段 5：验证
        # ────────────────────────────────────────────────────────────────
        print("[渲染] Agent4 输出再截图…")
        png_final, error = render_matplotlib_code_to_png(code_new, gen_png)
        if not png_final:
            return False, code_path, None, f"Agent4 后截图失败: {error}"

        print("[多维验证器] 对比原图与复现图…")
        ok, score, last_summary, detailed_result = multidimensional_validate(
            input_chart_image,
            png_final,
            threshold=threshold,
            chart_report=chart_report,
            code_report=code_report,
        )
        print(f"  → score={score:.4f} pass={ok} | {last_summary}")

        # 保存验证结果
        Path(os.path.join(out_dir, f"validator_round{loop+1}.json")).write_text(
            json.dumps(
                {
                    "pass": ok,
                    "final_score": score,
                    "round": loop + 1,
                    "summary": last_summary,
                    "detailed_result": detailed_result,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
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