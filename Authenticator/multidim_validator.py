# -*- coding: utf-8 -*-
"""
多维验证器（流程图）：对比「原始参考图」与「修改后代码渲染图」，给出是否通过与分数。
使用 VLM 输出结构化判断。
"""
from __future__ import annotations

import json
import re
from typing import Dict, Tuple

from Authenticator import (
    evaluate_color_consistency,
    evaluate_structural_consistency,
    evaluate_text_consistency,
)
from utils.dashscope_api import call_vlm


def _resolve_chart_policy(
    chart_type: str,
    base_threshold: float,
) -> Tuple[float, Dict[str, float]]:
    """
    按图表类型返回动态阈值与维度权重（增强版）。
    维度权重键：vlm/color/text/struct

    优化说明：
    - 调整 VLM 权重降低主观评分波动影响
    - 针对颜色/结构敏感图表调整对应权重
    - 饼图/热力图降低通过阈值（更难完美复现）
    """
    policies = {
        # 折线图：趋势最重要，颜色次之
        "line": {
            "delta": 0.03,
            "weights": {"vlm": 0.30, "color": 0.20, "text": 0.20, "struct": 0.30},
        },
        # 柱状图：颜色（区分柱子）和结构（柱高）并重
        "bar": {
            "delta": 0.02,
            "weights": {"vlm": 0.30, "color": 0.25, "text": 0.20, "struct": 0.25},
        },
        # 散点图：结构（点分布）最重要
        "scatter": {
            "delta": 0.01,
            "weights": {"vlm": 0.30, "color": 0.15, "text": 0.15, "struct": 0.40},
        },
        # 饼图：颜色（扇区区分）最关键，降低阈值
        "pie": {
            "delta": -0.02,
            "weights": {"vlm": 0.25, "color": 0.40, "text": 0.20, "struct": 0.15},
        },
        # 雷达图：结构（多边形形状）最重要
        "radar": {
            "delta": 0.00,
            "weights": {"vlm": 0.30, "color": 0.20, "text": 0.15, "struct": 0.35},
        },
        # 热力图：颜色（数值映射）最关键
        "heatmap": {
            "delta": 0.00,
            "weights": {"vlm": 0.25, "color": 0.45, "text": 0.15, "struct": 0.15},
        },
        # 未知类型：均衡权重
        "unknown": {
            "delta": 0.00,
            "weights": {"vlm": 0.35, "color": 0.20, "text": 0.20, "struct": 0.25},
        },
    }
    p = policies.get(chart_type, policies["unknown"])
    dynamic_threshold = max(0.0, min(1.0, base_threshold + p["delta"]))
    return dynamic_threshold, p["weights"]


def _refine_weights_by_subplot(
    base_weights: Dict[str, float],
    sub_type_weights: Dict[str, float],
) -> Dict[str, float]:
    """
    根据子类型微调权重（平滑过渡，避免权重突变）。
    """
    refined = base_weights.copy()
    for key, sub_weight in sub_type_weights.items():
        if key in refined:
            refined[key] = 0.7 * refined[key] + 0.3 * sub_weight
    return refined


def _calibrate_vlm_score(
    vlm_raw_score: float,
    algorithm_scores: Dict[str, float],
) -> float:
    """
    VLM 评分校准 - 将 VLM 输出映射到与算法评分一致的量纲。

    使用历史数据统计 VLM 评分分布，进行线性变换。
    解决 VLM 评分倾向于集中在 0.6-0.8 区间的问题。
    """
    import numpy as np

    # 计算算法评分均值作为参考
    algo_mean = float(np.mean(list(algorithm_scores.values())))

    # 如果 VLM 评分与算法评分差异过大，进行校准
    diff = vlm_raw_score - algo_mean

    if abs(diff) > 0.2:
        # VLM 偏离算法评分超过 0.2，进行收缩（向算法评分靠拢）
        calibration_factor = 0.6
        calibrated_score = algo_mean + (vlm_raw_score - algo_mean) * calibration_factor
    else:
        calibrated_score = vlm_raw_score

    return _clamp01(calibrated_score)


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _infer_chart_type_vlm(original_image_path: str, vlm_model: str) -> str:
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
    vlm_model: str = "qwen3.6-plus",
    chart_type: str = "auto",
) -> Tuple[bool, float, str]:
    """
    返回 (是否通过, 分数 0~1, 简短说明)。
    模型需返回 JSON：{"score": 0.82, "pass": true, "summary": "..."}
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

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": [
                {"image": original_image_path},
                {"image": generated_image_path},
                {
                    "text": (
                        "第一张为参考图，第二张为复现图。请只输出 JSON。\n"
                        "补充信息（算法预计算）：\n"
                        f"- color_score={color_result.score:.4f}\n"
                        f"- global_hist_score={color_result.global_hist_score:.4f}\n"
                        f"- block_match_score={color_result.block_match_score:.4f}\n"
                        f"- hsv_score={color_result.hsv_score:.4f}\n"
                        f"- hsv_distance={color_result.hsv_distance:.4f}\n"
                        f"- text_score={text_result.score:.4f}\n"
                        f"- text_bleu={text_result.bleu_score:.4f}\n"
                        f"- text_layout_score={text_result.layout_score:.4f}\n"
                        f"- text_coverage={text_result.coverage_score:.4f}\n"
                        f"- struct_score={struct_result.score:.4f}\n"
                        f"- ssim_score={struct_result.ssim_score:.4f}\n"
                        f"- topology_score={struct_result.topology_score:.4f}\n"
                        f"- distance_consistency={struct_result.distance_consistency:.4f}\n"
                        f"- angle_consistency={struct_result.angle_consistency:.4f}\n"
                        "请综合视觉结构、颜色一致性、文本一致性、整体结构一致性指标给出总评分。"
                    )
                },
            ],
        },
    ]
    raw = call_vlm(messages, model=vlm_model).strip()
    vlm_score, _, vlm_summary = _parse_validator_json(raw, dynamic_threshold)

    # VLM 评分校准 - 解决 VLM 与算法评分量纲不一致问题
    algorithm_scores = {
        "color": color_result.score,
        "text": text_result.score,
        "struct": struct_result.score,
    }
    calibrated_vlm_score = _calibrate_vlm_score(vlm_score, algorithm_scores)

    # 按图表类型的自适应权重融合多维得分。
    final_score = (
        weights["vlm"] * calibrated_vlm_score
        + weights["color"] * color_result.score
        + weights["text"] * text_result.score
        + weights["struct"] * struct_result.score
    )
    final_score = max(0.0, min(1.0, final_score))
    passed = final_score >= dynamic_threshold
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
    return passed, final_score, summary


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
