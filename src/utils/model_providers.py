# -*- coding: utf-8 -*-
"""
多模型提供商统一接口
支持: Qwen, OpenAI, Claude, Gemini, DeepSeek, GLM
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum


class ModelProvider(str, Enum):
    """支持的模型提供商"""
    QWEN = "qwen"
    OPENAI = "openai"
    GEMINI = "gemini"
    DOUBAO = "doubao"
    DEEPSEEK = "deepseek"
    RECOMMENDED = "recommended"


class BaseModelClient(ABC):
    """模型客户端基类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    def call_vlm(
        self,
        messages: List[dict],
        model: str,
        max_retries: int = 3,
        timeout: int = 120,
    ) -> str:
        """多模态对话（图片+文本）"""
        pass
    
    @abstractmethod
    def call_llm(
        self,
        messages: List[dict],
        model: str,
        max_retries: int = 3,
        timeout: int = 60,
    ) -> str:
        """纯文本对话"""
        pass
    
    @staticmethod
    def _extract_text_from_content(content) -> str:
        """从多种格式的content中提取文本"""
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


class QwenClient(BaseModelClient):
    """阿里云通义千问客户端"""
    
    # Qwen 多模态模型名单（仅支持 MultiModalConversation 端点）
    MULTIMODAL_MODELS = frozenset({
        "qwen-vl-plus", "qwen-vl-max",
        "qwen3.6-plus", "qwen3.6-flash",
        "qwen3.5-plus", "qwen3.5-flash",
        "qvq-max", "qwen2.5-vl-72b-instruct",
        "qwen2.5-vl-7b-instruct", "qwen2.5-vl-3b-instruct",
    })
    
    # Qwen 纯文本模型名单（仅支持 Generation 端点）
    TEXT_ONLY_MODELS = frozenset({
        "qwen-plus", "qwen-max", "qwen-turbo",
        "qwen3.6-max-preview", "qwen3.6-outline-preview",
        "qwq-plus", "qwq-max",
    })
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        import dashscope
        self.dashscope = dashscope
    
    @classmethod
    def _check_model_endpoint(cls, model: str, expected_type: str) -> None:
        """检查模型是否匹配当前端点类型，不匹配时抛出清晰错误"""
        if expected_type == "llm":
            if model in cls.MULTIMODAL_MODELS:
                raise RuntimeError(
                    f"模型 '{model}' 是多模态模型，仅支持 MultiModalConversation 端点，"
                    f"不能通过 call_llm() (Generation 端点) 调用。"
                    f"请改用纯文本模型（如 qwen-plus, qwen-max, qwen3.6-max-preview）"
                )
        elif expected_type == "vlm":
            if model in cls.TEXT_ONLY_MODELS:
                raise RuntimeError(
                    f"模型 '{model}' 是纯文本模型，仅支持 Generation 端点，"
                    f"不能通过 call_vlm() (MultiModalConversation 端点) 调用。"
                    f"请改用多模态模型（如 qwen3.6-plus, qwen3.6-flash）"
                )
    
    def _normalize_messages(self, messages: List[dict]) -> List[dict]:
        """将 system 的纯字符串转为多模态接口常用的 [{'text': ...}] 形式"""
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
    
    def call_vlm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 120) -> str:
        self._check_model_endpoint(model, "vlm")
        import time
        import socket
        import ssl
        import urllib3
        from http import HTTPStatus
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        messages = self._normalize_messages(messages)
        
        for attempt in range(max_retries):
            try:
                print(f"[Qwen VLM] 调用 (尝试 {attempt + 1}/{max_retries})...")
                
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(timeout)
                
                try:
                    resp = self.dashscope.MultiModalConversation.call(
                        api_key=self.api_key,
                        model=model,
                        messages=messages,
                        result_format="message",
                        stream=False,
                    )
                finally:
                    socket.setdefaulttimeout(old_timeout)
                
                if resp.status_code != HTTPStatus.OK:
                    raise RuntimeError(f"VLM 调用失败: {resp.code} {resp.message}")
                
                print(f"[Qwen VLM] ✅ 调用成功")
                return self._extract_text_from_content(resp.output.choices[0].message.content)
                
            except Exception as e:
                print(f"[Qwen VLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"[Qwen VLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def call_llm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 60) -> str:
        self._check_model_endpoint(model, "llm")
        import time
        import socket
        from http import HTTPStatus
        
        for attempt in range(max_retries):
            try:
                print(f"[Qwen LLM] 调用 (尝试 {attempt + 1}/{max_retries})...")
                
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(timeout)
                
                try:
                    resp = self.dashscope.Generation.call(
                        api_key=self.api_key,
                        model=model,
                        messages=messages,
                        result_format="message",
                        stream=False,
                    )
                finally:
                    socket.setdefaulttimeout(old_timeout)
                
                if resp.status_code != HTTPStatus.OK:
                    raise RuntimeError(f"LLM 调用失败: {resp.code} {resp.message}")
                
                print(f"[Qwen LLM] ✅ 调用成功")
                content = resp.output.choices[0].message.content
                return self._extract_text_from_content(content).strip()
                
            except Exception as e:
                print(f"[Qwen LLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"[Qwen LLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise


class OpenAIClient(BaseModelClient):
    """OpenAI GPT 客户端"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        super().__init__(api_key)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            raise RuntimeError("请安装 openai 库: pip install openai")
    
    def _convert_messages(self, messages: List[dict]) -> List[dict]:
        """转换消息格式为 OpenAI 格式"""
        converted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if isinstance(content, str):
                converted.append({"role": role, "content": content})
            elif isinstance(content, list):
                # 处理多模态内容
                new_content = []
                for item in content:
                    if isinstance(item, dict):
                        if "text" in item:
                            new_content.append({"type": "text", "text": item["text"]})
                        elif "image" in item:
                            # 读取图片并转为 base64
                            import base64
                            with open(item["image"], "rb") as f:
                                image_data = base64.b64encode(f.read()).decode()
                            new_content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_data}"}
                            })
                converted.append({"role": role, "content": new_content})
        
        return converted
    
    def call_vlm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 120) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[OpenAI VLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                converted_messages = self._convert_messages(messages)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=converted_messages,
                    timeout=timeout,
                )
                
                print(f"[OpenAI VLM] ✅ 调用成功")
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"[OpenAI VLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"[OpenAI VLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def call_llm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 60) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[OpenAI LLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                converted_messages = self._convert_messages(messages)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=converted_messages,
                    timeout=timeout,
                )
                
                print(f"[OpenAI LLM] ✅ 调用成功")
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"[OpenAI LLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"[OpenAI LLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise


class GeminiClient(BaseModelClient):
    """Google Gemini 客户端"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise RuntimeError("请安装 google-generativeai 库: pip install google-generativeai")
    
    def _convert_messages(self, messages: List[dict]) -> tuple[str, List[dict]]:
        """转换消息格式为 Gemini 格式"""
        system = ""
        converted = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            # Gemini 使用 "user" 和 "model" 作为角色
            gemini_role = "model" if role == "assistant" else "user"
            
            if role == "system":
                # 将 system 消息转为用户消息的前缀
                if isinstance(content, str):
                    system = content
                elif isinstance(content, list):
                    system = self._extract_text_from_content(content)
            else:
                if isinstance(content, str):
                    converted.append({"role": gemini_role, "parts": [content]})
                elif isinstance(content, list):
                    parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if "text" in item:
                                parts.append(item["text"])
                            elif "image" in item:
                                # Gemini 支持直接传入图片路径
                                from PIL import Image
                                img = Image.open(item["image"])
                                parts.append(img)
                    converted.append({"role": gemini_role, "parts": parts})
        
        return system, converted
    
    def call_vlm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 120) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[Gemini VLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                system, converted_messages = self._convert_messages(messages)
                
                # 创建模型
                gemini_model = self.genai.GenerativeModel(model)
                
                # 如果有 system 消息，添加到第一条用户消息前
                if system and converted_messages:
                    first_msg = converted_messages[0]
                    if first_msg["role"] == "user":
                        first_msg["parts"].insert(0, f"[System Instructions]\n{system}\n\n")
                
                # 开始对话
                chat = gemini_model.start_chat(history=converted_messages[:-1] if len(converted_messages) > 1 else [])
                response = chat.send_message(converted_messages[-1]["parts"])
                
                print(f"[Gemini VLM] ✅ 调用成功")
                return response.text
                
            except Exception as e:
                print(f"[Gemini VLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"[Gemini VLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def call_llm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 60) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[Gemini LLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                system, converted_messages = self._convert_messages(messages)
                
                gemini_model = self.genai.GenerativeModel(model)
                
                if system and converted_messages:
                    first_msg = converted_messages[0]
                    if first_msg["role"] == "user":
                        first_msg["parts"].insert(0, f"[System Instructions]\n{system}\n\n")
                
                chat = gemini_model.start_chat(history=converted_messages[:-1] if len(converted_messages) > 1 else [])
                response = chat.send_message(converted_messages[-1]["parts"])
                
                print(f"[Gemini LLM] ✅ 调用成功")
                return response.text.strip()
                
            except Exception as e:
                print(f"[Gemini LLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"[Gemini LLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise


class DoubaoClient(BaseModelClient):
    """字节跳动豆包客户端（兼容 OpenAI API）"""
    
    def __init__(self, api_key: str, base_url: str = "https://ark.cn-beijing.volces.com/api/v3"):
        super().__init__(api_key)
        try:
            from openai import OpenAI
            # 豆包使用兼容 OpenAI 的 API
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except ImportError:
            raise RuntimeError("请安装 openai 库: pip install openai")
    
    def _convert_messages(self, messages: List[dict]) -> List[dict]:
        """转换消息格式为豆包格式"""
        converted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if isinstance(content, str):
                converted.append({"role": role, "content": content})
            elif isinstance(content, list):
                # 处理多模态内容
                new_content = []
                for item in content:
                    if isinstance(item, dict):
                        if "text" in item:
                            new_content.append({"type": "text", "text": item["text"]})
                        elif "image" in item:
                            # 读取图片并转为 base64
                            import base64
                            with open(item["image"], "rb") as f:
                                image_data = base64.b64encode(f.read()).decode()
                            new_content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_data}"}
                            })
                converted.append({"role": role, "content": new_content})
        
        return converted
    
    def call_vlm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 120) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[Doubao VLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                converted_messages = self._convert_messages(messages)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=converted_messages,
                    timeout=timeout,
                )
                
                print(f"[Doubao VLM] ✅ 调用成功")
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"[Doubao VLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"[Doubao VLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def call_llm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 60) -> str:
        import time
        
        for attempt in range(max_retries):
            try:
                print(f"[Doubao LLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")
                
                converted_messages = self._convert_messages(messages)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=converted_messages,
                    timeout=timeout,
                )
                
                print(f"[Doubao LLM] ✅ 调用成功")
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"[Doubao LLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"[Doubao LLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise


class DeepSeekClient(BaseModelClient):
    """DeepSeek 客户端（兼容 OpenAI API，纯文本模型）"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        except ImportError:
            raise RuntimeError("请安装 openai 库: pip install openai")

    def _convert_messages(self, messages: List[dict]) -> List[dict]:
        """转换消息格式为 OpenAI 格式"""
        converted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if isinstance(content, str):
                converted.append({"role": role, "content": content})
            elif isinstance(content, list):
                new_content = []
                for item in content:
                    if isinstance(item, dict):
                        if "text" in item:
                            new_content.append({"type": "text", "text": item["text"]})
                converted.append({"role": role, "content": new_content})
        return converted

    def call_vlm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 120) -> str:
        """DeepSeek 不支持多模态，调用 VLM 时抛出错误"""
        raise RuntimeError(
            "DeepSeek 是纯文本模型，不支持多模态 (VLM) 调用。请使用 call_llm() 或将 MODEL_PROVIDER 切换为支持 VLM 的提供商。"
        )

    def call_llm(self, messages: List[dict], model: str, max_retries: int = 3, timeout: int = 60) -> str:
        import time

        for attempt in range(max_retries):
            try:
                print(f"[DeepSeek LLM] 调用 {model} (尝试 {attempt + 1}/{max_retries})...")

                converted_messages = self._convert_messages(messages)
                response = self.client.chat.completions.create(
                    model=model,
                    messages=converted_messages,
                    timeout=timeout,
                )

                print(f"[DeepSeek LLM] ✅ 调用成功")
                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"[DeepSeek LLM] ⚠️ 调用出错: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"[DeepSeek LLM] 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise


# 模型提供商工厂
def create_model_client(provider: str, api_key: str, **kwargs) -> BaseModelClient:
    """
    创建模型客户端
    
    Args:
        provider: 提供商名称 (qwen, openai, gemini, doubao)
        api_key: API密钥
        **kwargs: 额外参数 (如 OpenAI/Doubao 的 base_url)
    
    Returns:
        BaseModelClient: 模型客户端实例
    """
    provider = provider.lower()
    
    if provider == ModelProvider.QWEN:
        return QwenClient(api_key)
    elif provider == ModelProvider.OPENAI:
        return OpenAIClient(api_key, kwargs.get("base_url"))
    elif provider == ModelProvider.GEMINI:
        return GeminiClient(api_key)
    elif provider == ModelProvider.DOUBAO:
        return DoubaoClient(api_key, kwargs.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"))
    elif provider == ModelProvider.DEEPSEEK:
        return DeepSeekClient(api_key)
    else:
        raise ValueError(f"不支持的模型提供商: {provider}")
