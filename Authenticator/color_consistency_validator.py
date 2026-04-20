#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
颜色一致性评估器：
1) 全局颜色直方图对比（RGB）；
2) 色块匹配（网格分块 + 每块直方图相似度）；
3) 加权 HSV 距离（D_HSV）；
4) 输出 0~1 颜色一致性分数与解释信息。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


@dataclass
class ColorConsistencyResult:
    """颜色一致性量化结果。"""

    score: float
    global_hist_score: float
    block_match_score: float
    hsv_score: float
    hsv_distance: float
    gradient_score: float  # 新增：渐变色检测分数
    grid_size: Tuple[int, int]
    bins_per_channel: int
    details: Dict[str, float]


def evaluate_color_consistency(
    original_image_path: str,
    generated_image_path: str,
    *,
    resize_to: Tuple[int, int] = (512, 512),
    grid_size: Tuple[int, int] = (8, 8),
    bins_per_channel: int = 16,
    global_hist_weight: float = 0.30,
    block_match_weight: float = 0.40,
    hsv_weight: float = 0.20,
    gradient_weight: float = 0.10,  # 新增：渐变色检测权重
    hue_weight: float = 2.0,
    saturation_weight: float = 1.0,
    value_weight: float = 1.0,
) -> ColorConsistencyResult:
    """
    计算颜色一致性分数（0~1）。
    - 全局颜色分布：衡量总体色彩风格是否接近；
    - 色块匹配：衡量局部区域（关键数据、背景、标注附近）颜色还原精度；
    - HSV 距离：衡量色相、饱和度、亮度的综合差异；
    - 渐变色检测：衡量渐变色区域的还原精度（新增）。
    """
    if bins_per_channel <= 1:
        raise ValueError("bins_per_channel 必须大于 1")
    if grid_size[0] <= 0 or grid_size[1] <= 0:
        raise ValueError("grid_size 必须为正整数")

    orig = _load_rgb_array(original_image_path, resize_to)
    gen = _load_rgb_array(generated_image_path, resize_to)

    global_score = _hist_intersection_score(orig, gen, bins_per_channel)
    block_score = _grid_block_hist_score(orig, gen, grid_size, bins_per_channel)
    hsv_distance, hsv_score = _hsv_distance_score(
        orig,
        gen,
        hue_weight=hue_weight,
        saturation_weight=saturation_weight,
        value_weight=value_weight,
    )

    # 新增：渐变色检测
    gradient_strength_orig, main_colors_orig = _gradient_color_detection(orig)
    gradient_strength_gen, main_colors_gen = _gradient_color_detection(gen)
    gradient_score = _gradient_similarity(main_colors_orig, main_colors_gen)

    # 根据渐变强度自适应调整 HSV 权重（渐变色强时提升 HSV 权重）
    adaptive_hsv_weight = hsv_weight * (1.0 + gradient_strength_orig * 0.5)

    weight_sum = max(global_hist_weight + block_match_weight + adaptive_hsv_weight + gradient_weight, 1e-8)
    final_score = (
        global_score * global_hist_weight
        + block_score * block_match_weight
        + hsv_score * adaptive_hsv_weight
        + gradient_score * gradient_weight
    ) / weight_sum
    final_score = _clamp01(final_score)

    details = {
        "global_hist_weight": float(global_hist_weight),
        "block_match_weight": float(block_match_weight),
        "hsv_weight": float(hsv_weight),
        "adaptive_hsv_weight": float(adaptive_hsv_weight),
        "gradient_weight": float(gradient_weight),
        "hue_weight": float(hue_weight),
        "saturation_weight": float(saturation_weight),
        "value_weight": float(value_weight),
        "gradient_strength_orig": float(gradient_strength_orig),
        "gradient_strength_gen": float(gradient_strength_gen),
    }
    return ColorConsistencyResult(
        score=final_score,
        global_hist_score=global_score,
        block_match_score=block_score,
        hsv_score=hsv_score,
        hsv_distance=hsv_distance,
        gradient_score=gradient_score,
        grid_size=grid_size,
        bins_per_channel=bins_per_channel,
        details=details,
    )


def _load_rgb_array(image_path: str, resize_to: Tuple[int, int]) -> np.ndarray:
    with Image.open(image_path) as im:
        rgb = im.convert("RGB").resize(resize_to, Image.Resampling.BILINEAR)
    return np.asarray(rgb, dtype=np.uint8)


def _rgb_hist(arr: np.ndarray, bins_per_channel: int) -> np.ndarray:
    hist_parts = []
    for ch in range(3):
        h, _ = np.histogram(
            arr[..., ch],
            bins=bins_per_channel,
            range=(0, 256),
            density=False,
        )
        hist_parts.append(h.astype(np.float64))
    hist = np.concatenate(hist_parts, axis=0)
    total = np.sum(hist)
    if total <= 0:
        return np.zeros_like(hist)
    return hist / total


def _hist_intersection_score(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    bins_per_channel: int,
) -> float:
    """
    直方图交集相似度：
    score = sum(min(p_i, q_i))，范围 [0, 1]，越大越相似。
    """
    hist_a = _rgb_hist(arr_a, bins_per_channel)
    hist_b = _rgb_hist(arr_b, bins_per_channel)
    return _clamp01(float(np.minimum(hist_a, hist_b).sum()))


