# -*- coding: utf-8 -*-
"""
整体结构一致性评估器：
1) 基于灰度图计算 SSIM（亮度/对比度/结构）；
2) 基于关键结构元素的几何中心点，计算空间拓扑一致性
   （相对距离 + 相对角度）；
3) 输出 0~1 的整体结构一致性分数。
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageOps


@dataclass
class StructuralConsistencyResult:
    score: float
    ssim_score: float
    topology_score: float
    distance_consistency: float
    angle_consistency: float
    matched_keypoints: int
    details: Dict[str, float]


def evaluate_structural_consistency(
    original_image_path: str,
    generated_image_path: str,
    *,
    resize_to: Tuple[int, int] = (512, 512),
    max_keypoints: int = 12,
    ssim_weight: float = 0.45,
    topology_weight: float = 0.55,
) -> StructuralConsistencyResult:
    """
    计算整体结构一致性分数（0~1）。
    - SSIM 对应公式中的亮度/对比度/结构比较项；
    - Topology 使用关键元素几何中心间的距离与角度关系。
    """
    a = _load_gray_array(original_image_path, resize_to)
    b = _load_gray_array(generated_image_path, resize_to)

    ssim_score = _ssim(a, b)

    pts_a = _extract_keypoint_centers(a, max_keypoints=max_keypoints)
    pts_b = _extract_keypoint_centers(b, max_keypoints=max_keypoints)
    distance_consistency, angle_consistency, matched_n = _topology_consistency(pts_a, pts_b)
    topology_score = _clamp01(0.6 * distance_consistency + 0.4 * angle_consistency)

    total_w = max(ssim_weight + topology_weight, 1e-8)
    score = _clamp01((ssim_weight * ssim_score + topology_weight * topology_score) / total_w)

    return StructuralConsistencyResult(
        score=score,
        ssim_score=ssim_score,
        topology_score=topology_score,
        distance_consistency=distance_consistency,
        angle_consistency=angle_consistency,
        matched_keypoints=matched_n,
        details={
            "ssim_weight": float(ssim_weight),
            "topology_weight": float(topology_weight),
            "max_keypoints": float(max_keypoints),
        },
    )


def _load_gray_array(image_path: str, resize_to: Tuple[int, int]) -> np.ndarray:
    with Image.open(image_path) as im:
        gray = ImageOps.grayscale(im).resize(resize_to, Image.Resampling.BILINEAR)
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    return arr


def _ssim(x: np.ndarray, y: np.ndarray) -> float:
    """
    简化全局 SSIM：
    SSIM = [l(x,y)]^alpha * [c(x,y)]^beta * [s(x,y)]^gamma
    在 alpha=beta=gamma=1 的情况下可化简为常见形式。
    """
    c1 = (0.01 ** 2)
    c2 = (0.03 ** 2)

    mu_x = float(np.mean(x))
    mu_y = float(np.mean(y))
    sigma_x = float(np.var(x))
    sigma_y = float(np.var(y))
    sigma_xy = float(np.mean((x - mu_x) * (y - mu_y)))

    numerator = (2.0 * mu_x * mu_y + c1) * (2.0 * sigma_xy + c2)
    denominator = (mu_x * mu_x + mu_y * mu_y + c1) * (sigma_x + sigma_y + c2)
    if abs(denominator) < 1e-12:
        return 1.0 if abs(numerator) < 1e-12 else 0.0
    return _clamp01((numerator / denominator + 1.0) / 2.0)


def _extract_keypoint_centers(arr: np.ndarray, max_keypoints: int) -> np.ndarray:
    """
    从图中提取关键结构元素近似中心：
    - 边缘增强 -> 二值化 -> 连通域中心；
    - 按连通域面积排序，保留前 max_keypoints。
    """
    img = Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8), mode="L")
    edge = img.filter(ImageFilter.FIND_EDGES)
    edge_arr = np.asarray(edge, dtype=np.float32)

    th = float(np.mean(edge_arr) + 0.8 * np.std(edge_arr))
    mask = edge_arr > th
    comps = _connected_components(mask)
    if not comps:
        return np.zeros((0, 2), dtype=np.float32)

    comps.sort(key=lambda c: c["area"], reverse=True)
    top = comps[: max(max_keypoints, 1)]
    pts = np.array([[c["cx"], c["cy"]] for c in top], dtype=np.float32)
    h, w = arr.shape
    pts[:, 0] /= max(w, 1)
    pts[:, 1] /= max(h, 1)
    return pts


def _connected_components(mask: np.ndarray) -> List[Dict[str, float]]:
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components: List[Dict[str, float]] = []
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            stack = [(y, x)]
            visited[y, x] = True
            area = 0
            sx = 0.0
            sy = 0.0

            while stack:
                cy, cx = stack.pop()
                area += 1
                sx += cx
                sy += cy
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))

            if area >= 20:
                components.append({"area": float(area), "cx": sx / area, "cy": sy / area})
    return components


def _topology_consistency(pts_a: np.ndarray, pts_b: np.ndarray) -> Tuple[float, float, int]:
    """
    以几何中心点集评估拓扑一致性：
    1) 先按最近邻做一一匹配；
    2) 计算匹配点集的相对距离矩阵差异；
    3) 计算匹配点集的相对角度矩阵差异。
    """
    if len(pts_a) == 0 or len(pts_b) == 0:
        return 0.0, 0.0, 0

    pairs = _greedy_match_points(pts_a, pts_b)
    if len(pairs) < 2:
        return 0.0, 0.0, len(pairs)

    a = np.array([pts_a[i] for i, _ in pairs], dtype=np.float32)
    b = np.array([pts_b[j] for _, j in pairs], dtype=np.float32)

    dist_errs = []
    angle_errs = []
    n = len(pairs)
    for i in range(n):
        for j in range(i + 1, n):
            va = a[j] - a[i]
            vb = b[j] - b[i]
            da = float(np.linalg.norm(va))
            db = float(np.linalg.norm(vb))
            if da < 1e-8 and db < 1e-8:
                continue

            dist_err = abs(da - db) / max(da, db, 1e-8)
            dist_errs.append(min(dist_err, 1.0))

            aa = math.atan2(float(va[1]), float(va[0]))
            ab = math.atan2(float(vb[1]), float(vb[0]))
            ad = abs(aa - ab)
            ad = min(ad, 2.0 * math.pi - ad)
            angle_errs.append(min(ad / math.pi, 1.0))

    if not dist_errs:
        return 0.0, 0.0, n
    distance_consistency = _clamp01(1.0 - float(np.mean(dist_errs)))
    angle_consistency = _clamp01(1.0 - float(np.mean(angle_errs))) if angle_errs else 0.0
    return distance_consistency, angle_consistency, n


def _greedy_match_points(pts_a: np.ndarray, pts_b: np.ndarray) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    used_b: set[int] = set()
    for i in range(len(pts_a)):
        best_j = -1
        best_d = 1e9
        for j in range(len(pts_b)):
            if j in used_b:
                continue
            d = float(np.linalg.norm(pts_a[i] - pts_b[j]))
            if d < best_d:
                best_d = d
                best_j = j
        if best_j >= 0:
            used_b.add(best_j)
            pairs.append((i, best_j))
    return pairs


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))
