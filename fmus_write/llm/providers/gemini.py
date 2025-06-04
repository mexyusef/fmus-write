"""
Google Gemini API provider implementation.

This module provides integration with Google's Gemini API for LLM functionality.
"""

import asyncio
import time
from typing import List, Optional, Callable

from google import genai

from ..base import LLMProvider, LLMMessage
from ..config import get_llm_config, DEFAULT_LLM_CONFIG
from ..key_manager import KeyManager


class GeminiProvider(LLMProvider):
    """Google Gemini API implementation using official google.genai SDK."""

    validModels = [
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-exp-1206",
    ]


    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Gemini provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        # self.key_manager = key_manager
        self.key_manager = KeyManager(get_llm_config())
        self.default_model = self.validModels[0]
        self._api_key = None
        self._client = None

    def _get_client(self):
        """
        Get a Gemini client with the current API key.

        Returns:
            Initialized Gemini client and API key

        Raises:
            ValueError: If no API key is available
        """
        # print("\n\nGeminiProvider._get_client()......................#1")
        api_key = self.key_manager.get_random_key("gemini")
        # print("\n\nGeminiProvider._get_client()......................#2")
        if not api_key:
            raise ValueError("No API key available for Gemini")
        # print("\n\nGeminiProvider._get_client()......................#3")
        # Configure the client if the API key has changed
        if self._api_key != api_key.key:
            # print("\n\nGeminiProvider._get_client()......................#4")
            self._client = genai.Client(api_key=api_key.key)
            self._api_key = api_key.key
        # print("\n\nGeminiProvider._get_client()......................#5")
        return self._client, api_key

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "gemini"

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for this provider.

        Returns:
            List of model identifiers
        """
        # https://ai.google.dev/gemini-api/docs/models
        return self.validModels

    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Gemini supports streaming
        """
        return True

    async def generate_response(self,
                         messages: List[LLMMessage],
                         model: Optional[str] = None,
                         temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate a response using the Gemini API.

        Args:
            messages: List of messages in the conversation
            model: Name of the model to use (defaults to the default model)
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response

        Raises:
            ValueError: If no API key is available
            Exception: On API errors or other issues
        """
        client = None
        api_key = None
        print(f"""\n\nGeminiProvider.generate_response()
            messages: {messages}
            model: {model}
            temperature: {temperature}
            max_tokens: {max_tokens}
            """)
        try:
            client, api_key = self._get_client()
            model_name = model or self.default_model
            # Format messages for Gemini API
            formatted_contents = self._format_messages_for_api(messages)

            # Set generation config
            generation_config = {
                "temperature": temperature
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            # Run in an executor to avoid blocking the event loop
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model_name,
                contents=formatted_contents,
                config=generation_config
            )

            api_key.mark_used()
            print(f"""\n\nGeminiProvider.generate_response()
                response: {response.text}
                """)
            return response.text

        except Exception as e:
            if api_key is None:
                # Error occurred before we got an API key
                raise ValueError("Failed to initialize Gemini client") from e

            # Common error handling for all exception types
            if hasattr(e, 'retry_after'):
                # Handle rate limiting
                retry_delay = getattr(e, 'retry_after', "60s")

                # Mark the key as used but not as an error
                api_key.last_used = time.time()

                msg = f"Rate limit exceeded. Retry after {retry_delay}. "
                msg += "Try using a different model like 'gemini-1.5-flash'."
                raise ValueError(msg) from e

            # All other errors mark the key as errored
            api_key.mark_error()

            # Categorize the error type
            error_type = type(e).__name__
            if "Unauthorized" in error_type:
                raise ValueError("Authentication error: Invalid API key for Gemini") from e
            if "InvalidArgument" in error_type:
                raise ValueError(f"Invalid argument: {str(e)}") from e
            if "API" in error_type:
                raise ValueError(f"Gemini API error: {str(e)}") from e
            raise ValueError(f"Error calling Gemini API: {str(e)}") from e

    async def generate_response_streaming(self,
                                   messages: List[LLMMessage],
                                   # callback: Callable[[str], None],
                                   model: Optional[str] = None,
                                   temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                   max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the Gemini API.

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
        client = None
        api_key = None

        try:
            client, api_key = self._get_client()
            model_name = model or self.default_model

            # Format messages for Gemini API
            formatted_contents = self._format_messages_for_api(messages)

            # Set generation config
            generation_config = {
                "temperature": temperature
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create streaming response using a thread to avoid blocking the event loop
            stream_generator = await asyncio.to_thread(
                client.models.generate_content_stream,
                model=model_name,
                contents=formatted_contents,
                config=generation_config
            )

            api_key.mark_used()

            # Process the stream
            for chunk in stream_generator:
                if chunk.text:
                    callback(chunk.text)

        except Exception as e:
            if api_key is None:
                # Error occurred before we got an API key
                raise ValueError("Failed to initialize Gemini client") from e

            # Common error handling for all exception types
            if hasattr(e, 'retry_after'):
                # Handle rate limiting
                retry_delay = getattr(e, 'retry_after', "60s")

                # Mark the key as used but not as an error
                api_key.last_used = time.time()

                msg = f"Rate limit exceeded. Retry after {retry_delay}. "
                msg += "Try using a different model like 'gemini-1.5-flash'."
                raise ValueError(msg) from e

            # All other errors mark the key as errored
            api_key.mark_error()

            # Categorize the error type
            error_type = type(e).__name__
            if "Unauthorized" in error_type:
                raise ValueError("Authentication error: Invalid API key for Gemini") from e
            if "InvalidArgument" in error_type:
                raise ValueError(f"Invalid argument: {str(e)}") from e
            if "API" in error_type:
                raise ValueError(f"Gemini API error: {str(e)}") from e
            raise ValueError(f"Error calling Gemini API: {str(e)}") from e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List:
        """
        Format messages for the Gemini API.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Formatted messages for the API request
        """
        formatted_contents = []

        # Convert messages to the format expected by the google.genai package
        for msg in messages:
            if msg.role == "system":
                # Handle system messages - convert to user message with prefix
                system_prompt = f"[System Instruction]: {msg.content}\n\n"
                system_prompt += "Please acknowledge this system instruction."
                formatted_contents.append({
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                })
                # Add a model response acknowledging the system instruction
                formatted_contents.append({
                    "role": "model",
                    "parts": [{"text": "I'll follow these instructions."}]
                })
            else:
                # Normal message
                formatted_contents.append({
                    "role": msg.role,
                    "parts": [{"text": msg.content}]
                })

        return formatted_contents
