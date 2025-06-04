"""
LLM configuration utilities.

This module provides functions for managing LLM-specific configuration
within the larger application configuration system.
"""

import os

from typing import Dict, Any, Optional
from .default_llm_config import DEFAULT_LLM_CONFIG

def get_default_config() -> Dict[str, Any]:
    """
    Get the default LLM configuration.

    Returns:
        Default configuration dictionary
    """
    return DEFAULT_LLM_CONFIG.copy()


def get_llm_config(app_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract LLM-specific configuration from application config.

    Args:
        app_config: Application configuration dictionary

    Returns:
        LLM configuration dictionary
    """
    llm_config = get_default_config()

    # Override defaults with values from app config
    if app_config and "llm" in app_config:
        llm_config.update(app_config["llm"])

    return llm_config


def load_models_config() -> Dict[str, Dict[str, Any]]:
    """
    Load models configuration for LLM providers.

    Returns:
        Dictionary mapping provider names to model configuration
    """
    return {
        "openai": {
            "default": "gpt-3.5-turbo",
            "models": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ]
        },
        "anthropic": {
            "default": "claude-3-sonnet-20240229",
            "models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        },
        "gemini": {
            "default": "gemini-2.0-flash-exp",
            "models": [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]
        },
        "groq": {
            "default": "llama3-8b-8192",
            "models": [
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768"
            ]
        }
    }


def update_llm_config(app_config: Dict[str, Any], llm_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update LLM configuration in application config.

    Args:
        app_config: Application configuration dictionary
        llm_config: LLM configuration to update

    Returns:
        Updated application configuration
    """
    if "llm" not in app_config:
        app_config["llm"] = {}

    app_config["llm"].update(llm_config)
    return app_config


def get_system_prompt(app_config: Dict[str, Any], prompt_key: str) -> str:
    """
    Get a system prompt by key.

    Args:
        app_config: Application configuration dictionary
        prompt_key: Key of the prompt to retrieve

    Returns:
        System prompt string, or default prompt if key not found
    """
    llm_config = get_llm_config(app_config)
    prompts = llm_config.get("system_prompts", {})
    return prompts.get(prompt_key, prompts.get("default", DEFAULT_LLM_CONFIG["system_prompts"]["default"]))


def validate_api_key_paths(llm_config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate that API key files exist.

    Args:
        llm_config: LLM configuration dictionary

    Returns:
        Dictionary mapping provider names to boolean indicating if key file exists
    """
    result = {}

    # Extract all provider key paths from config
    provider_keys = {}
    for key in llm_config:
        if key.endswith("_keys_path"):
            provider_name = key[:-10]  # Remove "_keys_path"
            provider_keys[provider_name] = key

    # Check all provider keys
    for provider, config_key in provider_keys.items():
        key_path = llm_config.get(config_key, "")
        result[provider] = bool(key_path and os.path.exists(key_path))

    return result
