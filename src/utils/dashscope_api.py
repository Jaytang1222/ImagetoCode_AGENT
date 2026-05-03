# -*- coding: utf-8 -*-
"""
DashScope（通义）API 封装：VLM 多模态与纯文本 LLM。
此文件保留用于向后兼容，新代码请使用 unified_api.py
"""
from __future__ import annotations

import os
import re
import time
from http import HTTPStatus
from typing import Any, List, Optional, Union

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载项目根目录的 .env 文件
except ImportError:
    # 如果没有安装 python-dotenv，继续使用系统环境变量
    pass

# 尝试导入统一 API（如果可用）
try:
    from src.utils.unified_api import call_vlm as unified_call_vlm
    from src.utils.unified_api import call_llm as unified_call_llm
    from src.utils.unified_api import extract_python_code as unified_extract_python_code
    USE_UNIFIED_API = True
except ImportError:
    USE_UNIFIED_API = False
    import dashscope
    import requests


def get_api_key() -> str:
    """获取 API Key（兼容旧配置）"""
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")
    if not key:
        raise RuntimeError(
            "请设置环境变量 DASHSCOPE_API_KEY 或 QWEN_API_KEY 为阿里云百炼/灵积 API Key。"
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
    max_retries: int = 3,
    timeout: int = 120,
) -> str:
    """
    多模态对话（图片+文本），返回模型文本。
    
    如果配置了统一 API，将自动路由到对应的模型提供商。
    否则使用原有的 DashScope 实现。
    """
    # 如果启用了统一 API，使用新的实现
    if USE_UNIFIED_API:
        provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
        if provider != "qwen":
            # 使用统一 API
            return unified_call_vlm(messages, model, max_retries, timeout)
    
    # 否则使用原有的 DashScope 实现
    import time
    import socket
    import ssl
    import urllib3
    
    # 禁用SSL警告（仅在开发环境）
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    messages = _normalize_multimodal_messages(messages)
    
    for attempt in range(max_retries):
        try:
            print(f"[API] 调用 VLM (尝试 {attempt + 1}/{max_retries})...")
            
            # 设置全局 socket 超时
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            
            # 配置SSL上下文以提高兼容性
            try:
                # 创建更宽松的SSL上下文
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                # 允许更多的SSL/TLS版本
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
            except Exception as ssl_err:
                print(f"[API] ⚠️ SSL配置警告: {ssl_err}")
            
            try:
                resp = dashscope.MultiModalConversation.call(
                    api_key=get_api_key(),
                    model=model,
                    messages=messages,
                    result_format="message",
                    stream=False,
                )
            finally:
                # 恢复原始超时设置
                socket.setdefaulttimeout(old_timeout)
            
            if resp.status_code != HTTPStatus.OK:
                raise RuntimeError(f"VLM 调用失败: {resp.code} {resp.message}")
            
            print(f"[API] ✅ VLM 调用成功")
            return _extract_text_from_mm_content(resp.output.choices[0].message.content)
            
        except socket.timeout:
            print(f"[API] ⚠️ Socket 超时")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"VLM 调用失败: 超时，已重试 {max_retries} 次")
        
        except (requests.exceptions.SSLError, ssl.SSLError) as ssl_err:
            print(f"[API] ⚠️ SSL错误: {ssl_err}")
            if attempt < max_retries - 1:
                # SSL错误时等待更长时间
                wait_time = (attempt + 1) * 5
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"VLM 调用失败: SSL连接错误，已重试 {max_retries} 次。请检查网络连接或防火墙设置。")
        
        except KeyboardInterrupt:
            print(f"[API] ⚠️ 用户中断")
            raise
        
        except Exception as e:
            print(f"[API] ⚠️ 调用出错: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise


def call_llm(
    messages: List[dict],
    model: str = "qwen-plus",
    max_retries: int = 3,
    timeout: int = 60,
) -> str:
    """
    纯文本对话。
    
    如果配置了统一 API，将自动路由到对应的模型提供商。
    否则使用原有的 DashScope 实现。
    """
    # 如果启用了统一 API，使用新的实现
    if USE_UNIFIED_API:
        provider = os.getenv("MODEL_PROVIDER", "qwen").lower()
        if provider != "qwen":
            # 使用统一 API
            return unified_call_llm(messages, model, max_retries, timeout)
    
    # 否则使用原有的 DashScope 实现
    import time
    import socket
    import ssl
    
    for attempt in range(max_retries):
        try:
            print(f"[API] 调用 LLM (尝试 {attempt + 1}/{max_retries})...")
            
            # 设置全局 socket 超时
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            
            try:
                resp = dashscope.Generation.call(
                    api_key=get_api_key(),
                    model=model,
                    messages=messages,
                    result_format="message",
                    stream=False,
                )
            finally:
                # 恢复原始超时设置
                socket.setdefaulttimeout(old_timeout)
            
            if resp.status_code != HTTPStatus.OK:
                raise RuntimeError(f"LLM 调用失败: {resp.code} {resp.message}")
            
            print(f"[API] ✅ LLM 调用成功")
            content = resp.output.choices[0].message.content
            if isinstance(content, str):
                return content.strip()
            if isinstance(content, list):
                return _extract_text_from_mm_content(content).strip()
            return str(content).strip()
            
        except socket.timeout:
            print(f"[API] ⚠️ Socket 超时")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"LLM 调用失败: 超时，已重试 {max_retries} 次")
        
        except (requests.exceptions.SSLError, ssl.SSLError) as ssl_err:
            print(f"[API] ⚠️ SSL错误: {ssl_err}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"LLM 调用失败: SSL连接错误，已重试 {max_retries} 次。请检查网络连接。")
        
        except KeyboardInterrupt:
            print(f"[API] ⚠️ 用户中断")
            raise
            
        except Exception as e:
            print(f"[API] ⚠️ 调用出错: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[API] 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise


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
    
def extract_python_code(raw: str) -> str:
    """从模型回复中提取 Python 代码块；若无围栏则返回去首尾空白的全文。"""
    # 如果启用了统一 API，使用新的实现
    if USE_UNIFIED_API:
        return unified_extract_python_code(raw)
    
    # 否则使用原有实现
    raw = raw.strip()
    fence = re.search(
        r"```(?:python|py)?\s*([\s\S]*?)```",
        raw,
        re.IGNORECASE,
    )
    if fence:
        return fence.group(1).strip()
    return raw


