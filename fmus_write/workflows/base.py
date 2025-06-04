from typing import Dict, Any, Optional, List, Callable, Type
from abc import ABC, abstractmethod
import logging
import uuid
from datetime import datetime
import time
import json
import traceback

from ..agents import Agent, AgentFactory
from ..models.base import BaseModel


class WorkflowStep:
    """A step in a workflow pipeline."""

    def __init__(
        self,
        name: str,
        agent_type: str,
        input_mapping: Dict[str, str],
        output_mapping: Dict[str, str],
        agent_params: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.agent_type = agent_type
        self.input_mapping = input_mapping
        self.output_mapping = output_mapping
        self.agent_params = agent_params or {}
        self.agent: Optional[Agent] = None
        print("WorkflowStep.__init__()")

    def initialize_agent(self):
        """Initialize the agent for this step."""
        if self.agent is None:
            self.agent = AgentFactory.create(self.agent_type, **self.agent_params)
        print("WorkflowStep.initialize_agent()")

    def prepare_input(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map workflow data to agent input format."""
        input_data = {}
        for agent_key, workflow_key in self.input_mapping.items():
            # Handle nested keys with dot notation
            if '.' in workflow_key:
                parts = workflow_key.split('.')
                value = workflow_data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    input_data[agent_key] = value
            else:
                if workflow_key in workflow_data:
                    input_data[agent_key] = workflow_data[workflow_key]
        print("WorkflowStep.prepare_input()")
        return input_data

    def update_workflow_data(self, agent_output: Dict[str, Any], workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map agent output to workflow data."""
        for agent_key, workflow_key in self.output_mapping.items():
            # Handle nested keys with dot notation for output
            if '.' in workflow_key:
                parts = workflow_key.split('.')
                target = workflow_data
                for part in parts[:-1]:
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                if agent_key in agent_output:
                    target[parts[-1]] = agent_output[agent_key]
            else:
                if agent_key in agent_output:
                    workflow_data[workflow_key] = agent_output[agent_key]
        print("WorkflowStep.update_workflow_data()")
        return workflow_data

    def execute(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute this step on the workflow data."""
        print(f">>> WorkflowStep.execute: {self.name} (agent: {self.agent_type})")

        # Prepare input data
        input_data = self.prepare_input(workflow_data)
        print(f">>> Input data prepared for {self.name}")

        try:
            # Get the agent implementation
            agent = self.agent
            print(f">>> Agent obtained: {self.agent_type}")

            # Execute the agent with input data
            print(f">>> Calling agent.execute...")
            output_data = agent.process(input_data)
            print(f">>> Agent.execute completed")

            # Check output
            if output_data is None:
                print(f"!!! WARNING: Agent returned None output")
            elif not output_data:
                print(f"!!! WARNING: Agent returned empty output: {output_data}")
            else:
                print(f">>> Agent returned output of type: {type(output_data)}")
                if isinstance(output_data, dict):
                    print(f">>> Output keys: {list(output_data.keys())}")

            # Update workflow data with output according to mapping
            updated_data = workflow_data.copy()
            for agent_key, workflow_key in self.output_mapping.items():
                if agent_key in output_data:
                    print(f">>> Mapping output key '{agent_key}' to workflow key '{workflow_key}'")
                    # Use dot notation to access nested keys
                    self.set_nested_value(updated_data, workflow_key, output_data[agent_key])
                else:
                    print(f"!!! WARNING: Expected output key '{agent_key}' not found in agent output")

            return updated_data

        except json.JSONDecodeError as je:
            print(f"\n!!! JSON DECODE ERROR in WorkflowStep.execute for {self.name}: {str(je)} !!!")
            print(f"Error position: line {je.lineno}, column {je.colno}, char {je.pos}")

            # Try to dump the raw content that caused the error
            if hasattr(je, 'doc'):
                print(f"Raw content that failed to parse (first 500 chars):")
                if je.doc:
                    print(f"{je.doc[:500]}...")
                else:
                    print("Empty string received (this is the likely cause)")
            else:
                print("No raw content available from error")

            # Print input data that led to this error
            print(f"Input data that led to this error (keys): {list(input_data.keys()) if isinstance(input_data, dict) else 'not a dict'}")
            raise

        except Exception as e:
            print(f"\n!!! ERROR in WorkflowStep.execute for {self.name}: {str(e)} !!!")
            print(f"Exception type: {type(e).__name__}")
            print(f"Traceback:")
            traceback.print_exc()

            # Print input data that led to this error
            print(f"Input data that led to this error (keys): {list(input_data.keys()) if isinstance(input_data, dict) else 'not a dict'}")
            raise


class WorkflowState(BaseModel):
    """State of a workflow execution."""

    def __init__(
        self,
        workflow_type: str,
        data: Optional[Dict[str, Any]] = None,
        current_step: int = 0,
        completed_steps: Optional[List[str]] = None,
        id: Optional[str] = None
    ):
        super().__init__(id)
        self.workflow_type = workflow_type
        self.data = data or {}
        self.current_step = current_step
        self.completed_steps = completed_steps or []
        self.status = "initialized"
        self.errors: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "workflow_type": self.workflow_type,
            "data": self.data,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "status": self.status,
            "errors": self.errors
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        instance = super().from_dict(data)
        instance.workflow_type = data.get("workflow_type", "")
        instance.data = data.get("data", {})
        instance.current_step = data.get("current_step", 0)
        instance.completed_steps = data.get("completed_steps", [])
        instance.status = data.get("status", "initialized")
        instance.errors = data.get("errors", [])
        return instance

    def add_error(self, step_name: str, error_message: str, details: Any = None):
        """Add an error to the workflow state."""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "message": error_message,
            "details": details
        })
        self.update()


class Workflow(ABC):
    """Base class for all workflows in the system."""

    def __init__(
        self,
        name: str,
        description: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a workflow.

        Args:
            name: Workflow name
            description: Description of what the workflow does
            config: Configuration parameters
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.state: Dict[str, Any] = {
            "status": "initialized",
            "progress": 0.0,
            "current_step": None,
            "results": {},
            "start_time": None,
            "end_time": None,
            "errors": []
        }
        self.steps: List[WorkflowStep] = []
        self.logger = logging.getLogger(f"fmus_write.workflow.{self.name}")

    @abstractmethod
    def setup_steps(self):
        """Set up the workflow steps.

        This method should be implemented by all workflow subclasses.
        """
        pass

    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps.append(step)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow with the given input data.

        Args:
            input_data: Input data for the workflow

        Returns:
            Dict[str, Any]: The workflow results
        """
        # Set up the workflow steps if not already done
        if not self.steps:
            self.setup_steps()

        # Initialize workflow state
        if input_data:
            self.state["data"].update(input_data)

        self.state["status"] = "running"
        self.state["start_time"] = time.time()
        self.state["progress"] = 0.0

        # Execute each step in sequence
        while self.state["current_step"] < len(self.steps):
            step = self.steps[self.state["current_step"]]
            self.logger.info(f"Executing step: {step.name}")

            try:
                # Execute the step
                self.state["data"] = step.execute(self.state["data"])

                # Update state
                self.state["completed_steps"].append(step.name)
                self.state["current_step"] += 1
                self.state["progress"] = (self.state["current_step"] / len(self.steps)) * 100
                self.state["current_step"] = step.name
                self.state.update()

                self.logger.info(f"Step {step.name} completed successfully")
            except Exception as e:
                self.logger.error(f"Error in step {step.name}: {str(e)}")
                self.state["status"] = "error"
                self.state["errors"].append(str(e))
                break

        if self.state["status"] == "running":
            self.state["status"] = "completed"
            self.state["end_time"] = time.time()
            self.state["progress"] = 100.0

            duration = self.state["end_time"] - self.state["start_time"]
            self.logger.info(f"Completed workflow: {self.name} in {duration:.2f}s")

        return self.state["data"]

    def start(self) -> None:
        """Start the workflow execution."""
        self.state["status"] = "running"
        self.state["start_time"] = time.time()
        self.state["progress"] = 0.0
        self.logger.info(f"Starting workflow: {self.name}")

    def complete(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark the workflow as completed.

        Args:
            results: The workflow results

        Returns:
            Dict[str, Any]: The workflow results
        """
        self.state["status"] = "completed"
        self.state["progress"] = 100.0
        self.state["end_time"] = time.time()
        self.state["results"] = results

        duration = self.state["end_time"] - self.state["start_time"]
        self.logger.info(f"Completed workflow: {self.name} in {duration:.2f}s")

        return results

    def fail(self, error: str) -> None:
        """
        Mark the workflow as failed.

        Args:
            error: Error message
        """
        self.state["status"] = "failed"
        self.state["end_time"] = time.time()
        self.state["errors"].append(error)
        self.logger.error(f"Workflow failed: {self.name} - {error}")

    def update_progress(self, progress: float, current_step: Optional[str] = None) -> None:
        """
        Update the workflow progress.

        Args:
            progress: Progress percentage (0-100)
            current_step: Current step being executed
        """
        self.state["progress"] = progress
        if current_step:
            self.state["current_step"] = current_step
        self.logger.debug(f"Workflow progress: {self.name} - {progress:.1f}% ({current_step or 'unknown step'})")

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current workflow state.

        Returns:
            Dict[str, Any]: Current state
        """
        return self.state

    def configure(self, config: Dict[str, Any]) -> None:
        """
        Update the workflow configuration.

        Args:
            config: New configuration values
        """
        self.config.update(config)
        self.logger.debug(f"Updated workflow config: {self.name}")

    def __str__(self) -> str:
        """String representation of the workflow."""
        status = self.state["status"]
        progress = self.state["progress"]
        return f"Workflow(name={self.name}, status={status}, progress={progress:.1f}%)"


class WorkflowRegistry:
    """Registry for workflow classes."""

    _workflow_types: Dict[str, Type[Workflow]] = {}

    @classmethod
    def register(cls, workflow_type: str) -> Callable:
        """Register a workflow class with a specific type name."""
        def decorator(workflow_class):
            cls._workflow_types[workflow_type] = workflow_class
            return workflow_class
        return decorator

    @classmethod
    def create(cls, workflow_type: str, **kwargs) -> Workflow:
        """Create a workflow of the specified type."""
        if workflow_type not in cls._workflow_types:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        workflow_class = cls._workflow_types[workflow_type]
        workflow = workflow_class(**kwargs)
        workflow.setup_steps()
        return workflow
