from typing import Dict, Any, Optional
import logging
import traceback
import json
import sys
from .base import Workflow, WorkflowStep, WorkflowRegistry, WorkflowState


@WorkflowRegistry.register("complete_book")
class CompleteBookWorkflow(Workflow):
    """Workflow for generating a complete book."""

    def __init__(
        self,
        name: str = "Complete Book Generation",
        description: str = "Generate a complete book from initial parameters",
        state: Optional[WorkflowState] = None
    ):
        super().__init__(name, description, state)
        self.logger = logging.getLogger(f"fmus_write.workflow.{getattr(self.state, 'name', 'unnamed')}_complete_book")

    def setup_steps(self):
        """Set up the workflow steps."""
        # Step 1: Story Architecture
        self.add_step(WorkflowStep(
            name="story_architecture",
            agent_type="architect",
            input_mapping={
                "title": "title",
                "genre": "genre",
                "theme": "theme",
                "chapter_count": "chapter_count"
            },
            output_mapping={
                "title": "title",
                "genre": "genre",
                "theme": "theme",
                "summary": "summary",
                "plot_outline": "plot_outline",
                "chapter_count": "chapter_count"
            }
        ))

        # Step 2: Character Development
        self.add_step(WorkflowStep(
            name="character_development",
            agent_type="character_artist",
            input_mapping={
                "story_structure": ".",
                "character_count": "character_count"
            },
            output_mapping={
                "characters": "characters",
                "relationships": "relationships"
            }
        ))

        # Step 3: World Building
        self.add_step(WorkflowStep(
            name="world_building",
            agent_type="world_builder",
            input_mapping={
                "story_structure": ".",
                "time_period": "time_period"
            },
            output_mapping={
                "world": "world"
            }
        ))

        # Step 4: Detailed Plot
        self.add_step(WorkflowStep(
            name="detailed_plot",
            agent_type="plotter",
            input_mapping={
                "story_structure": "."
            },
            output_mapping={
                "chapters": "detailed_chapters",
                "plot_points": "detailed_plot_points"
            }
        ))

        # Steps 5+: Generate each chapter (dynamically added)
        def add_chapter_generation_steps(workflow: CompleteBookWorkflow):
            chapter_count = workflow.state.data.get("chapter_count", 10)
            for i in range(1, chapter_count + 1):
                # Find the chapter data from detailed_chapters
                input_mapping = {
                    "chapter_data": f"detailed_chapters.{i-1}",
                    "characters": "characters",
                    "world": "world"
                }

                workflow.add_step(WorkflowStep(
                    name=f"generate_chapter_{i}",
                    agent_type="narrator",
                    input_mapping=input_mapping,
                    output_mapping={
                        "content": f"generated_chapters.{i-1}.content",
                        "title": f"generated_chapters.{i-1}.title",
                        "chapter_number": f"generated_chapters.{i-1}.number"
                    }
                ))

                # Add an editing step for each chapter
                workflow.add_step(WorkflowStep(
                    name=f"edit_chapter_{i}",
                    agent_type="editor",
                    input_mapping={
                        "content": f"generated_chapters.{i-1}.content",
                        "content_type": "chapter"
                    },
                    output_mapping={
                        "edited_content": f"final_chapters.{i-1}.content",
                        "suggestions": f"final_chapters.{i-1}.edit_notes"
                    }
                ))

        # Register a callback to add chapter generation steps after initialization
        self.add_chapter_generation = add_chapter_generation_steps

    def run(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the workflow with dynamic step addition."""
        print(f"\n### WORKFLOW START: {self.state.name if hasattr(self.state, 'name') else 'unnamed'} ###")

        # Initialize workflow state
        if input_data:
            print(f"Input data keys: {list(input_data.keys())}")
            self.state.data.update(input_data)

        # Run the first four steps
        for _ in range(min(4, len(self.steps))):
            step = self.steps[self.state.current_step]
            print(f"\n>> EXECUTING STEP: {step.name}")

            try:
                # Log input data for debugging
                step_input = step.get_input_data(self.state.data)
                print(f">> Step {step.name} input keys: {list(step_input.keys()) if isinstance(step_input, dict) else 'not a dict'}")

                # Execute the step
                print(f">> Calling step.execute for {step.name}...")
                step_output = step.execute(self.state.data)
                print(f">> Step {step.name} executed")

                # Log output
                if isinstance(step_output, dict):
                    print(f">> Step {step.name} output keys: {list(step_output.keys())}")
                else:
                    print(f">> Step {step.name} output type: {type(step_output)}")

                # Update state with step output
                self.state.data = step_output

                # Update state
                self.state.completed_steps.append(step.name)
                self.state.current_step += 1
                self.state.update()

                print(f">> Step {step.name} completed successfully")
            except json.JSONDecodeError as je:
                # Direct print for immediate visibility
                print(f"\n!!! JSON DECODE ERROR in step {step.name}: {str(je)} !!!")
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

                # Also dump the last successful state
                print(f"Last successful state keys: {list(self.state.data.keys())}")

                self.state.status = "error"
                self.state.add_error(step.name, f"JSON decode error: {str(je)}")
                return self.state.data
            except Exception as e:
                # Print full exception info
                print(f"\n!!! ERROR in step {step.name}: {str(e)} !!!")
                print(f"Exception type: {type(e).__name__}")
                print(f"Traceback:")
                traceback.print_exc()

                self.state.status = "error"
                self.state.add_error(step.name, str(e))
                return self.state.data

        # Now that we have chapter_count, add the chapter generation steps
        print(f"\n>> Adding chapter generation steps")
        self.add_chapter_generation(self)
        print(f">> Added {len(self.steps) - 4} chapter generation steps")

        try:
            # Continue with the rest of the steps
            print(f"\n>> Continuing with parent run method")
            result = super().run()  # Continue with parent run method
            print(f">> Workflow completed successfully")
            return result
        except Exception as e:
            print(f"\n!!! ERROR during workflow execution: {str(e)} !!!")
            print(f"Exception type: {type(e).__name__}")
            print(f"Traceback:")
            traceback.print_exc()

            self.state.status = "error"
            self.state.add_error("workflow_execution", str(e))
            return self.state.data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompleteBookWorkflow':
        """Create a workflow instance from a dictionary."""
        state_data = data.get("state", {})
        state = WorkflowState.from_dict(state_data) if state_data else None

        workflow = cls(
            name=data.get("name", "Complete Book Generation"),
            description=data.get("description", "Generate a complete book"),
            state=state
        )

        # Set up steps based on data
        workflow.setup_steps()

        return workflow


@WorkflowRegistry.register("outline_only")
class OutlineWorkflow(Workflow):
    """Workflow for generating just an outline."""

    def __init__(
        self,
        name: str = "Outline Generation",
        description: str = "Generate a detailed outline for a book",
        state: Optional[WorkflowState] = None
    ):
        super().__init__(name, description, state)

    def setup_steps(self):
        """Set up the workflow steps."""
        # Step 1: Story Architecture
        self.add_step(WorkflowStep(
            name="story_architecture",
            agent_type="architect",
            input_mapping={
                "title": "title",
                "genre": "genre",
                "theme": "theme",
                "chapter_count": "chapter_count"
            },
            output_mapping={
                "title": "title",
                "genre": "genre",
                "theme": "theme",
                "summary": "summary",
                "plot_outline": "plot_outline",
                "chapter_count": "chapter_count"
            }
        ))

        # Step 2: Character Development
        self.add_step(WorkflowStep(
            name="character_development",
            agent_type="character_artist",
            input_mapping={
                "story_structure": ".",
                "character_count": "character_count"
            },
            output_mapping={
                "characters": "characters",
                "relationships": "relationships"
            }
        ))

        # Step 3: World Building
        self.add_step(WorkflowStep(
            name="world_building",
            agent_type="world_builder",
            input_mapping={
                "story_structure": ".",
                "time_period": "time_period"
            },
            output_mapping={
                "world": "world"
            }
        ))

        # Step 4: Detailed Plot
        self.add_step(WorkflowStep(
            name="detailed_plot",
            agent_type="plotter",
            input_mapping={
                "story_structure": "."
            },
            output_mapping={
                "chapters": "detailed_chapters",
                "plot_points": "detailed_plot_points"
            }
        ))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutlineWorkflow':
        """Create a workflow instance from a dictionary."""
        state_data = data.get("state", {})
        state = WorkflowState.from_dict(state_data) if state_data else None

        workflow = cls(
            name=data.get("name", "Outline Generation"),
            description=data.get("description", "Generate a detailed outline"),
            state=state
        )

        # Set up steps based on data
        workflow.setup_steps()

        return workflow


@WorkflowRegistry.register("chapter_generation")
class ChapterGenerationWorkflow(Workflow):
    """Workflow for generating a single chapter."""

    def __init__(
        self,
        name: str = "Chapter Generation",
        description: str = "Generate a single chapter from details",
        state: Optional[WorkflowState] = None
    ):
        super().__init__(name, description, state)

    def setup_steps(self):
        """Set up the workflow steps."""
        # Step 1: Generate the chapter
        self.add_step(WorkflowStep(
            name="generate_chapter",
            agent_type="narrator",
            input_mapping={
                "chapter_data": "chapter_data",
                "characters": "characters",
                "world": "world"
            },
            output_mapping={
                "content": "generated_chapter.content",
                "title": "generated_chapter.title",
                "chapter_number": "generated_chapter.number"
            }
        ))

        # Step 2: Edit the chapter
        self.add_step(WorkflowStep(
            name="edit_chapter",
            agent_type="editor",
            input_mapping={
                "content": "generated_chapter.content",
                "content_type": "chapter"
            },
            output_mapping={
                "edited_content": "final_chapter.content",
                "suggestions": "final_chapter.edit_notes"
            }
        ))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterGenerationWorkflow':
        """Create a workflow instance from a dictionary."""
        state_data = data.get("state", {})
        state = WorkflowState.from_dict(state_data) if state_data else None

        workflow = cls(
            name=data.get("name", "Chapter Generation"),
            description=data.get("description", "Generate a single chapter"),
            state=state
        )

        # Set up steps based on data
        workflow.setup_steps()

        return workflow
