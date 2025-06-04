"""
LLM service module.

This module provides the main service for LLM interactions.
"""

# import logging
import asyncio
import traceback
import time
from typing import Dict, List, Optional, Any, Callable, Union
from threading import Thread
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot

from .base import LLMMessage, LLMProvider
from .key_manager import KeyManager
from .context_manager import ConversationContext
from .config import load_models_config, DEFAULT_LLM_CONFIG
from .colored_logging import setup_colored_logger

# Set up logger with colors
logger = setup_colored_logger(__name__)

class LLMWorker(QRunnable):
    """Worker for handling LLM requests in a separate thread."""

    class Signals(QObject):
        """Signals for the LLM worker."""
        finished = pyqtSignal(str)
        error = pyqtSignal(str)
        progress = pyqtSignal(str)  # For streaming responses
        debug = pyqtSignal(str)    # For debug messages

    def __init__(self,
                 provider: LLMProvider,
                 messages: List[LLMMessage],
                 model: Optional[str] = None,
                 temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                 max_tokens: Optional[int] = None,
                 streaming: bool = False,
                 debug: bool = False):
        """
        Initialize the LLM worker.

        Args:
            provider: LLM provider to use
            messages: List of messages for the conversation
            model: Model to use for generation
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            streaming: Whether to use streaming generation
            debug: Whether to enable debug logging
        """
        super().__init__()
        self.provider = provider
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.debug = debug
        self.signals = self.Signals()

    def _debug_log(self, message):
        """
        Log a debug message.

        Args:
            message: Debug message to log
        """
        if self.debug:
            logger.debug(f"[LLMWorker] {message}")
            self.signals.debug.emit(message)

    @pyqtSlot()
    def run(self):
        """Execute the LLM request in a separate thread."""
        try:
            # print("\n\nLLMWorker.run()......................#1")
            self._debug_log(f"Starting LLM request (streaming={self.streaming})")
            # print("\n\nLLMWorker.run()......................#2")
            # Log provider and model info
            self._debug_log(f"Provider: {self.provider.provider_name}")
            self._debug_log(f"Model: {self.model}")
            self._debug_log(f"Message count: {len(self.messages)}")
            # print("\n\nLLMWorker.run()......................#3")
            # Create and set up a new event loop
            self._debug_log("Setting up asyncio event loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            logger.info(f"""
            [LLMWorker]
            self.streaming: {self.streaming}
            self.provider.supports_streaming: {self.provider.supports_streaming}
            self.provider.provider_name: {self.provider.provider_name}
            self.model: {self.model}
            self.temperature: {self.temperature}
            self.max_tokens: {self.max_tokens}
            self.messages: {self.messages}
            """)

            if self.streaming and self.provider.supports_streaming:
                # Use streaming API
                self._debug_log("Using streaming API")
                # print("\n\nLLMWorker.run()......................#5")
                async def stream_request():
                    try:
                        self._debug_log("Starting streaming request")
                        start_time = time.time()
                        # print("\n\nLLMWorker.run()......................#6")
                        await self.provider.generate_response_streaming(
                            self.messages,
                            lambda chunk: self.signals.progress.emit(chunk),
                            self.model,
                            self.temperature,
                            self.max_tokens
                        )

                        elapsed = time.time() - start_time
                        self._debug_log(f"Streaming request completed in {elapsed:.2f}s")
                        # print("\n\nLLMWorker.run()......................#7")
                        self.signals.finished.emit("")  # Empty string indicates completion
                    except Exception as e:
                        self._debug_log(f"Streaming request error: {str(e)}")
                        # Print the full traceback for better debugging
                        self._debug_log("".join(traceback.format_exception(type(e), e, e.__traceback__)))
                        self.signals.error.emit(str(e))

                self._debug_log("Running streaming request")
                # print("\n\nLLMWorker.run()......................#8")
                loop.run_until_complete(stream_request())
            else:
                # Use non-streaming API
                self._debug_log("Using non-streaming API")

                async def non_stream_request():
                    try:
                        self._debug_log("Starting non-streaming request")
                        start_time = time.time()
                        response = await self.provider.generate_response(
                            self.messages,
                            self.model,
                            self.temperature,
                            self.max_tokens
                        )

                        elapsed = time.time() - start_time
                        self._debug_log(f"Non-streaming request completed in {elapsed:.2f}s")
                        self.signals.finished.emit(response)
                    except Exception as e:
                        self._debug_log(f"Non-streaming request error: {str(e)}")
                        self._debug_log("".join(traceback.format_exception(type(e), e, e.__traceback__)))
                        self.signals.error.emit(str(e))
                self._debug_log("Running non-streaming request")
                loop.run_until_complete(non_stream_request())
            self._debug_log("Closing event loop")
            loop.close()
            self._debug_log("Worker completed")
        except Exception as e:
            error_msg = f"Thread error: {str(e)}"
            self._debug_log(error_msg)
            self._debug_log("".join(traceback.format_exception(type(e), e, e.__traceback__)))
            self.signals.error.emit(error_msg)


class LLMService:
    """Main service for LLM interactions."""

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the LLM service.

        Args:
            llm_config: LLM configuration dictionary
        """
        self.config = llm_config
        self.debug = self.config.get("debug", False)
        self.default_provider = self.config.get("default_provider", "gemini")
        self.temperature = self.config.get("temperature", DEFAULT_LLM_CONFIG['temperature'])
        self.streaming = self.config.get("streaming", True)
        self.system_prompt = self.config.get("system_prompt", "You are a helpful assistant.")
        self.font_size = self.config.get("font_size", 16)

        # Load models configuration
        self.models_config = load_models_config()

        # Initialize key manager
        self.key_manager = KeyManager()

        # Load keys for each provider
        self._load_provider_keys()

        # Initialize providers
        self.providers = {}
        self._initialize_providers()

        # Initialize context manager
        self.context_manager = ConversationContext(
            max_context_bytes=self.config.get("max_context_bytes", 8192),
            system_prompt=self.system_prompt
        )

        # Thread pool for running LLM requests
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(5)  # Limit concurrent requests

        logger.info(f"LLM service initialized with {len(self.providers)} providers")

    def _load_provider_keys(self):
        """Load API keys for all providers."""
        from .providers import PROVIDER_MAP

        # Try to load keys for each provider
        for provider in PROVIDER_MAP.keys():
            key_path = self.config.get(f"{provider}_keys_path", "")
            if key_path:
                logger.info(f"Loading keys for {provider} from {key_path}")
                self.key_manager.load_keys_from_file(provider, key_path)

    def _initialize_providers(self) -> bool:
        """
        Initialize LLM providers.

        Returns:
            True if at least one provider was initialized successfully
        """
        from .providers import get_provider_class, PROVIDER_MAP

        logger.info(f"Initializing providers from: {list(PROVIDER_MAP.keys())}")
        initialized_count = 0

        # Get available providers with valid API keys
        available_providers = self.key_manager.get_available_providers()
        logger.info(f"Providers with valid API keys: {available_providers}")

        # Initialize each provider that has valid keys
        for provider_name in available_providers:
            try:
                provider_class = get_provider_class(provider_name)
                if not provider_class:
                    logger.warning(f"No provider class found for {provider_name}")
                    continue

                logger.info(f"Initializing provider: {provider_name}")
                provider_instance = provider_class(
                    # self.key_manager
                )
                self.providers[provider_name] = provider_instance
                initialized_count += 1
                logger.info(f"***       Successfully initialized provider: {provider_name}")
            except Exception as e:
                logger.error(f"*** Failed to initialize provider {provider_name}: {str(e)}")
                logger.error("".join(traceback.format_exception(type(e), e, e.__traceback__)))

        logger.info(f"Initialized {initialized_count} providers")
        return initialized_count > 0

    def get_available_providers(self) -> List[str]:
        """
        Get a list of available providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def get_available_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get a list of available models for providers.

        Args:
            provider: Provider name, or None for all providers

        Returns:
            Dictionary mapping provider names to lists of model names
        """
        result = {}

        if provider:
            # Get models for a specific provider
            if provider in self.providers:
                result[provider] = self.providers[provider].get_available_models()
            elif provider in self.models_config:
                # Provider not initialized, but we have config for it
                result[provider] = self.models_config[provider].get("models", [])
        else:
            # Get models for all providers
            for p_name, p_instance in self.providers.items():
                result[p_name] = p_instance.get_available_models()

            # Add models from config for providers not initialized
            for p_name, p_config in self.models_config.items():
                if p_name not in result:
                    result[p_name] = p_config.get("models", [])

        return result

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation context.

        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
        """
        self.context_manager.add_message(role, content)

    def clear_context(self) -> None:
        """Clear the conversation context."""
        self.context_manager.clear()

    def set_system_message(self, content: str) -> None:
        """
        Set the system message for the conversation.

        Args:
            content: System message content
        """
        self.system_prompt = content
        self.context_manager.set_system_message(content)

    def generate_response_async(self,
                          user_message: str,
                          on_complete: Callable[[str], None],
                          on_error: Callable[[str], None],
                          on_progress: Optional[Callable[[str], None]] = None,
                          provider: Optional[str] = None,
                          model: Optional[str] = None,
                          temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                          max_tokens: Optional[int] = None,
                          streaming: bool = False) -> None:
        """
        Generate a response asynchronously.

        Args:
            user_message: User message to respond to
            on_complete: Callback for when generation is complete
            on_error: Callback for when an error occurs
            on_progress: Callback for streaming progress updates
            provider: Provider to use, or None for default
            model: Model to use, or None for default
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            streaming: Whether to use streaming generation
        """
        # Add user message to context
        self.add_message("user", user_message)

        # Use default provider if not specified
        provider_name = provider or self.default_provider

        # Check if the provider is available
        if provider_name not in self.providers:
            error_msg = f"Provider '{provider_name}' not available"
            logger.error(error_msg)
            on_error(error_msg)
            return

        provider_instance = self.providers[provider_name]

        # Use default model if not specified
        if not model:
            model = provider_instance.get_default_model()
            if not model and provider_name in self.models_config:
                model = self.models_config[provider_name].get("default")

        # Use default temperature if not specified
        if temperature is None:
            temperature = self.temperature

        # Use default streaming setting if not specified
        if streaming is None:
            streaming = self.streaming

        # Check if streaming is supported
        if streaming and not provider_instance.supports_streaming:
            logger.warning(f"Provider '{provider_name}' does not support streaming, falling back to non-streaming")
            streaming = False

        # Create worker
        worker = LLMWorker(
            provider=provider_instance,
            messages=self.context_manager.get_messages(),
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            debug=self.debug
        )

        # Connect signals
        worker.signals.finished.connect(lambda response: self._handle_response(response, on_complete))
        worker.signals.error.connect(on_error)

        if streaming and on_progress:
            worker.signals.progress.connect(on_progress)

        if self.debug:
            worker.signals.debug.connect(logger.debug)

        # Start worker
        logger.info(f"Starting LLM request with provider '{provider_name}', model '{model}'")
        self.thread_pool.start(worker)

    def _handle_response(self, response: str, callback: Callable[[str], None]) -> None:
        """
        Handle a response from the LLM.

        Args:
            response: Response text
            callback: Callback function
        """
        # Add response to context if not empty (streaming responses will be empty)
        if response:
            self.add_message("assistant", response)

        # Call the callback
        callback(response)

    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the LLM configuration.

        Args:
            config: New configuration dictionary
        """
        self.config.update(config)

        # Update service parameters
        self.debug = self.config.get("debug", False)
        self.default_provider = self.config.get("default_provider", "gemini")
        self.temperature = self.config.get("temperature", DEFAULT_LLM_CONFIG['temperature'])
        self.streaming = self.config.get("streaming", True)

        # Update system prompt if it changed
        new_system_prompt = self.config.get("system_prompt")
        if new_system_prompt and new_system_prompt != self.system_prompt:
            self.set_system_message(new_system_prompt)

        # Update font size
        self.font_size = self.config.get("font_size", 16)

        logger.info("LLM service configuration updated")

    def get_key_file(self, provider):
        """
        Get the key file path for a provider.

        Args:
            provider: Provider name

        Returns:
            Key file path, or empty string if not set
        """
        return self.config.get(f"{provider}_keys_path", "")

    def set_key_file(self, provider, file_path):
        """
        Set the key file path for a provider.

        Args:
            provider: Provider name
            file_path: Key file path
        """
        self.config[f"{provider}_keys_path"] = file_path
        self.key_manager.load_keys_from_file(provider, file_path)

        # Reload provider if necessary
        # TODO: Implement provider reloading

    def get_system_prompt(self, prompt_key=None):
        """
        Get the system prompt.

        Args:
            prompt_key: Optional prompt key

        Returns:
            System prompt text
        """
        # TODO: Implement prompt templates if needed
        return self.system_prompt

    def set_system_prompt(self, prompt_key, prompt_text):
        """
        Set the system prompt.

        Args:
            prompt_key: Optional prompt key
            prompt_text: Prompt text
        """
        self.system_prompt = prompt_text
        self.context_manager.set_system_message(prompt_text)

    def save_config(self):
        """Save the LLM configuration."""
        # This needs to be implemented by the application using this service
        pass

    def reload_configuration(self, config=None):
        """
        Reload the LLM configuration.

        Args:
            config: New configuration dictionary
        """
        if config:
            self.update_config(config)

        # Reload keys
        self._load_provider_keys()

        # Reinitialize providers
        self._initialize_providers()