def _grid_block_hist_score(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    grid_size: Tuple[int, int],
    bins_per_channel: int,
) -> float:
    gh, gw = grid_size
    h, w, _ = arr_a.shape

    ys = np.linspace(0, h, gh + 1, dtype=np.int32)
    xs = np.linspace(0, w, gw + 1, dtype=np.int32)

    scores = []
    weights = []
    for i in range(gh):
        for j in range(gw):
            y0, y1 = ys[i], ys[i + 1]
            x0, x1 = xs[j], xs[j + 1]
            block_a = arr_a[y0:y1, x0:x1, :]
            block_b = arr_b[y0:y1, x0:x1, :]
            if block_a.size == 0 or block_b.size == 0:
                continue

            score = _hist_intersection_score(block_a, block_b, bins_per_channel)

            # 用原图块内颜色标准差作为权重，减少纯背景区对结果的主导。
            variance_weight = float(np.std(block_a.astype(np.float32)) + 1e-6)
            scores.append(score)
            weights.append(variance_weight)

    if not scores:
        return 0.0
    return _clamp01(float(np.average(np.asarray(scores), weights=np.asarray(weights))))


def _hsv_distance_score(
    arr_a: np.ndarray,
    arr_b: np.ndarray,
    *,
    hue_weight: float,
    saturation_weight: float,
    value_weight: float,
) -> Tuple[float, float]:
    """
    按给定公式计算图像级 HSV 距离并映射为相似度：
    D_HSV = sqrt(WH*(ΔH)^2 + WS*(ΔS)^2 + WV*(ΔV)^2)

    说明：
    - 对图像先转 HSV，再按像素求均方差；
    - H 使用环形距离（0 与 1 邻接）；
    - 最终 distance 归一化到 [0,1]，score = 1 - distance。
    """
    hsv_a = _rgb_to_hsv01(arr_a)
    hsv_b = _rgb_to_hsv01(arr_b)

    dh = np.abs(hsv_a[..., 0] - hsv_b[..., 0])
    dh = np.minimum(dh, 1.0 - dh)
    ds = np.abs(hsv_a[..., 1] - hsv_b[..., 1])
    dv = np.abs(hsv_a[..., 2] - hsv_b[..., 2])

    delta_h = float(np.sqrt(np.mean(np.square(dh))))
    delta_s = float(np.sqrt(np.mean(np.square(ds))))
    delta_v = float(np.sqrt(np.mean(np.square(dv))))

    numerator = np.sqrt(
        hue_weight * (delta_h ** 2)
        + saturation_weight * (delta_s ** 2)
        + value_weight * (delta_v ** 2)
    )
    denominator = np.sqrt(max(hue_weight + saturation_weight + value_weight, 1e-8))
    distance = float(numerator / max(denominator, 1e-8))
    distance = _clamp01(distance)
    score = _clamp01(1.0 - distance)
    return distance, score


def _rgb_to_hsv01(arr: np.ndarray) -> np.ndarray:
    img = Image.fromarray(arr, mode="RGB").convert("HSV")
    hsv = np.asarray(img, dtype=np.float32)
    hsv[..., 0] = hsv[..., 0] / 255.0
    hsv[..., 1] = hsv[..., 1] / 255.0
    hsv[..., 2] = hsv[..., 2] / 255.0
    return hsv


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _gradient_color_detection(arr: np.ndarray) -> Tuple[float, List[Tuple[int, int, int]]]:
    """
    检测图像中的渐变色区域。

    返回：渐变强度分数 + 主色列表
    - 渐变强度：相邻像素颜色变化率
    - 主色：使用 K-Means 聚类提取的主要颜色
    """
    # 计算相邻像素颜色变化率（梯度幅值）
    dx = np.diff(arr.astype(np.float32), axis=1)
    dy = np.diff(arr.astype(np.float32), axis=0)
    gradient_magnitude = np.sqrt(np.mean(dx**2) + np.mean(dy**2))

    # 归一化梯度强度到 [0, 1]
    gradient_strength = _clamp01(gradient_magnitude / 50.0)  # 50 为经验阈值

    # 提取主色（使用 K-Means 聚类）
    try:
        from sklearn.cluster import KMeans
        pixels = arr.reshape(-1, 3)
        # 采样加速（每 10 个像素取 1 个）
        sample_step = max(1, len(pixels) // 1000)
        sampled_pixels = pixels[::sample_step]
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(sampled_pixels)
        main_colors = kmeans.cluster_centers_.astype(int)
        main_colors_list = [tuple(c) for c in main_colors]
    except ImportError:
        # 无 sklearn 时返回简单主色（平均值）
        main_colors_list = [tuple(np.mean(arr, axis=(0, 1)).astype(int))]

    return gradient_strength, main_colors_list


def _gradient_similarity(
    colors_a: List[Tuple[int, int, int]],
    colors_b: List[Tuple[int, int, int]],
) -> float:
    """
    计算两组主色的相似度。
    使用最近邻匹配，返回平均颜色距离的倒数。
    """
    if not colors_a or not colors_b:
        return 0.0

    similarities = []
    for color_a in colors_a:
        # 找到 colors_b 中最近的颜色
        min_distance = float('inf')
        for color_b in colors_b:
            # 欧氏距离
            distance = np.sqrt(
                (color_a[0] - color_b[0])**2 +
                (color_a[1] - color_b[1])**2 +
                (color_a[2] - color_b[2])**2
            )
            min_distance = min(min_distance, distance)

        # 距离转相似度（最大距离 441.67 = sqrt(255^2 * 3)）
        max_distance = 441.67
        similarity = 1.0 - (min_distance / max_distance)
        similarities.append(max(0.0, similarity))

    return _clamp01(np.mean(similarities))
