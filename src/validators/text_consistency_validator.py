# -*- coding: utf-8 -*-
"""
文本一致性评估器：
1) OCR 提取文本块（内容 + 边框）；
2) 基于 BLEU 的文本内容一致性评分；
3) 基于文本块空间相对坐标偏差的布局一致性评分；
4) 输出 0~1 文本一致性总分。
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
import math
import os
import re
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# 加载环境变量
load_dotenv()

import pytesseract
# 从环境变量读取 Tesseract 路径
_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


@dataclass
class OCRTextBlock:
    text: str
    conf: float
    left: int
    top: int
    width: int
    height: int


@dataclass
class TextConsistencyResult:
    score: float
    bleu_score: float
    content_score: float
    layout_score: float
    coverage_score: float
    matched_blocks: int
    total_ref_blocks: int
    details: Dict[str, float | str]


def evaluate_text_consistency(
    original_image_path: str,
    generated_image_path: str,
    *,
    ocr_lang: str = "chi_sim+eng",
    max_bleu_n: int = 4,
    content_weight: float = 0.55,
    layout_weight: float = 0.30,
    coverage_weight: float = 0.15,
    min_match_similarity: float = 0.25,
    original_pil_image: Optional[Image.Image] = None,
    generated_pil_image: Optional[Image.Image] = None,
) -> TextConsistencyResult:
    """
    计算文本一致性分数（0~1）。

    - 内容一致性：OCR 文本块两两匹配后，计算字符级 BLEU（含 BP）；
    - 布局一致性：匹配文本块中心点坐标偏差 + 尺寸偏差；
    - 覆盖率：参考图文本块中有多少在生成图中匹配成功。

    可选参数:
        original_pil_image: 预加载的原始图 PIL.Image（RGB），若提供则跳过从磁盘加载。
        generated_pil_image: 预加载的生成图 PIL.Image（RGB），若提供则跳过从磁盘加载。
    """
    try:
        import pytesseract
    except ImportError as exc:
        raise RuntimeError(
            "缺少 pytesseract 依赖，请执行: pip install pytesseract "
            "并确保本机已安装 Tesseract OCR 程序。"
        ) from exc

    ref_blocks, ref_size = _extract_ocr_blocks(
        original_image_path, ocr_lang, pytesseract, pil_image=original_pil_image
    )
    gen_blocks, gen_size = _extract_ocr_blocks(
        generated_image_path, ocr_lang, pytesseract, pil_image=generated_pil_image
    )

    if not ref_blocks:
        # 参考图无文本时，视为文本一致性满分（避免误伤纯图表场景）。
        return TextConsistencyResult(
            score=1.0,
            bleu_score=1.0,
            content_score=1.0,
            layout_score=1.0,
            coverage_score=1.0,
            matched_blocks=0,
            total_ref_blocks=0,
            details={"note": "reference_has_no_text"},
        )

    matches = _match_text_blocks(
        ref_blocks=ref_blocks,
        gen_blocks=gen_blocks,
        min_match_similarity=min_match_similarity,
    )

    bleu_values: List[float] = []
    sim_values: List[float] = []
    layout_values: List[float] = []
    ref_weight_values: List[float] = []
    for ref_idx, gen_idx, sim in matches:
        ref_block = ref_blocks[ref_idx]
        gen_block = gen_blocks[gen_idx]
        bleu = _sentence_bleu(
            _tokenize_for_bleu(ref_block.text),
            _tokenize_for_bleu(gen_block.text),
            max_n=max_bleu_n,
        )
        layout = _layout_similarity(ref_block, gen_block, ref_size, gen_size)
        weight = max(float(len(ref_block.text)), 1.0)
        bleu_values.append(bleu)
        sim_values.append(sim)
        layout_values.append(layout)
        ref_weight_values.append(weight)

    if bleu_values:
        bleu_score = float(_weighted_average(bleu_values, ref_weight_values))
        sim_score = float(_weighted_average(sim_values, ref_weight_values))
        layout_score = float(_weighted_average(layout_values, ref_weight_values))
    else:
        bleu_score = 0.0
        sim_score = 0.0
        layout_score = 0.0

    content_score = _clamp01(0.7 * bleu_score + 0.3 * sim_score)
    coverage_score = _clamp01(len(matches) / max(len(ref_blocks), 1))

    total_weight = max(content_weight + layout_weight + coverage_weight, 1e-8)
    score = (
        content_weight * content_score
        + layout_weight * layout_score
        + coverage_weight * coverage_score
    ) / total_weight
    score = _clamp01(score)

    return TextConsistencyResult(
        score=score,
        bleu_score=bleu_score,
        content_score=content_score,
        layout_score=layout_score,
        coverage_score=coverage_score,
        matched_blocks=len(matches),
        total_ref_blocks=len(ref_blocks),
        details={
            "ref_blocks": float(len(ref_blocks)),
            "gen_blocks": float(len(gen_blocks)),
            "min_match_similarity": float(min_match_similarity),
            "max_bleu_n": float(max_bleu_n),
        },
    )


def _extract_ocr_blocks(
    image_path: str,
    ocr_lang: str,
    pytesseract,
    *,
    pil_image: Optional[Image.Image] = None,
) -> Tuple[List[OCRTextBlock], Tuple[int, int]]:
    if pil_image is not None:
        image = pil_image
    else:
        image = Image.open(image_path).convert("RGB")
    orig_width, orig_height = image.size

    # 优化：OCR 前先降采样到合理分辨率（宽度不超过 2000px），大幅减少 OCR 耗时
    max_dim = 2000
    if orig_width > max_dim or orig_height > max_dim:
        ratio = max_dim / max(orig_width, orig_height)
        new_w = int(orig_width * ratio)
        new_h = int(orig_height * ratio)
        downscaled = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    else:
        downscaled = image
        new_w, new_h = orig_width, orig_height

    prep = _preprocess_for_ocr(downscaled)
    data = pytesseract.image_to_data(
        prep,
        lang=ocr_lang,
        output_type=pytesseract.Output.DICT,
        config="--oem 3 --psm 6",
    )
    # 将 OCR 坐标映射回原始图像坐标系
    scale_x = orig_width / max(new_w, 1)
    scale_y = orig_height / max(new_h, 1)

    blocks: List[OCRTextBlock] = []
    n = len(data.get("text", []))
    for i in range(n):
        raw_text = data["text"][i] if i < len(data["text"]) else ""
        text = _normalize_text(raw_text)
        if not text:
            continue
        conf = _safe_float(
            data.get("conf", ["-1"])[i] if i < len(data.get("conf", [])) else -1
        )
        left = int((int(data.get("left", [0])[i] if i < len(data.get("left", [])) else 0)) * scale_x)
        top = int((int(data.get("top", [0])[i] if i < len(data.get("top", [])) else 0)) * scale_y)
        bw = int((int(data.get("width", [0])[i] if i < len(data.get("width", [])) else 0)) * scale_x)
        bh = int((int(data.get("height", [0])[i] if i < len(data.get("height", [])) else 0)) * scale_y)
        if bw <= 0 or bh <= 0:
            continue
        blocks.append(
            OCRTextBlock(text=text, conf=conf, left=left, top=top, width=bw, height=bh)
        )
    return blocks, (orig_width, orig_height)


def _preprocess_for_ocr(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    gray = ImageEnhance.Contrast(gray).enhance(1.8)
    gray = gray.filter(ImageFilter.SHARPEN)
    # 简单二值化，提升坐标轴标签/图例等细小文本识别率。
    binary = gray.point(lambda p: 255 if p > 150 else 0, mode="1").convert("L")
    return binary


def _match_text_blocks(
    ref_blocks: List[OCRTextBlock],
    gen_blocks: List[OCRTextBlock],
    min_match_similarity: float,
) -> List[Tuple[int, int, float]]:
    matches: List[Tuple[int, int, float]] = []
    used_gen: set[int] = set()
    for i, rb in enumerate(ref_blocks):
        best_idx: Optional[int] = None
        best_score = -1.0
        for j, gb in enumerate(gen_blocks):
            if j in used_gen:
                continue
            sim = _text_similarity(rb.text, gb.text)
            if sim > best_score:
                best_score = sim
                best_idx = j
        if best_idx is not None and best_score >= min_match_similarity:
            used_gen.add(best_idx)
            matches.append((i, best_idx, best_score))
    return matches


def _text_similarity(a: str, b: str) -> float:
    return _clamp01(SequenceMatcher(None, a, b).ratio())


def _layout_similarity(
    ref_block: OCRTextBlock,
    gen_block: OCRTextBlock,
    ref_size: Tuple[int, int],
    gen_size: Tuple[int, int],
) -> float:
    rw, rh = ref_size
    gw, gh = gen_size
    ref_cx = (ref_block.left + ref_block.width / 2.0) / max(rw, 1)
    ref_cy = (ref_block.top + ref_block.height / 2.0) / max(rh, 1)
    gen_cx = (gen_block.left + gen_block.width / 2.0) / max(gw, 1)
    gen_cy = (gen_block.top + gen_block.height / 2.0) / max(gh, 1)

    dx = ref_cx - gen_cx
    dy = ref_cy - gen_cy
    center_dist = math.sqrt(dx * dx + dy * dy) / math.sqrt(2.0)

    ref_area = (ref_block.width / max(rw, 1)) * (ref_block.height / max(rh, 1))
    gen_area = (gen_block.width / max(gw, 1)) * (gen_block.height / max(gh, 1))
    area_diff = abs(ref_area - gen_area)

    # 位置偏差更重要，面积偏差次之。
    layout_error = 0.75 * center_dist + 0.25 * min(area_diff * 4.0, 1.0)
    return _clamp01(1.0 - layout_error)


def _sentence_bleu(reference_tokens: List[str], hypothesis_tokens: List[str], max_n: int = 4) -> float:
    """
    BLEU = BP * exp(sum_n w_n * log(Precision_n))
    """
    if not reference_tokens:
        return 1.0 if not hypothesis_tokens else 0.0
    if not hypothesis_tokens:
        return 0.0

    eps = 1e-12
    weights = [1.0 / max_n] * max_n
    log_precision_sum = 0.0
    for n in range(1, max_n + 1):
        p_n = _modified_precision(reference_tokens, hypothesis_tokens, n)
        log_precision_sum += weights[n - 1] * math.log(max(p_n, eps))

    ref_len = len(reference_tokens)
    hyp_len = len(hypothesis_tokens)
    if hyp_len == 0:
        bp = 0.0
    elif hyp_len > ref_len:
        bp = 1.0
    else:
        bp = math.exp(1.0 - (ref_len / max(hyp_len, 1)))

    bleu = bp * math.exp(log_precision_sum)
    return _clamp01(bleu)


def _modified_precision(reference_tokens: List[str], hypothesis_tokens: List[str], n: int) -> float:
    ref_counts = _ngram_counts(reference_tokens, n)
    hyp_counts = _ngram_counts(hypothesis_tokens, n)
    if not hyp_counts:
        return 0.0
    clipped = 0
    total = 0
    for gram, h_count in hyp_counts.items():
        r_count = ref_counts.get(gram, 0)
        clipped += min(h_count, r_count)
        total += h_count
    return clipped / max(total, 1)


def _ngram_counts(tokens: List[str], n: int) -> Dict[Tuple[str, ...], int]:
    counts: Dict[Tuple[str, ...], int] = {}
    if len(tokens) < n:
        return counts
    for i in range(len(tokens) - n + 1):
        g = tuple(tokens[i : i + n])
        counts[g] = counts.get(g, 0) + 1
    return counts


def _tokenize_for_bleu(text: str) -> List[str]:
    # 中文场景优先字符级分词；英文单词也会按字符参与，保持简洁稳健。
    return list(text)


def _normalize_text(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    # 去除多余空白，保留中英文与常见符号。
    text = re.sub(r"\s+", "", text)
    return text


def _safe_float(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return -1.0


def _weighted_average(values: List[float], weights: List[float]) -> float:
    if not values:
        return 0.0
    w_sum = sum(weights)
    if w_sum <= 1e-8:
        return sum(values) / len(values)
    return sum(v * w for v, w in zip(values, weights)) / w_sum


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))
