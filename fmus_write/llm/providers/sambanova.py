"""
SambaNova API provider implementation.

This module provides integration with SambaNova API for LLM functionality.
"""

from typing import List, Dict, Any, Optional, Callable

from openai import AsyncOpenAI, RateLimitError, APIError, APIConnectionError, AuthenticationError

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

class SambanovaProvider(LLMProvider):
    """SambaNova API implementation using OpenAI Python package."""

    BASE_URL = "https://api.sambanova.ai/v1"

    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the SambaNova provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        self.key_manager = key_manager or KeyManager(get_llm_config())
        self.default_model = self.validModels[0]

    def _get_client(self):
        """
        Get an OpenAI client with the current API key and SambaNova base URL.

        Returns:
            AsyncOpenAI client instance

        Raises:
            ValueError: If no API key is available
        """
        api_key = self.key_manager.get_random_key("sambanova")

        if not api_key:
            raise ValueError("No API key available for SambaNova")

        # Create a new client with the current API key and SambaNova base URL
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
        return "sambanova"
    validModels = [
        "Meta-Llama-3.1-405B-Instruct",
    ]

    validVisionModels = []
    validImageGenerationModels = []

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
            True as SambaNova supports streaming
        """
        return True

    async def generate_response(
            self,
            messages: List[LLMMessage],
            model: Optional[str] = None,
            temperature: float = DEFAULT_LLM_CONFIG['temperature'],
            max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the SambaNova API.

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
        Generate a streaming response from the SambaNova API.

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
        Format messages for the SambaNova API.

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
