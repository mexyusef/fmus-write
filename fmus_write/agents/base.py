"""
Base agent classes for FMUS-Write.
"""

from typing import Dict, Any, List, Optional, Callable
import json
import logging
from ..llm.utils import parse_llm_json_response

logger = logging.getLogger(__name__)


class Agent:
    """Base class for all agents in the system."""

    def __init__(
        self,
        name: str,
        role: str,
        provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an agent.

        Args:
            name: Agent name
            role: Agent role/purpose
            provider: LLM provider (openai, anthropic, ollama)
            model: Model to use
            temperature: Creativity parameter (0.0-1.0)
            api_key: API key for the provider
        """
        self.name = name
        self.role = role
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.kwargs = kwargs
        self.memory = []
        self._client = None

    def initialize(self) -> None:
        """Initialize the agent's LLM client."""
        if self.provider == "openai":
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Run 'pip install openai'")
                raise
        elif self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error("Anthropic library not installed. Run 'pip install anthropic'")
                raise
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generate text using the agent's LLM.

        Args:
            prompt: The prompt to send to the LLM
            system_message: Optional system message

        Returns:
            str: The generated text
        """
        if not self._client:
            self.initialize()

        try:
            if self.provider == "openai":
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})

                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    **self.kwargs
                )
                return response.choices[0].message.content

            elif self.provider == "anthropic":
                message = self._client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=self.temperature,
                    system=system_message if system_message else "",
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def add_to_memory(self, item: Any) -> None:
        """Add an item to the agent's memory."""
        self.memory.append(item)

    def clear_memory(self) -> None:
        """Clear the agent's memory."""
        self.memory = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature
        }

    # def execute(self, input_data):
    #     """Execute the agent with input data."""
    #     # Generate prompt and get LLM response
    #     # ... existing code ...

    #     # Parse the response using our utility function
    #     try:
    #         response_data = parse_llm_json_response(response_text)
    #         return response_data
    #     except json.JSONDecodeError as e:
    #         self.logger.error(f"Failed to parse LLM response: {e}")
    #         self.logger.debug(f"Raw response that failed to parse: {response_text[:500]}...")
    #         raise


class AgentFactory:
    """Factory for creating agents of different types."""

    _agent_types: Dict[str, type] = {}

    @classmethod
    def register(cls, agent_type: str) -> Callable:
        """Register an agent class with a specific type name."""
        def decorator(agent_class):
            cls._agent_types[agent_type] = agent_class
            return agent_class
        return decorator

    @classmethod
    def create(cls, agent_type: str, **kwargs) -> Agent:
        """Create an agent of the specified type."""
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = cls._agent_types[agent_type]
        return agent_class(**kwargs)
