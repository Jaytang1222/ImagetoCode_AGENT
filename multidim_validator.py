# -*- coding: utf-8 -*-
"""
多维验证器（流程图）：对比「原始参考图」与「修改后代码渲染图」，给出是否通过与分数。
使用 VLM 输出结构化判断。
"""
from __future__ import annotations

import json
import re
from typing import Tuple

from dashscope_api import call_vlm


def multidimensional_validate(
    original_image_path: str,
    generated_image_path: str,
    threshold: float = 0.75,
    vlm_model: str = "qwen3.5-plus",
) -> Tuple[bool, float, str]:
    """
    返回 (是否通过, 分数 0~1, 简短说明)。
    模型需返回 JSON：{"score": 0.82, "pass": true, "summary": "..."}
    """
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
                {"text": "第一张为参考图，第二张为复现图。请只输出 JSON。"},
            ],
        },
    ]
    raw = call_vlm(messages, model=vlm_model).strip()
    score, passed, summary = _parse_validator_json(raw, threshold)
    return passed, score, summary


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
