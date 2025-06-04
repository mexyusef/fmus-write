"""
Together.ai API provider implementation.

This module provides integration with Together.ai API for LLM functionality.
"""

from typing import List, Dict, Any, Optional, Callable

from openai import AsyncOpenAI, RateLimitError, APIError, APIConnectionError, AuthenticationError

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

class TogetherProvider(LLMProvider):
    """Together.ai API implementation using OpenAI Python package."""

    BASE_URL = "https://api.together.xyz/v1"
    # https://api.together.xyz/models
    validModels = [
        "deepseek-ai/DeepSeek-V3", # $1.25
        "deepseek-ai/DeepSeek-R1",  # $7
        "meta-llama/Llama-3.3-70B-Instruct-Turbo", # $0.88
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", # $3.5
        "Qwen/Qwen2.5-Coder-32B-Instruct", # $0.8
        "Qwen/Qwen2.5-72B-Instruct-Turbo", # $1.2
        "deepseek-ai/deepseek-llm-67b-chat", # 0.9
        "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    ]

    # C:\ai\yuagent\extensions\yutools\src\libraries\ai\together\vision_library.ts
    validVisionModels = [
        "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "meta-llama/Llama-Vision-Free",
    ]

    # https://api.together.xyz/models
    validImageGenerationModels = [
        "black-forest-labs/FLUX.1-dev",
        "black-forest-labs/FLUX.1-canny",
        "black-forest-labs/FLUX.1-depth",
        "black-forest-labs/FLUX.1-redux",
        "black-forest-labs/FLUX.1-schnell",
        "black-forest-labs/FLUX.1.1-pro",
        "black-forest-labs/FLUX.1-schnell-Free",
    ]

    # https://api.together.xyz/models
    validEmbeddingModels = [
        "togethercomputer/m2-bert-80M-32k-retrieval",
        "togethercomputer/m2-bert-80M-8k-retrieval",
        "togethercomputer/m2-bert-80M-2k-retrieval",
        "WhereIsAI/UAE-Large-V1",
        "BAAI/bge-large-en-v1.5",
        "BAAI/bge-base-en-v1.5",
    ]
    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Together.ai provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        self.key_manager = key_manager or KeyManager(get_llm_config())
        self.default_model = self.validModels[0] # "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    def _get_client(self):
        """
        Get an OpenAI client with the current API key and Together.ai base URL.

        Returns:
            AsyncOpenAI client instance

        Raises:
            ValueError: If no API key is available
        """
        api_key = self.key_manager.get_random_key("together")

        if not api_key:
            raise ValueError("No API key available for Together.ai")

        # Create a new client with the current API key and Together.ai base URL
        return AsyncOpenAI(api_key=api_key.key, base_url=self.BASE_URL), api_key
    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Gemini supports streaming
        """
        return True
    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "together"

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
            True as Together.ai supports streaming
        """
        return True

    async def generate_response(
            self,
            messages: List[LLMMessage],
            model: Optional[str] = None,
            temperature: float = DEFAULT_LLM_CONFIG['temperature'],
            max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the Together.ai API.

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
        client, api_key = self._get_client()

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Create the completion
            completion = await client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            api_key.mark_used()
            return completion.choices[0].message.content

        except RateLimitError as e:
            api_key.mark_error()
            # Check if retry_after is available in the error
            retry_after = getattr(e, 'retry_after', None)
            if retry_after:
                raise ValueError(f"Rate limit exceeded. Retry after {retry_after} seconds.") from e
            raise ValueError("Rate limit exceeded. Please try again later.") from e
        except AuthenticationError as exc:
            api_key.mark_error()
            raise ValueError("Authentication error: Invalid API key") from exc
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)}") from e
        except APIError as e:
            api_key.mark_error()
            raise ValueError(f"API error: {str(e)}") from e
        except Exception as e:
            # If it's not a network error, mark the key as having an error
            api_key.mark_error()
            raise ValueError(f"Error: {str(e)}") from e

    async def generate_response_streaming(
            self,
            messages: List[LLMMessage],
            callback: Callable[[str], None],
            model: Optional[str] = None,
            temperature: float = DEFAULT_LLM_CONFIG['temperature'],
            max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the Together.ai API.

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
        client, api_key = self._get_client()

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Create the streaming completion
            stream = await client.chat.completions.create(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            api_key.mark_used()

            # Process the stream
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    callback(chunk.choices[0].delta.content)

        except RateLimitError as e:
            api_key.mark_error()
            # Check if retry_after is available in the error
            retry_after = getattr(e, 'retry_after', None)
            if retry_after:
                raise ValueError(f"Rate limit exceeded. Retry after {retry_after} seconds.") from e
            raise ValueError("Rate limit exceeded. Please try again later.") from e
        except AuthenticationError as exc:
            api_key.mark_error()
            raise ValueError("Authentication error: Invalid API key") from exc
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)}") from e
        except APIError as e:
            api_key.mark_error()
            raise ValueError(f"API error: {str(e)}") from e
        except Exception as e:
            # If it's not a network error, mark the key as having an error
            api_key.mark_error()
            raise ValueError(f"Error: {str(e)}") from e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for the Together.ai API.

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
