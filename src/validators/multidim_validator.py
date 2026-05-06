# -*- coding: utf-8 -*-
"""
多维验证器（流程图）：对比「原始参考图」与「修改后代码渲染图」，给出是否通过与分数。
使用 VLM 输出结构化判断。
"""
from __future__ import annotations

import json
import re
from typing import Dict, Tuple

from src.validators import (
    evaluate_color_consistency,
    evaluate_structural_consistency,
    evaluate_text_consistency,
)
from src.utils.dashscope_api import call_vlm


def _resolve_chart_policy(
    chart_type: str,
    base_threshold: float,
) -> Tuple[float, Dict[str, float]]:
    """
    按图表类型返回动态阈值与维度权重。
    维度权重键：vlm/color/text/struct
    """
    policies = {
        "line": {
            "delta": 0.03,
            "weights": {"vlm": 0.35, "color": 0.15, "text": 0.20, "struct": 0.30},
        },
        "bar": {
            "delta": 0.02,
            "weights": {"vlm": 0.35, "color": 0.20, "text": 0.20, "struct": 0.25},
        },
        "scatter": {
            "delta": 0.01,
            "weights": {"vlm": 0.35, "color": 0.20, "text": 0.15, "struct": 0.30},
        },
        "pie": {
            "delta": -0.01,
            "weights": {"vlm": 0.30, "color": 0.35, "text": 0.20, "struct": 0.15},
        },
        "radar": {
            "delta": 0.00,
            "weights": {"vlm": 0.35, "color": 0.20, "text": 0.15, "struct": 0.30},
        },
        "heatmap": {
            "delta": 0.00,
            "weights": {"vlm": 0.30, "color": 0.40, "text": 0.15, "struct": 0.15},
        },
        "unknown": {
            "delta": 0.00,
            "weights": {"vlm": 0.40, "color": 0.20, "text": 0.20, "struct": 0.20},
        },
    }
    p = policies.get(chart_type, policies["unknown"])
    dynamic_threshold = max(0.0, min(1.0, base_threshold + p["delta"]))
    return dynamic_threshold, p["weights"]


def _infer_chart_type_vlm(original_image_path: str, vlm_model: Optional[str] = None) -> str:
    """
    识别图表类型，用于动态权重与阈值。
    仅返回：line/bar/scatter/pie/radar/heatmap/unknown
    """
    system = (
        "你是图表类型识别器。"
        "根据输入图像判断类型，只能输出一个小写英文词："
        "line/bar/scatter/pie/radar/heatmap/unknown。"
        "不要输出其他内容。"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": [{"image": original_image_path}, {"text": "识别图表类型。"}]},
    ]
    try:
        raw = call_vlm(messages, model=vlm_model).strip().lower()
    except Exception:
        return "unknown"
    for t in ["line", "bar", "scatter", "pie", "radar", "heatmap", "unknown"]:
        if t in raw:
            return t
    return "unknown"


