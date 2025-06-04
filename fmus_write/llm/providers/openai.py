"""
OpenAI provider implementation.

This module provides integration with the OpenAI API.
"""

# import asyncio
# import json
import logging
import time
from typing import List, Dict, Any, Optional, Callable, Union

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    Provider for the OpenAI API.
    """

    validModels = [
        "gpt-4o-mini",
        "gpt-4",
        "gpt-4o",
        "gpt-3.5-turbo",
    ]

    validVisionModels = [
        "gpt-4-vision-preview"
    ]

    validImageGenerationModels = []

    def __init__(self):
        """Initialize the OpenAI provider."""
        # super().__init__(provider_name="openai", supports_streaming=True)
        self._client = None
        self._key_manager = KeyManager(get_llm_config())
        # self._available_models = []
        self._initialize()

    def _initialize(self):
        """Initialize the OpenAI client."""
        if not _OPENAI_AVAILABLE:
            logger.warning("OpenAI Python package not available. Install with 'pip install openai'")
            return

        # Check if we have a valid key
        if not self._key_manager.has_valid_key("openai"):
            logger.warning("No valid OpenAI API key found")
            return

        try:
            # Get a key
            key = self._key_manager.get_random_key("openai")
            if not key:
                logger.error("Failed to get OpenAI API key")
                return

            # Initialize client
            self._client = openai.AsyncOpenAI(api_key=key.key)

            logger.info(f"OpenAI client initialized with {len(self.validModels)} models")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self._client = None

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "openai"

    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Gemini supports streaming
        """
        return True

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models.

        Returns:
            List of model names
        """
        return self.validModels

    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """
        Convert internal message format to OpenAI format.

        Args:
            messages: List of messages to convert

        Returns:
            List of OpenAI-formatted messages
        """
        result = []
        for msg in messages:
            # Map role
            role = msg.role
            if role == "user":
                role = "user"
            elif role == "assistant":
                role = "assistant"
            elif role == "system":
                role = "system"
            else:
                logger.warning(f"Unknown role: {role}, defaulting to user")
                role = "user"

            # Add message
            result.append({
                "role": role,
                "content": msg.content
            })

        return result

    async def generate_response(self,
                              messages: List[LLMMessage],
                              model: Optional[str] = None,
                              temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                              max_tokens: int = 1024,
                              **kwargs) -> str:
        """
        Generate a response using the OpenAI API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            temperature: Temperature for sampling
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response

        Raises:
            Exception: If generation fails
        """
        if not self._client:
            self._initialize()
            if not self._client:
                raise Exception("OpenAI client not initialized")

        try:
            # Get a key
            key = self._key_manager.get_random_key("openai")
            if not key:
                raise Exception("No valid OpenAI API key available")

            # Use a new client with the key
            client = openai.AsyncOpenAI(api_key=key.key)

            # Prepare parameters
            params = {
                "model": model or "gpt-3.5-turbo",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": self._convert_messages(messages),
            }

            # Update with additional parameters
            params.update(kwargs)

            # Generate response
            start_time = time.time()
            response = await client.chat.completions.create(**params)
            end_time = time.time()

            # Mark key as used
            key.mark_used()

            # Log generation
            logger.debug(f"Generated response with OpenAI API in {end_time - start_time:.2f}s")

            # Return response text
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with OpenAI API: {str(e)}")
            raise

    async def generate_response_streaming(self,
                                       messages: List[LLMMessage],
                                       callback: Callable[[str], None],
                                       model: Optional[str] = None,
                                       temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                       max_tokens: int = 1024,
                                       **kwargs) -> None:
        """
        Generate a response using the OpenAI API with streaming.

        Args:
            messages: List of messages in the conversation
            callback: Function to call for each chunk of generated text
            model: Model to use
            temperature: Temperature for sampling
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters

        Raises:
            Exception: If generation fails
        """
        if not self._client:
            self._initialize()
            if not self._client:
                raise Exception("OpenAI client not initialized")

        try:
            # Get a key
            key = self._key_manager.get_random_key("openai")
            if not key:
                raise Exception("No valid OpenAI API key available")

            # Use a new client with the key
            client = openai.AsyncOpenAI(api_key=key.key)

            # Prepare parameters
            params = {
                "model": model or "gpt-3.5-turbo",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": self._convert_messages(messages),
                "stream": True
            }

            # Update with additional parameters
            params.update(kwargs)

            # Generate response with streaming
            start_time = time.time()
            stream = await client.chat.completions.create(**params)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    callback(chunk.choices[0].delta.content)

            end_time = time.time()

            # Mark key as used
            key.mark_used()

            # Log generation
            logger.debug(f"Generated streaming response with OpenAI API in {end_time - start_time:.2f}s")
        except Exception as e:
            logger.error(f"Error generating streaming response with OpenAI API: {str(e)}")
            raise

# No register_provider call needed here - providers are registered in providers/__init__.py
