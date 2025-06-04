"""
LLM Integration Module.

This module provides functions for integrating LLM features with the main application.
"""

import logging
import os
from typing import Dict, Any, Optional, List

from .service import LLMService
from .key_manager import KeyManager
from .config import get_llm_config, load_models_config

# Set up logger
logger = logging.getLogger(__name__)

# Global LLM service instance
_llm_service: Optional[LLMService] = None


def initialize_llm(config_override: Optional[Dict[str, Any]] = None) -> LLMService:
    """
    Initialize the LLM service.

    This function initializes the LLM service with the given configuration.
    If no configuration is provided, the default configuration is used.

    Args:
        config_override: Optional configuration to override the default

    Returns:
        Initialized LLMService
    """
    global _llm_service

    try:
        # Load the configuration
        config = get_llm_config()

        # Override with provided config if any
        if config_override:
            config.update(config_override)

        # Create the LLM service
        _llm_service = LLMService(config)
        logger.info("LLM service initialized successfully")

        return _llm_service
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {str(e)}")
        raise


def get_llm_service() -> LLMService:
    """
    Get the LLM service.

    Returns:
        LLM service instance

    Raises:
        RuntimeError: If the LLM service has not been initialized
    """
    global _llm_service

    if _llm_service is None:
        # Try to initialize the service with default config
        return initialize_llm()

    return _llm_service


def integrate_llm_features(app: Any) -> None:
    """
    Integrate LLM features with the main application.

    This function adds LLM-related menus, dialogs, and commands to the application.

    Args:
        app: The main application instance
    """
    # This is just a placeholder for integration with the main app
    # In a real application, this would add menus, commands, etc.
    logger.info("Integrating LLM features with the application")

    try:
        # Initialize the LLM service if not already done
        llm_service = get_llm_service()

        # Add application-specific integration here
        # For example, adding a chat panel to the UI
        if hasattr(app, 'add_chat_panel'):
            app.add_chat_panel(llm_service)

        # Or adding commands to the command palette
        if hasattr(app, 'register_command'):
            app.register_command('llm.send_message', "Send a message to the LLM")
            app.register_command('llm.clear_conversation', "Clear the current conversation")
            app.register_command('llm.switch_provider', "Switch the LLM provider")

        logger.info("LLM features integrated successfully")
    except Exception as e:
        logger.error(f"Failed to integrate LLM features: {str(e)}")
        # Don't raise, just log the error to avoid crashing the application
        # The application should be able to function without LLM features

def get_model_info(service: LLMService) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get information about available models.

    Args:
        service: LLM service instance

    Returns:
        Dictionary of provider -> list of model info dictionaries
    """
    result = {}

    try:
        for provider_name in service.get_available_providers():
            provider = service.get_provider(provider_name)
            if not provider:
                continue

            model_list = []
            for model_name in provider.get_available_models():
                if model_name in provider.models:
                    model_info = provider.models[model_name].copy()
                    model_info["name"] = model_name
                    model_list.append(model_info)
                else:
                    model_list.append({
                        "name": model_name,
                        "description": f"Model {model_name}",
                        "max_tokens": 2048,
                        "max_input_tokens": 8192
                    })

            result[provider_name] = model_list
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")

    return result

def set_default_system_prompt(service: LLMService, prompt: str) -> bool:
    """
    Set the default system prompt.

    Args:
        service: LLM service instance
        prompt: System prompt text

    Returns:
        True if successful, False otherwise
    """
    try:
        service.set_system_message(prompt)
        return True
    except Exception as e:
        logger.error(f"Error setting system prompt: {str(e)}")
        return False

def test_api_key(provider: str, api_key: str) -> Dict[str, Any]:
    """
    Test if an API key is valid.

    Args:
        provider: Provider name
        api_key: API key to test

    Returns:
        Dictionary with test result
    """
    from .provider import create_provider

    result = {
        "valid": False,
        "error": None,
        "provider": provider,
        "models": []
    }

    try:
        # Create provider with the API key
        provider_instance = create_provider(provider, api_key)

        # Try to get available models - this will typically fail if the API key is invalid
        models = provider_instance.get_available_models()

        # If we get here, the key is probably valid
        result["valid"] = True
        result["models"] = models
    except Exception as e:
        result["error"] = str(e)

    return result
