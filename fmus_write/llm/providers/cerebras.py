"""
Cerebras API provider implementation.

This module provides integration with Cerebras API for LLM functionality.
"""

import json
import time
from typing import List, Dict, Any, Optional, Callable

import aiohttp
from ..base import LLMProvider, LLMMessage
from ..config import get_llm_config, DEFAULT_LLM_CONFIG
from ..key_manager import KeyManager


class CerebrasProvider(LLMProvider):
    """Cerebras API implementation."""

    API_URL = "https://api.cerebras.ai/v1/chat/completions"

    validModels = [
        "llama3.1-8b",
        "llama3.1-70b",
        "llama-3.3-70b",
    ]

    validVisionModels = []
    validImageGenerationModels = []

    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Cerebras provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        self.key_manager = KeyManager(get_llm_config())
        self.default_model = self.validModels[0]

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "cerebras"

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
            True as Cerebras supports streaming
        """
        return True

    async def generate_response(self,
                         messages: List[LLMMessage],
                         model: Optional[str] = None,
                         temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the Cerebras API.

        Args:
            messages: List of messages in the conversation
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response

        Raises:
            ValueError: If no API key is available
            Exception: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("cerebras")

        if not api_key:
            raise ValueError("No API key available for Cerebras")

        # Format messages for API
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
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        api_key.mark_error()
                        raise Exception(f"Cerebras API error: {response.status}, {error_text}")
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
        Generate a streaming response from the Cerebras API.

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
        api_key = self.key_manager.get_random_key("cerebras")

        if not api_key:
            raise ValueError("No API key available for Cerebras")

        # Format messages for API
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

                                try:
                                    data = json.loads(line[6:])  # Skip 'data: ' prefix
                                    if "choices" in data and data["choices"]:
                                        delta = data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            callback(content)
                                except json.JSONDecodeError:
                                    # Skip invalid JSON
                                    pass
                        return

                    error_text = await response.text()
                    api_key.mark_error()
                    raise Exception(f"Cerebras API error: {response.status}, {error_text}")
        except Exception as e:
            # If it's a network error or other non-API error, don't mark the key as errored
            if not isinstance(e, aiohttp.ClientError):
                api_key.mark_error()
            raise e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for the Cerebras API.

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
