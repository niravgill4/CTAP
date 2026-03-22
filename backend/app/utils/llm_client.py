"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
import logging
from typing import Optional, Dict, Any, List, Callable
import openai
from openai import OpenAI

from ..utils.logger import get_logger
from ..config import Config
logger = get_logger('mirofish.llm')


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=600.0  # 为本地模型提供更充足的生成时间（10分钟）
        )
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        wait_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            wait_callback: 等待时的回调函数，接收 (剩余秒数, 总秒数)
            
        Returns:
            模型响应文本
        """
        import time
        
        fallback_models_str = getattr(Config, 'LLM_FALLBACK_MODELS', '')
        fallback_models = [m.strip() for m in fallback_models_str.split(',') if m.strip()]
        
        models_to_try = [self.model] + fallback_models
        last_error = None
        max_retries = 10  # Total retry rounds (each round tries all models)
        wait_seconds = 65  # Wait time between retry rounds (requested: 65s)
        
        for retry_round in range(max_retries):
            for current_model in models_to_try:
                kwargs = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                
                if response_format:
                    kwargs["response_format"] = response_format
                
                try:
                    logger.info(f"[{current_model}] Sending LLM request (max_tokens={max_tokens})...")
                    start_time = time.time()
                    response = self.client.chat.completions.create(**kwargs)
                    duration = time.time() - start_time
                    logger.info(f"[{current_model}] LLM request completed in {duration:.2f}s")
                    
                    content = response.choices[0].message.content
                    # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
                    content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
                    return content
                except (openai.NotFoundError, openai.BadRequestError) as e:
                    # 如果是模型找不到或者是请求格式错误，直接尝试下一个备用模型，不进入等待
                    logger.warning(f"Model ID error or bad request on {current_model}: {str(e)[:100]}. Trying next fallback immediately...")
                    last_error = e
                    continue # 立即尝试下一个模型
                except openai.OpenAIError as e:
                    # 其他OpenAI错误（如429速率限制或500服务器错误）
                    logger.warning(f"Error on model {current_model}: {str(e)[:100]}. Will retry round if all fail.")
                    last_error = e
            
            # All models failed this round
            if isinstance(last_error, openai.RateLimitError) and retry_round < max_retries - 1:
                # 只有在确实遇到速率限制时才进行等待
                logger.warning(
                    f"Rate limit hit on all models (round {retry_round + 1}/{max_retries}). "
                    f"Waiting {wait_seconds}s for rate limits to reset..."
                )
                for remaining in range(wait_seconds, 0, -1):
                    if wait_callback:
                        wait_callback(remaining, wait_seconds)
                    logger.info(f"⏳ Rate limit cooldown: {remaining}s remaining...")
                    time.sleep(1)
                logger.info("Cooldown complete, retrying all models...")
            elif retry_round < max_retries - 1:
                # 其他错误（如500或Token超限后的BadRequest），且还有重试机会
                logger.warning(f"Request failed (round {retry_round + 1}/{max_retries}). Retrying round in 1s...")
                time.sleep(1)
        
        # If all retries exhausted, raise the last exception
        if last_error:
            raise last_error
            
        raise Exception("LLM call failed with unknown error.")
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
        wait_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            wait_callback=wait_callback
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")

