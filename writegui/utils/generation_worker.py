"""
Generation worker for asynchronous content generation.
"""
from PyQt6.QtCore import QThread, pyqtSignal
import logging
import traceback
import asyncio

logger = logging.getLogger("WriterGUI.GenerationWorker")

class GenerationWorker(QThread):
    """Worker thread for asynchronous content generation."""

    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    step_completed = pyqtSignal(int)  # step index
    step_progress = pyqtSignal(int)  # progress within current step (0-100)
    generation_completed = pyqtSignal(bool, object, str)  # success, result, error message

    def __init__(self, controller, workflow_type, params=None):
        """
        Initialize the generation worker.

        Args:
            controller: The application controller
            workflow_type: The type of workflow to generate (complete_book, chapter, etc.)
            params: Additional parameters for the generation
        """
        super().__init__()
        self.controller = controller
        self.workflow_type = workflow_type
        self.params = params or {}
        self.is_cancelled = False

    def run(self):
        """Run the generation process in a separate thread."""
        try:
            logger.info(f"Starting generation worker for {self.workflow_type}")

            # Emit initial progress
            self.progress_updated.emit(0, f"Starting {self.workflow_type} generation...")

            # Get the provider name
            provider_name = self.params.get('provider',
                self.controller.settings_manager.get('llm_provider', 'gemini')).lower()

            logger.info(f"Generating workflow '{self.workflow_type}' with provider: {provider_name}")
            logger.debug(f"Generation parameters: {self.params}")

            # Configure the project with the parameters
            if hasattr(self.controller.current_project, 'configure'):
                logger.debug("Configuring project...")
                self.controller.current_project.configure(settings=self.params)

            # Generate the content
            logger.debug("Starting content generation...")

            # Call the generate method
            result = self.controller.current_project.generate(workflow_type=self.workflow_type, **self.params)

            # Handle the result based on whether it's a coroutine or not
            import asyncio

            if asyncio.iscoroutine(result):
                logger.debug("Handling async generation result")

                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Define a progress callback for the coroutine
                async def run_with_progress():
                    # This would ideally be implemented with actual progress updates
                    # from the generation process
                    steps = 5  # Example number of steps
                    for i in range(steps):
                        if self.is_cancelled:
                            raise asyncio.CancelledError("Generation cancelled by user")

                        # Emit step progress
                        self.step_completed.emit(i)

                        # Simulate progress within step
                        for j in range(10):
                            if self.is_cancelled:
                                raise asyncio.CancelledError("Generation cancelled by user")

                            # Update progress within step
                            progress = j * 10
                            self.step_progress.emit(progress)

                            # Small delay to simulate work
                            await asyncio.sleep(0.1)

                    # Run the actual generation
                    return await result

                try:
                    # Run the coroutine with progress updates
                    generated_content = loop.run_until_complete(run_with_progress())

                    # Store the result in the project
                    self.controller.current_project.generated_content = generated_content

                    # Process the generated content
                    self.controller.current_project._process_generated_content(self.workflow_type)

                    success = generated_content is not None
                except asyncio.CancelledError as e:
                    logger.warning(f"Generation cancelled: {str(e)}")
                    self.generation_completed.emit(False, None, f"Generation cancelled: {str(e)}")
                    return
                finally:
                    # Clean up the event loop
                    loop.close()
            else:
                # Result is already the final content
                success = result is not None

            # Save the project after generation
            if success:
                logger.info(f"Successfully generated {self.workflow_type} content")
                self.controller._save_project_with_backup()
                self.generation_completed.emit(True, result, "")
            else:
                logger.warning(f"Failed to generate {self.workflow_type} content")
                self.generation_completed.emit(False, None, f"Failed to generate {self.workflow_type} content")

        except Exception as e:
            logger.error(f"Error in generation worker: {str(e)}")
            logger.error(traceback.format_exc())
            self.generation_completed.emit(False, None, str(e))

    def cancel(self):
        """Cancel the generation process."""
        logger.info("Cancelling generation process")
        self.is_cancelled = True
