# -*- coding: utf-8 -*-
"""
统一的 API 调用接口
自动根据配置选择模型提供商
"""
from __future__ import annotations

import os
from typing import List, Optional

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.utils.model_providers import create_model_client, ModelProvider


# 模型提供商默认模型配置
MODEL_DEFAULTS = {
    ModelProvider.QWEN: {
        "vlm": "qwen3.5-plus",
        "llm": "qwen-plus"
    },
    ModelProvider.OPENAI: {
        "vlm": "gpt-4o",
        "llm": "gpt-4o"
    },
    ModelProvider.GEMINI: {
        "vlm": "gemini-1.5-pro",
        "llm": "gemini-1.5-pro"
    },
    ModelProvider.DOUBAO: {
        "vlm": "doubao-seed-2-0-pro-260215",
        "llm": "doubao-seed-2-0-pro-260215"
    }
}


# 全局客户端缓存
_client_cache = {}


def get_model_client():
    """获取当前配置的模型客户端（带缓存）"""
    provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
    
    # 如果已缓存，直接返回
    if provider in _client_cache:
        return _client_cache[provider]
    
    # 获取对应的 API Key
    api_key = None
    if provider == ModelProvider.QWEN:
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    elif provider == ModelProvider.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == ModelProvider.GEMINI:
        api_key = os.getenv("GEMINI_API_KEY")
    elif provider == ModelProvider.DOUBAO:
        api_key = os.getenv("DOUBAO_API_KEY")
    
    if not api_key:
        raise RuntimeError(
            f"未设置 {provider.upper()} 的 API Key。"
            f"请在 .env 文件中设置 {provider.upper()}_API_KEY"
        )
    
    # 创建客户端
    kwargs = {}
    if provider == ModelProvider.OPENAI:
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            kwargs["base_url"] = base_url
    elif provider == ModelProvider.DOUBAO:
        base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        kwargs["base_url"] = base_url
    
    client = create_model_client(provider, api_key, **kwargs)
    
    # 缓存客户端
    _client_cache[provider] = client
    
    return client


def call_vlm(
    messages: List[dict],
    model: Optional[str] = None,
    max_retries: int = 3,
    timeout: int = 120,
) -> str:
    """
    多模态对话（图片+文本），返回模型文本。
    
    Args:
        messages: 消息列表
        model: 模型名称（如果为 None，使用当前提供商的默认 VLM 模型）
        max_retries: 最大重试次数
        timeout: 超时时间（秒）
    
    Returns:
        str: 模型返回的文本
    """
    if model is None:
        # 获取当前提供商
        provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
        # 使用提供商的默认 VLM 模型
        model = MODEL_DEFAULTS.get(provider, MODEL_DEFAULTS[ModelProvider.QWEN])["vlm"]
    
    client = get_model_client()
    return client.call_vlm(messages, model, max_retries, timeout)


def call_llm(
    messages: List[dict],
    model: Optional[str] = None,
    max_retries: int = 3,
    timeout: int = 60,
) -> str:
    """
    纯文本对话。
    
    Args:
        messages: 消息列表
        model: 模型名称（如果为 None，使用当前提供商的默认 LLM 模型）
        max_retries: 最大重试次数
        timeout: 超时时间（秒）
    
    Returns:
        str: 模型返回的文本
    """
    if model is None:
        # 获取当前提供商
        provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
        # 使用提供商的默认 LLM 模型
        model = MODEL_DEFAULTS.get(provider, MODEL_DEFAULTS[ModelProvider.QWEN])["llm"]
    
    client = get_model_client()
    return client.call_llm(messages, model, max_retries, timeout)


def extract_python_code(raw: str) -> str:
    """从模型回复中提取 Python 代码块；若无围栏则返回去首尾空白的全文。"""
    import re
    
    raw = raw.strip()
    fence = re.search(
        r"```(?:python|py)?\s*([\s\S]*?)```",
        raw,
        re.IGNORECASE,
    )
    if fence:
        return fence.group(1).strip()
    return raw


# 获取当前提供商信息（用于调试和日志）
def get_current_provider_info() -> dict:
    """获取当前模型提供商信息"""
    provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
    
    # 获取默认模型
    defaults = MODEL_DEFAULTS.get(provider, MODEL_DEFAULTS[ModelProvider.QWEN])
    vlm_model = os.getenv("DEFAULT_VLM_MODEL", defaults["vlm"])
    llm_model = os.getenv("DEFAULT_LLM_MODEL", defaults["llm"])
    
    return {
        "provider": provider,
        "vlm_model": vlm_model,
        "llm_model": llm_model,
    }