def multidimensional_validate(
    original_image_path: str,
    generated_image_path: str,
    threshold: float = 0.75,
    vlm_model: Optional[str] = None,
    chart_type: str = "auto",
    chart_report: str = "",
    code_report: str = "",
) -> Tuple[bool, float, str, dict]:
    """
    返回 (是否通过, 最终分数 0~1, 简短说明, 详细结果字典)。
    详细结果字典包含：
    {
        "final_score": float,
        "passed": bool,
        "threshold": float,
        "chart_type": str,
        "dimensions": {
            "color": float,
            "text": float,
            "structure": float,
            "vlm": float
        },
        "weights": {
            "color": float,
            "text": float,
            "structure": float,
            "vlm": float
        },
        "details": {
            "color": {...},
            "text": {...},
            "structure": {...},
            "vlm": {...}
        }
    }
    
    参数:
        chart_report: Agent2 的视觉评判报告
        code_report: Agent3 的代码评判报告
    """
    # 先做颜色维度量化评估（色块匹配 + 直方图 + HSV 距离）。
    color_result = evaluate_color_consistency(
        original_image_path,
        generated_image_path,
        resize_to=(512, 512),
        grid_size=(8, 8),
        bins_per_channel=16,
    )
    # 再做文本一致性量化评估（OCR + BLEU + 空间偏差）。
    text_result = evaluate_text_consistency(
        original_image_path,
        generated_image_path,
        ocr_lang="chi_sim+eng",
        max_bleu_n=4,
    )
    # 最后做整体结构一致性（SSIM + 空间拓扑关系）。
    struct_result = evaluate_structural_consistency(
        original_image_path,
        generated_image_path,
        resize_to=(512, 512),
        max_keypoints=12,
    )
    inferred_type = (
        _infer_chart_type_vlm(original_image_path, vlm_model)
        if chart_type == "auto"
        else chart_type.lower().strip()
    )
    dynamic_threshold, weights = _resolve_chart_policy(inferred_type, threshold)

    system = """你是图表一致性评测器。你会看到两张图：第一张为参考原图，第二张为复现图。
请评估复现图与参考图在图表类型、主要系列、趋势与整体观感上的一致程度。

**必须只输出一个 JSON 对象**（不要 Markdown 代码围栏），格式严格如下：
{"score": <0到1之间的小数>, "pass": <true或false>, "summary": "<一句话中文说明>"}

pass 的规则：若 score >= 0.75 则为 true，否则 false（除非你认为存在严重错位可将 pass 置为 false）。"""

    # 构建包含 Agent 报告的提示文本
    prompt_parts = ["第一张为参考图，第二张为复现图。请只输出 JSON。\n"]
    
    # 添加 Agent2 视觉评判报告
    if chart_report:
        prompt_parts.append("=== Agent2 视觉评判报告 ===\n")
        prompt_parts.append(f"{chart_report}\n\n")
    
    # 添加 Agent3 代码评判报告
    if code_report:
        prompt_parts.append("=== Agent3 代码评判报告 ===\n")
        prompt_parts.append(f"{code_report}\n\n")
    
    # 添加算法预计算指标
    prompt_parts.append("=== 算法预计算指标 ===\n")
    prompt_parts.append(f"- color_score={color_result.score:.4f}\n")
    prompt_parts.append(f"- global_hist_score={color_result.global_hist_score:.4f}\n")
    prompt_parts.append(f"- block_match_score={color_result.block_match_score:.4f}\n")
    prompt_parts.append(f"- hsv_score={color_result.hsv_score:.4f}\n")
    prompt_parts.append(f"- hsv_distance={color_result.hsv_distance:.4f}\n")
    prompt_parts.append(f"- text_score={text_result.score:.4f}\n")
    prompt_parts.append(f"- text_bleu={text_result.bleu_score:.4f}\n")
    prompt_parts.append(f"- text_layout_score={text_result.layout_score:.4f}\n")
    prompt_parts.append(f"- text_coverage={text_result.coverage_score:.4f}\n")
    prompt_parts.append(f"- struct_score={struct_result.score:.4f}\n")
    prompt_parts.append(f"- ssim_score={struct_result.ssim_score:.4f}\n")
    prompt_parts.append(f"- topology_score={struct_result.topology_score:.4f}\n")
    prompt_parts.append(f"- distance_consistency={struct_result.distance_consistency:.4f}\n")
    prompt_parts.append(f"- angle_consistency={struct_result.angle_consistency:.4f}\n\n")
    prompt_parts.append("请综合以上 Agent 报告和算法指标，评估视觉结构、颜色一致性、文本一致性、整体结构一致性，给出总评分。")
    
    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": [
                {"image": original_image_path},
                {"image": generated_image_path},
                {"text": "".join(prompt_parts)},
            ],
        },
    ]
    raw = call_vlm(messages, model=vlm_model).strip()
    vlm_score, _, vlm_summary = _parse_validator_json(raw, dynamic_threshold)

    # 按图表类型的自适应权重融合多维得分。
    final_score = (
        weights["vlm"] * vlm_score
        + weights["color"] * color_result.score
        + weights["text"] * text_result.score
        + weights["struct"] * struct_result.score
    )
    final_score = max(0.0, min(1.0, final_score))
    passed = final_score >= dynamic_threshold
    
    # 构建详细结果字典
    detailed_result = {
        "final_score": final_score,
        "passed": passed,
        "threshold": dynamic_threshold,
        "chart_type": inferred_type,
        "dimensions": {
            "color": color_result.score,
            "text": text_result.score,
            "structure": struct_result.score,
            "vlm": vlm_score
        },
        "weights": {
            "color": weights["color"],
            "text": weights["text"],
            "structure": weights["struct"],
            "vlm": weights["vlm"]
        },
        "details": {
            "color": {
                "score": color_result.score,
                "global_hist_score": color_result.global_hist_score,
                "block_match_score": color_result.block_match_score,
                "hsv_score": color_result.hsv_score,
                "hsv_distance": color_result.hsv_distance
            },
            "text": {
                "score": text_result.score,
                "bleu_score": text_result.bleu_score,
                "layout_score": text_result.layout_score,
                "coverage_score": text_result.coverage_score
            },
            "structure": {
                "score": struct_result.score,
                "ssim_score": struct_result.ssim_score,
                "topology_score": struct_result.topology_score,
                "distance_consistency": struct_result.distance_consistency,
                "angle_consistency": struct_result.angle_consistency
            },
            "vlm": {
                "score": vlm_score,
                "summary": vlm_summary
            }
        }
    }
    
    # 生成人类可读的摘要
    summary = (
        f"type={inferred_type}, thr={dynamic_threshold:.3f}, "
        f"w(vlm={weights['vlm']:.2f},color={weights['color']:.2f},"
        f"text={weights['text']:.2f},struct={weights['struct']:.2f}) | "
        f"{vlm_summary} | "
        f"color={color_result.score:.3f}(global={color_result.global_hist_score:.3f},"
        f" block={color_result.block_match_score:.3f}, hsv={color_result.hsv_score:.3f}) | "
        f"text={text_result.score:.3f}(bleu={text_result.bleu_score:.3f},"
        f" layout={text_result.layout_score:.3f}, cov={text_result.coverage_score:.3f}) | "
        f"struct={struct_result.score:.3f}(ssim={struct_result.ssim_score:.3f},"
        f" topo={struct_result.topology_score:.3f}, dist={struct_result.distance_consistency:.3f},"
        f" ang={struct_result.angle_consistency:.3f}) | "
        f"final={final_score:.3f}"
    )
    
    return passed, final_score, summary, detailed_result


def _parse_validator_json(raw: str, threshold: float) -> Tuple[float, bool, str]:
    """容错解析 JSON。"""
    raw = raw.strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        raw = m.group(0)
    try:
        obj = json.loads(raw)
        score = float(obj.get("score", 0.0))
        score = max(0.0, min(1.0, score))
        summary = str(obj.get("summary", ""))
        passed = bool(obj.get("pass", score >= threshold))
        return score, passed, summary
    except (json.JSONDecodeError, TypeError, ValueError):
        # 回退：尝试提取数字
        nums = re.findall(r"0?\.\d+|1\.0*|0|1", raw[:200])
        score = float(nums[0]) if nums else 0.0
        passed = score >= threshold
        return score, passed, raw[:500]
