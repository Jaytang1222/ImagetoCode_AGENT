# -*- coding: utf-8 -*-
"""
验证器模块
"""
from .color_consistency_validator import evaluate_color_consistency
from .text_consistency_validator import evaluate_text_consistency
from .structural_consistency_validator import evaluate_structural_consistency

__all__ = [
    'evaluate_color_consistency',
    'evaluate_text_consistency',
    'evaluate_structural_consistency',
]
