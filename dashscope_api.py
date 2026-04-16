# -*- coding: utf-8 -*-
"""DashScope（通义）API 封装：VLM 多模态与纯文本 LLM。"""
from __future__ import annotations

import os
import re
from http import HTTPStatus
from typing import Any, List, Optional, Union

import dashscope


def get_api_key() -> str:
    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError(
            "请设置环境变量 DASHSCOPE_API_KEY 为阿里云百炼/灵积 API Key。"
        )
    return key


def _normalize_multimodal_messages(messages: List[dict]) -> List[dict]:
    """将 system 的纯字符串转为多模态接口常用的 [{'text': ...}] 形式。"""
    out = []
    for m in messages:
        if m.get("role") == "system":
            c = m.get("content")
            if isinstance(c, str):
                out.append({**m, "content": [{"text": c}]})
            else:
                out.append(m)
        else:
            out.append(m)
    return out


def call_vlm(
    messages: List[dict],
    model: str = "qwen3.5-plus",
) -> str:
    """多模态对话（图片+文本），返回模型文本。"""
    messages = _normalize_multimodal_messages(messages)
    resp = dashscope.MultiModalConversation.call(
        api_key=get_api_key(),
        model=model,
        messages=messages,
        result_format="message",
        stream=False,
    )
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"VLM 调用失败: {resp.code} {resp.message}")
    return _extract_text_from_mm_content(resp.output.choices[0].message.content)


def call_llm(
    messages: List[dict],
    model: str = "qwen-plus",
) -> str:
    """纯文本对话。"""
    resp = dashscope.Generation.call(
        api_key=get_api_key(),
        model=model,
        messages=messages,
        result_format="message",
        stream=False,
    )
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"LLM 调用失败: {resp.code} {resp.message}")
    content = resp.output.choices[0].message.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return _extract_text_from_mm_content(content).strip()
    return str(content).strip()


def _extract_text_from_mm_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts)
    return str(content)


def extract_javascript_code(raw: str) -> str:
    """从模型回复中提取 JS 代码块；若无围栏则返回去首尾空白的全文。"""
    raw = raw.strip()
    fence = re.search(
        r"```(?:javascript|js|ecmascript)?\s*([\s\S]*?)```",
        raw,
        re.IGNORECASE,
    )
    if fence:
        return fence.group(1).strip()
    return raw


def strip_esm_imports(js: str) -> str:
    """浏览器内联脚本需去掉 import/export。"""
    lines = []
    for line in js.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("export "):
            continue
        lines.append(line)
    return "\n".join(lines).strip()
