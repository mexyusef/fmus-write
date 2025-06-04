"""
Registry for workflow management.
"""

from typing import Dict, Type, List, Optional, Any
import importlib
import logging
from .base import Workflow

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """Registry for managing and retrieving workflow classes."""

    def __init__(self):
        """Initialize the workflow registry."""
        self._registry: Dict[str, Type[Workflow]] = {}

    def register_workflow(self, workflow_type: str, workflow_class: Type[Workflow]) -> None:
        """
        Register a workflow type with its class.

        Args:
            workflow_type: Unique identifier for the workflow
            workflow_class: The workflow class to register
        """
        self._registry[workflow_type] = workflow_class
        logger.debug(f"Registered workflow: {workflow_type}")

    def get_workflow_class(self, workflow_type: str) -> Optional[Type[Workflow]]:
        """
        Get the workflow class for a specific type.

        Args:
            workflow_type: The workflow type to retrieve

        Returns:
            Optional[Type[Workflow]]: The workflow class or None if not found
        """
        return self._registry.get(workflow_type)

    def create_workflow(
        self,
        workflow_type: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Workflow:
        """
        Create a new workflow instance.

        Args:
            workflow_type: Type of workflow to create
            name: Optional name for the workflow instance
            config: Configuration for the workflow
            **kwargs: Additional parameters for the workflow

        Returns:
            Workflow: The created workflow instance

        Raises:
            ValueError: If the workflow type is not registered
        """
        workflow_class = self.get_workflow_class(workflow_type)
        if not workflow_class:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        workflow_instance = workflow_class(
            name=name or f"{workflow_type}_workflow",
            config=config or {},
            **kwargs
        )
        logger.info(f"Created workflow: {workflow_instance.name} (type: {workflow_type})")
        return workflow_instance

    def list_registered_workflows(self) -> List[str]:
        """
        List all registered workflow types.

        Returns:
            List[str]: List of registered workflow type names
        """
        return list(self._registry.keys())

    def load_workflows(self, package_path: str = "fmus_write.workflows.types") -> None:
        """
        Load workflow types from a package dynamically.

        Args:
            package_path: Path to the package containing workflow modules
        """
        try:
            package = importlib.import_module(package_path)
            for module_name in getattr(package, "__all__", []):
                try:
                    module = importlib.import_module(f"{package_path}.{module_name}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, Workflow)
                            and attr is not Workflow
                        ):
                            # Create a consistent workflow ID: convert CompleteBookWorkflow to complete_book
                            workflow_name = attr_name.replace("Workflow", "")
                            # Convert CamelCase to snake_case
                            workflow_type = ""
                            for i, char in enumerate(workflow_name):
                                if char.isupper() and i > 0:
                                    workflow_type += "_" + char.lower()
                                else:
                                    workflow_type += char.lower()

                            # Register the workflow with its ID
                            self.register_workflow(workflow_type, attr)
                            logger.debug(f"Registered workflow: {workflow_type}")
                            logger.debug(f"Registered workflow from module {module_name}: {workflow_type}")
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error loading workflow module {module_name}: {e}")
        except ImportError as e:
            logger.error(f"Error loading workflow package: {e}")

    def __getitem__(self, workflow_type: str) -> Type[Workflow]:
        """
        Get a workflow class using dictionary-like access.

        Args:
            workflow_type: The workflow type

        Returns:
            Type[Workflow]: The workflow class

        Raises:
            KeyError: If the workflow type is not registered
        """
        if workflow_type not in self._registry:
            raise KeyError(f"Workflow type not registered: {workflow_type}")
        return self._registry[workflow_type]
