"""
Conversation context management for LLMs.

This module handles context management for conversations with LLMs.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path

from .base import LLMMessage


class ConversationContext:
    """Manages the context of a conversation with an LLM."""

    def __init__(self,
                 max_messages: int = 50,
                 max_context_bytes: int = 8192,
                 system_prompt: Optional[str] = None):
        """
        Initialize a new conversation context.

        Args:
            max_messages: Maximum number of messages to keep in context
            max_context_bytes: Maximum context size in bytes
            system_prompt: System prompt to use for the conversation
        """
        self.messages: List[LLMMessage] = []
        self.max_messages = max_messages
        self.max_context_bytes = max_context_bytes

        if system_prompt:
            self.set_system_message(system_prompt)

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> LLMMessage:
        """
        Add a message to the conversation.

        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
            metadata: Additional metadata for the message

        Returns:
            The added message
        """
        message = LLMMessage(role, content, metadata, datetime.now().isoformat())
        self.messages.append(message)

        # Trim context if needed
        self._trim_context_if_needed()

        return message

    def get_messages(self) -> List[LLMMessage]:
        """
        Get all messages in the conversation.

        Returns:
            List of messages
        """
        return self.messages

    def clear(self) -> None:
        """Clear all messages in the conversation."""
        system_message = next((m for m in self.messages if m.role == "system"), None)
        self.messages = []

        # Restore system message if it existed
        if system_message:
            self.messages.append(system_message)

    def set_system_message(self, content: str) -> None:
        """
        Set or update the system message.

        Args:
            content: System message content
        """
        # Remove existing system message if any
        self.messages = [m for m in self.messages if m.role != "system"]

        # Add the new system message at the beginning
        self.messages.insert(0, LLMMessage("system", content))

    def get_system_message(self) -> Optional[str]:
        """
        Get the current system message.

        Returns:
            System message content, or None if no system message is set
        """
        for message in self.messages:
            if message.role == "system":
                return message.content
        return None

    def get_context_size(self) -> int:
        """
        Get the current context size in bytes.

        Returns:
            Context size in bytes
        """
        return sum(len(json.dumps(m.to_dict())) for m in self.messages)

    def _trim_context_if_needed(self) -> None:
        """Trim the context if it exceeds the maximum size."""
        # First, check if we have too many messages
        if len(self.messages) > self.max_messages:
            # Keep the system message and the most recent messages
            system_messages = [m for m in self.messages if m.role == "system"]
            non_system_messages = [m for m in self.messages if m.role != "system"]

            # Keep the most recent messages
            keep_count = self.max_messages - len(system_messages)
            if keep_count > 0:
                non_system_messages = non_system_messages[-keep_count:]
            else:
                non_system_messages = []

            self.messages = system_messages + non_system_messages

        # Then, check if we exceed the maximum context size
        while self.get_context_size() > self.max_context_bytes and len(self.messages) > 1:
            # Find the oldest non-system message
            for i, message in enumerate(self.messages):
                if message.role != "system":
                    self.messages.pop(i)
                    break

    def save_to_file(self, file_path: str) -> None:
        """
        Save the conversation to a file.

        Args:
            file_path: Path to save the file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(Path(file_path)), exist_ok=True)

        # Convert messages to dicts
        data = {
            "messages": [m.to_dict() for m in self.messages],
            "timestamp": datetime.now().isoformat()
        }

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, file_path: str) -> None:
        """
        Load a conversation from a file.

        Args:
            file_path: Path to load the file from
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Clear existing messages
        self.clear()

        # Load messages
        for msg_data in data["messages"]:
            message = LLMMessage.from_dict(msg_data)
            self.messages.append(message)
