"""
Cohere API provider implementation.

This module provides integration with Cohere's API for LLM functionality.
"""

import time
import aiohttp
import json
from typing import List, Dict, Any, Optional, Callable

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager, APIKey
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

class CohereProvider(LLMProvider):
    """Cohere API implementation."""

    API_URL = "https://api.cohere.ai/v1/chat"

    validModels = [
        "command-r-plus-08-2024",
    ] + [
        "command",           # Powerful general model
        "command-r",         # Command model with more capabilities
        "command-r-plus",    # Enhanced version
        "command-light",     # Faster, lighter version
        "coral"              # Latest model
    ]
    validVisionModels = []
    validImageGenerationModels = []

    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Cohere provider.

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
        return "cohere"

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
            True as Cohere supports streaming
        """
        return True

    async def generate_response(self,
                         messages: List[LLMMessage],
                         model: Optional[str] = None,
                         temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                         max_tokens: Optional[int] = None) -> str:
        """
        Generate a response using the Cohere API.

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
        api_key = self.key_manager.get_random_key("cohere")

        if not api_key:
            raise ValueError("No API key available for Cohere")

        # Format messages for Cohere API
        chat_history, message = self._format_messages_for_api(messages)

        # Prepare request data
        request_data = {
            "model": model,
            "message": message,
            "temperature": temperature,
        }

        if chat_history:
            request_data["chat_history"] = chat_history

        if max_tokens:
            request_data["max_tokens"] = max_tokens

        # Make API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.key}",
            "Accept": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        api_key.mark_used()
                        # Extract the response text
                        return data["text"]
                    else:
                        error_text = await response.text()
                        api_key.mark_error()

                        # Special handling for rate limiting
                        if response.status == 429:
                            raise Exception(f"Rate limit exceeded. Please try again later.")
                        else:
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
        Generate a streaming response from the Cohere API.

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
        api_key = self.key_manager.get_random_key("cohere")

        if not api_key:
            raise ValueError("No API key available for Cohere")

        # Format messages for Cohere API
        chat_history, message = self._format_messages_for_api(messages)

        # Prepare request data
        request_data = {
            "model": model,
            "message": message,
            "temperature": temperature,
            "stream": True,
        }

        if chat_history:
            request_data["chat_history"] = chat_history

        if max_tokens:
            request_data["max_tokens"] = max_tokens

        # Make API request with streaming
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.key}",
            "Accept": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.API_URL, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        api_key.mark_used()
                        # Process streaming response
                        async for line in response.content:
                            line = line.decode('utf-8').strip()
                            if not line:
                                continue

                            try:
                                data = json.loads(line)
                                if "text" in data:
                                    # The API sends the text in chunks
                                    callback(data["text"])
                                if data.get("is_finished", False):
                                    # End of the message
                                    break
                            except json.JSONDecodeError:
                                # Skip invalid JSON
                                pass
                    else:
                        error_text = await response.text()
                        api_key.mark_error()

                        # Special handling for rate limiting
                        if response.status == 429:
                            raise Exception(f"Rate limit exceeded. Please try again later.")
                        else:
                            raise Exception(f"API error: {response.status}, {error_text}")
        except Exception as e:
            # If it's a network error or other non-API error, don't mark the key as errored
            if not isinstance(e, aiohttp.ClientError):
                api_key.mark_error()
            raise e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> tuple:
        """
        Format messages for the Cohere API.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Tuple of (chat_history, current_message)
        """
        # Cohere expects a different format:
        # - The most recent user message as "message"
        # - Previous messages as "chat_history" list

        chat_history = []
        current_message = ""

        # Extract all messages except system messages and the last user message
        non_system_messages = [msg for msg in messages if msg.role != "system"]

        if not non_system_messages:
            return [], ""

        # The last message from the user will be the "message"
        # All previous messages will be part of chat_history
        for i, msg in enumerate(non_system_messages):
            # If this is the last message and it's from the user, set it as current_message
            if i == len(non_system_messages) - 1 and msg.role == "user":
                current_message = msg.content
            else:
                # Convert role to match Cohere's expected format
                role = "USER" if msg.role == "user" else "CHATBOT"
                chat_history.append({
                    "role": role,
                    "message": msg.content
                })

        # If no current message was set (e.g., last message was from assistant),
        # use an empty message
        if not current_message and non_system_messages:
            # Use the last user message as current_message
            for msg in reversed(non_system_messages):
                if msg.role == "user":
                    current_message = msg.content
                    # Remove this message from chat_history
                    chat_history = [ch for ch in chat_history
                                  if not (ch["role"] == "USER" and ch["message"] == current_message)]
                    break

        # If we couldn't find a user message, use the last message regardless of role
        if not current_message and non_system_messages:
            last_msg = non_system_messages[-1]
            current_message = last_msg.content
            # Adjust chat_history to exclude the last message
            chat_history = [ch for ch in chat_history[:len(chat_history)-1]]

        return chat_history, current_message
