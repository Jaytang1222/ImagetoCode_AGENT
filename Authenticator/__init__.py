# -*- coding: utf-8 -*-
"""Authenticator 评估模块。"""

from .color_consistency_validator import (
    ColorConsistencyResult,
    evaluate_color_consistency,
)
from .text_consistency_validator import (
    TextConsistencyResult,
    evaluate_text_consistency,
)
from .structural_consistency_validator import (
    StructuralConsistencyResult,
    evaluate_structural_consistency,
)

__all__ = [
    "ColorConsistencyResult",
    "evaluate_color_consistency",
    "TextConsistencyResult",
    "evaluate_text_consistency",
    "StructuralConsistencyResult",
    "evaluate_structural_consistency",
]
