"""
Groq API provider implementation.

This module provides integration with Groq's API for LLM functionality.
"""

import time
import aiohttp
import json
from typing import List, Dict, Any, Optional, Callable

from ..base import LLMProvider, LLMMessage
from ..config import get_llm_config, DEFAULT_LLM_CONFIG
from ..key_manager import KeyManager, APIKey


class GroqProvider(LLMProvider):
    """Groq API implementation."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # https://console.groq.com/docs/models
    validModels = [
        "llama-3.3-70b-versatile", # 128k context, 32k output
        "llama-3.1-8b-instant", # 128k context, 8k output
        "mixtral-8x7b-32768", # 32k context
        # previews
        "deepseek-r1-distill-llama-70b", # DeepSeek	128k	-	-	https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B
        "llama3-groq-70b-8192-tool-use-preview", # Groq	8,192	-	-
        "llama3-groq-8b-8192-tool-use-preview", # Groq	8,192	-	-
        "llama-3.3-70b-specdec", # Meta	8,192	-	-
        "llama-3.1-70b-specdec", # Meta	-	8,192	-
        "llama-3.2-1b-preview", # Meta	128k	8,192	-
        "llama-3.2-3b-preview", # Meta	128k	8,192	-
    ]

    # https://console.groq.com/docs/vision
    validVisionModels = [
        "llama-3.2-11b-vision-preview", # Meta	128k	8,192	-
        "llama-3.2-90b-vision-preview", # Meta	128k	8,192	-
    ]

    validImageGenerationModels = []


    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Groq provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        # self.key_manager = key_manager
        self.key_manager = KeyManager(get_llm_config())
        self.default_model = self.validModels[0]

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "groq"

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for this provider.

        Returns:
            List of model identifiers
        """
        return self.validModels

    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Groq supports streaming
        """
        return True

    async def generate_response(self,
                         messages: List[LLMMessage],
                         model: Optional[str] = None,
                         temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate a response using the Groq API.

        Args:
            messages: List of messages in the conversation
            model: Name of the model to use (defaults to llama3-8b-8192)
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response

        Raises:
            ValueError: If no API key is available
            Exception: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("groq")

        if not api_key:
            raise ValueError("No API key available for Groq")

        # Format messages for Groq API (OpenAI-compatible format)
        formatted_messages = self._format_messages_for_api(messages)

        # Prepare request data
        request_data = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
        }

        if max_tokens:
            request_data["max_tokens"] = max_tokens

        # Make API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        api_key.mark_used()
                        # Extract the response text
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        api_key.mark_error()
                        raise Exception(f"API error: {response.status}, {error_text}")
        except Exception as e:
            # If it's a network error or other non-API error, don't mark the key as errored
            if not isinstance(e, aiohttp.ClientError):
                api_key.mark_error()
            raise e

    async def generate_response_streaming(self,
                                   messages: List[LLMMessage],
                                   callback: Callable[[str], None],
                                   model: Optional[str] = None,
                                   temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                   max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the Groq API.

        Args:
            messages: List of messages in the conversation
            callback: Function to call for each chunk of the response
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Raises:
            ValueError: If no API key is available
            Exception: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("groq")

        if not api_key:
            raise ValueError("No API key available for Groq")

        # Format messages for Groq API
        formatted_messages = self._format_messages_for_api(messages)

        # Prepare request data
        request_data = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True  # Enable streaming
        }

        if max_tokens:
            request_data["max_tokens"] = max_tokens

        # Make API request with streaming
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        api_key.mark_used()
                        # Process streaming response
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                if line == 'data: [DONE]':
                                    break

                                data = json.loads(line[6:])  # Skip 'data: ' prefix
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        callback(content)
                    else:
                        error_text = await response.text()
                        api_key.mark_error()
                        raise Exception(f"API error: {response.status}, {error_text}")
        except Exception as e:
            # If it's a network error or other non-API error, don't mark the key as errored
            if not isinstance(e, aiohttp.ClientError):
                api_key.mark_error()
            raise e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for the Groq API (OpenAI-compatible format).

        Args:
            messages: List of LLMMessage objects

        Returns:
            Formatted messages for the API request
        """
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        return formatted_messages
