"""
Agent factory for creating and managing agents.
"""

from typing import Dict, Any, Type, Optional, List
import importlib
import logging
from .base import Agent

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating and managing agent instances."""

    def __init__(self):
        """Initialize the agent factory."""
        self._registry: Dict[str, Type[Agent]] = {}
        self._instances: Dict[str, Agent] = {}
        self._default_config: Dict[str, Any] = {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        }

    def register_agent_type(self, agent_type: str, agent_class: Type[Agent]) -> None:
        """
        Register an agent type with its class.

        Args:
            agent_type: Type name for the agent
            agent_class: The agent class to register
        """
        self._registry[agent_type] = agent_class
        logger.debug(f"Registered agent type: {agent_type}")

    def set_default_config(self, config: Dict[str, Any]) -> None:
        """
        Set default configuration for agents.

        Args:
            config: Default configuration dictionary
        """
        self._default_config.update(config)
        logger.debug(f"Updated default agent config: {self._default_config}")

    def create_agent(
        self,
        agent_type: str,
        name: str,
        role: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Agent:
        """
        Create a new agent instance.

        Args:
            agent_type: Type of agent to create
            name: Name for the agent
            role: Role/purpose of the agent
            config: Configuration overrides
            **kwargs: Additional agent parameters

        Returns:
            Agent: The created agent instance
        """
        if agent_type not in self._registry:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Combine default config with provided config
        agent_config = self._default_config.copy()
        if config:
            agent_config.update(config)

        # Create the agent instance
        agent_class = self._registry[agent_type]
        agent = agent_class(name=name, role=role, **agent_config, **kwargs)

        # Store the instance
        instance_id = f"{agent_type}:{name}"
        self._instances[instance_id] = agent
        logger.info(f"Created agent: {instance_id}")

        return agent

    def get_agent(self, agent_type: str, name: str) -> Optional[Agent]:
        """
        Retrieve an existing agent instance.

        Args:
            agent_type: Type of the agent
            name: Name of the agent

        Returns:
            Optional[Agent]: The agent instance or None if not found
        """
        instance_id = f"{agent_type}:{name}"
        return self._instances.get(instance_id)

    def load_agent_types(self, package_path: str = "fmus_write.agents.types") -> None:
        """
        Load agent types from a package dynamically.

        Args:
            package_path: Path to the package containing agent type modules
        """
        try:
            package = importlib.import_module(package_path)
            for module_info in getattr(package, "__all__", []):
                try:
                    module = importlib.import_module(f"{package_path}.{module_info}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, Agent)
                            and attr is not Agent
                        ):
                            agent_type = attr_name.replace("Agent", "").lower()
                            self.register_agent_type(agent_type, attr)
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error loading agent module {module_info}: {e}")
        except ImportError as e:
            logger.error(f"Error loading agent types package: {e}")

    def list_registered_types(self) -> List[str]:
        """
        List all registered agent types.

        Returns:
            List[str]: List of registered agent type names
        """
        return list(self._registry.keys())

    def list_instances(self) -> List[str]:
        """
        List all created agent instances.

        Returns:
            List[str]: List of agent instance IDs
        """
        return list(self._instances.keys())
