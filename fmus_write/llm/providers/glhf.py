"""
GLHF API provider implementation.

This module provides integration with GLHF (Good Luck Have Fun) API for LLM functionality
using OpenAI client with a custom base URL.
"""

from typing import List, Dict, Any, Optional, Callable

from openai import AsyncOpenAI, APIError

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

class GLHFApiError(Exception):
    """Exception raised for GLHF API errors."""


class GLHFProvider(LLMProvider):
    """GLHF API implementation using OpenAI client with custom base URL."""

    BASE_URL = "https://glhf.chat/api/openai/v1"
    validModels = [
        # https://glhf.chat/api/openai/v1
        # https://glhf.chat/chat/create
        # Note that model names will need to be appended with "hf:". For example, hf:meta-llama/Llama-3.1-405B-Instruct.
        "hf:mistralai/Mistral-7B-Instruct-v0.3",
        "hf:mistralai/Mixtral-8x22B-Instruct-v0.1",
        "hf:meta-llama/Llama-3.1-405B-Instruct",
        "hf:meta-llama/Llama-3.3-70B-Instruct",
        "hf:Qwen/Qwen2.5-Coder-32B-Instruct",
        "hf:Qwen/Qwen2.5-72B-Instruct",
        "hf:Qwen/QwQ-32B-Preview",
        "hf:huihui-ai/Llama-3.3-70B-Instruct-abliterated",
    ]

    validVisionModels = [
        "hf:meta-llama/Llama-3.2-90B-Vision-Instruct",
    ]

    validImageGenerationModels = []
    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the GLHF provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        self.key_manager = key_manager or KeyManager(get_llm_config())
        self.default_model = self.validModels[0]

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "glhf"

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
            True as GLHF supports streaming
        """
        return True

    async def generate_response(self,
                         messages: List[LLMMessage],
                         model: Optional[str] = None,
                         temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the GLHF API using OpenAI client.

        Args:
            messages: List of messages in the conversation
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response

        Raises:
            ValueError: If no API key is available
            GLHFApiError: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("glhf")

        if not api_key:
            raise ValueError("No API key available for GLHF")

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Initialize OpenAI client with custom base URL and headers
            headers = {"Authorization": f"Bearer {api_key.key}"}
            client = AsyncOpenAI(
                api_key="dummy_key",  # The real key goes in the headers
                base_url=self.BASE_URL,
                default_headers=headers
            )

            # Prepare parameters
            params = {
                "model": model,
                "messages": formatted_messages,
                "temperature": temperature
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            # Make API request using OpenAI client
            response = await client.chat.completions.create(**params)

            api_key.mark_used()

            # Extract content from response
            if response.choices and len(response.choices) > 0:
                # Clear any potential problematic emojis or symbols
                content = response.choices[0].message.content or ""
                return self._sanitize_response(content)

            return ""

        except APIError as e:
            api_key.mark_error()
            raise GLHFApiError(f"GLHF API error: {str(e)}") from e
        except Exception as e:
            api_key.mark_error()
            raise GLHFApiError(f"GLHF API error: {str(e)}") from e

    async def generate_response_streaming(self,
                                   messages: List[LLMMessage],
                                   callback: Callable[[str], None],
                                   model: Optional[str] = None,
                                   temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                   max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the GLHF API using OpenAI client.

        Args:
            messages: List of messages in the conversation
            callback: Function to call for each chunk of the response
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Raises:
            ValueError: If no API key is available
            GLHFApiError: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("glhf")

        if not api_key:
            raise ValueError("No API key available for GLHF")

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Initialize OpenAI client with custom base URL and headers
            headers = {"Authorization": f"Bearer {api_key.key}"}
            client = AsyncOpenAI(
                api_key="dummy_key",  # The real key goes in the headers
                base_url=self.BASE_URL,
                default_headers=headers
            )

            # Prepare parameters
            params = {
                "model": model,
                "messages": formatted_messages,
                "temperature": temperature,
                "stream": True
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            # Make streaming API request using OpenAI client
            stream = await client.chat.completions.create(**params)

            api_key.mark_used()

            # Process streaming response
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    # OpenAI can sometimes return None for content
                    content = chunk.choices[0].delta.content
                    if content:
                        # Clean the content before sending it to the callback
                        clean_content = self._sanitize_response(content)
                        if clean_content:  # Only call callback if there's actual content
                            callback(clean_content)

        except APIError as e:
            api_key.mark_error()
            raise GLHFApiError(f"GLHF API error: {str(e)}") from e
        except Exception as e:
            api_key.mark_error()
            raise GLHFApiError(f"GLHF API error: {str(e)}") from e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for the GLHF API.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Formatted messages for the API request
        """
        formatted_messages = []
        for msg in messages:
            if msg is not None and hasattr(msg, "role") and hasattr(msg, "content"):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return formatted_messages

    def _sanitize_response(self, text: str) -> str:
        """
        Clean up response text to remove problematic characters.

        Args:
            text: The text to sanitize

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive globe emojis and other patterns found in bad responses
        if "🌐" in text:
            # Split at first globe emoji
            parts = text.split("🌐", 1)
            return parts[0]

        # Remove any other problematic patterns here
        # For example, if there are repeated emoji patterns

        return text
