"""
Base classes for LLM providers.

This module defines the base classes for LLM providers and messages.
"""

import abc
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator


class LLMMessage:
    """
    A message in a conversation with an LLM.

    Attributes:
        role: The role of the message sender (user, assistant, system)
        content: The content of the message
        metadata: Additional metadata for the message
    """

    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None, timestamp: Optional[str] = None):
        """
        Initialize a new message.

        Args:
            role: The role of the message sender (user, assistant, system)
            content: The content of the message
            metadata: Additional metadata for the message
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.

        Returns:
            Dictionary representation of the message
        """
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMMessage':
        """
        Create a message from a dictionary.

        Args:
            data: Dictionary representation of the message

        Returns:
            New LLMMessage instance
        """
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )

    def __str__(self) -> str:
        """
        Get a string representation of the message.

        Returns:
            String representation of the message
        """
        return f"{self.role}: {self.content}"


class LLMProvider(abc.ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface for LLM providers.
    """

    def __init__(self, provider_name: str, supports_streaming: bool = True):
        """
        Initialize a new LLM provider.

        Args:
            provider_name: The name of the provider
            supports_streaming: Whether the provider supports streaming
        """
        self.provider_name = provider_name
        self.supports_streaming = supports_streaming

    @abc.abstractmethod
    async def generate_response(self,
                               messages: List[LLMMessage],
                               model: Optional[str] = None,
                               temperature: float = 0.7,
                               max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of messages in the conversation
            model: Model to use (defaults to provider's default)
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens in the response

        Returns:
            Generated response text
        """
        pass

    async def generate_response_streaming(self,
                                        messages: List[LLMMessage],
                                        callback: Callable[[str], None],
                                        model: Optional[str] = None,
                                        temperature: float = 0.7,
                                        max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the LLM.

        Args:
            messages: List of messages in the conversation
            callback: Function to call with each chunk of the response
            model: Model to use (defaults to provider's default)
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens in the response
        """
        # Default implementation for providers that don't support streaming
        if not self.supports_streaming:
            response = await self.generate_response(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            callback(response)
            return

        # This method should be overridden by providers that support streaming
        raise NotImplementedError("Streaming is not implemented for this provider")

    @abc.abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from this provider.

        Returns:
            List of model names
        """
        pass

    def get_default_model(self) -> str:
        """
        Get the default model for this provider.

        Returns:
            Default model name
        """
        models = self.get_available_models()
        if not models:
            return ""
        return models[0]
