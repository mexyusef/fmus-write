"""
Anthropic provider implementation.

This module provides integration with the Anthropic API.
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any, Optional, Callable, Union

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Provider for the Anthropic API.
    """

    def __init__(self):
        """Initialize the Anthropic provider."""
        super().__init__(provider_name="anthropic", supports_streaming=True)
        self._client = None
        self._key_manager = KeyManager(get_llm_config())
        self._available_models = []
        self._initialize()

    def _initialize(self):
        """Initialize the Anthropic client."""
        if not _ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic Python package not available. Install with 'pip install anthropic'")
            return

        # Check if we have a valid key
        if not self._key_manager.has_valid_key("anthropic"):
            logger.warning("No valid Anthropic API key found")
            return

        try:
            # Get a key
            key = self._key_manager.get_random_key("anthropic")
            if not key:
                logger.error("Failed to get Anthropic API key")
                return

            # Initialize client
            self._client = anthropic.Anthropic(api_key=key.key)

            # Set available models
            self._available_models = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]

            logger.info(f"Anthropic client initialized with {len(self._available_models)} models")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            self._client = None

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models.

        Returns:
            List of model names
        """
        return self._available_models.copy()

    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """
        Convert internal message format to Anthropic format.

        Args:
            messages: List of messages to convert

        Returns:
            List of Anthropic-formatted messages
        """
        result = []
        for msg in messages:
            # Map role
            role = msg.role
            if role == "system":
                # Claude 3 uses system param separately
                continue
            if role == "user":
                role = "user"
            elif role == "assistant":
                role = "assistant"
            else:
                logger.warning(f"Unknown role: {role}, defaulting to user")
                role = "user"

            # Add message
            result.append({
                "role": role,
                "content": msg.content
            })

        return result

    def _get_system_message(self, messages: List[LLMMessage]) -> Optional[str]:
        """
        Extract system message from messages.

        Args:
            messages: List of messages

        Returns:
            System message content or None
        """
        for msg in messages:
            if msg.role == "system":
                return msg.content
        return None

    async def generate_response(self,
                              messages: List[LLMMessage],
                              model: Optional[str] = None,
                              temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                              max_tokens: int = 1024,
                              **kwargs) -> str:
        """
        Generate a response using the Anthropic API.

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
                raise Exception("Anthropic client not initialized")

        try:
            # Get a key
            key = self._key_manager.get_random_key("anthropic")
            if not key:
                raise Exception("No valid Anthropic API key available")

            # Use a new client with the key
            client = anthropic.Anthropic(api_key=key.key)

            # Prepare parameters
            params = {
                "model": model or "claude-3-sonnet-20240229",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": self._convert_messages(messages),
            }

            # Add system message if present
            system_message = self._get_system_message(messages)
            if system_message:
                params["system"] = system_message

            # Update with additional parameters
            params.update(kwargs)

            # Generate response
            start_time = time.time()
            response = await asyncio.to_thread(client.messages.create, **params)
            end_time = time.time()

            # Mark key as used
            key.mark_used()

            # Log generation
            logger.debug(f"Generated response with Anthropic API in {end_time - start_time:.2f}s")

            # Return response text
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating response with Anthropic API: {str(e)}")
            raise

    async def generate_response_streaming(self,
                                       messages: List[LLMMessage],
                                       callback: Callable[[str], None],
                                       model: Optional[str] = None,
                                       temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                       max_tokens: int = 1024,
                                       **kwargs) -> None:
        """
        Generate a response using the Anthropic API with streaming.

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
                raise Exception("Anthropic client not initialized")

        try:
            # Get a key
            key = self._key_manager.get_random_key("anthropic")
            if not key:
                raise Exception("No valid Anthropic API key available")

            # Use a new client with the key
            client = anthropic.Anthropic(api_key=key.key)

            # Prepare parameters
            params = {
                "model": model or "claude-3-sonnet-20240229",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": self._convert_messages(messages),
                "stream": True
            }

            # Add system message if present
            system_message = self._get_system_message(messages)
            if system_message:
                params["system"] = system_message

            # Update with additional parameters
            params.update(kwargs)

            # Generate response with streaming
            start_time = time.time()

            # Define streaming callback
            async def process_stream():
                with client.messages.stream(**params) as stream:
                    for chunk in stream:
                        if chunk.type == "content_block_delta":
                            if hasattr(chunk.delta, "text"):
                                callback(chunk.delta.text)

            # Run streaming
            await process_stream()

            end_time = time.time()

            # Mark key as used
            key.mark_used()

            # Log generation
            logger.debug(f"Generated streaming response with Anthropic API in {end_time - start_time:.2f}s")
        except Exception as e:
            logger.error(f"Error generating streaming response with Anthropic API: {str(e)}")
            raise
