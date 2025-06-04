"""
API key management for LLM providers.

This module handles loading, storing, and rotating API keys for various LLM providers.
It supports loading keys from JSON files and provides methods for retrieving keys for API requests.
"""

import json
import os
import random
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# # Set up logger
# logger = logging.getLogger(__name__)
# # Set debug level for this module
# logger.setLevel(logging.DEBUG)
from .colored_logging import setup_colored_logger
logger = setup_colored_logger(__name__)

# # Add a console handler if not already present
# if not logger.handlers:
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.DEBUG)
#     formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)


class APIKey:
    """Represents an API key with metadata."""

    def __init__(self, name: str, key: str, provider: str, **kwargs):
        """
        Initialize a new API key.

        Args:
            name: A descriptive name for the key
            key: The actual API key value
            provider: The provider this key is for (e.g., "gemini", "openai")
            **kwargs: Additional metadata for the key
        """
        self.name = name
        self.key = key
        self.provider = provider
        self.metadata = kwargs
        self.last_used = 0  # timestamp
        self.error_count = 0
        self.is_valid = True

    def mark_used(self):
        """Mark this key as used by updating its last_used timestamp."""
        self.last_used = time.time()

    def mark_error(self):
        """
        Mark that an error occurred with this key.

        Increments the error counter. Could be used for rate limiting or error tracking.
        """
        self.error_count += 1
        if self.error_count >= 5:  # Threshold for invalidating a key
            self.is_valid = False

    def reset_errors(self):
        """Reset the error counter for this key."""
        self.error_count = 0


class KeyManager:
    """Manages API keys for LLM providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new KeyManager instance.

        Args:
            config: Configuration dictionary with key paths
        """
        self.keys = {}  # provider -> list of APIKey objects
        self.config = config or {}

        # Get the list of providers dynamically from PROVIDER_MAP
        # Import PROVIDER_MAP to get all available providers
        # this is to prevent circular imports
        from .providers import PROVIDER_MAP
        self.known_providers = list(PROVIDER_MAP.keys())

        # Try to load keys for all known providers
        self._load_keys_from_config()

    def _load_keys_from_config(self):
        """Load keys from paths specified in the configuration."""
        logger.debug(f"Loading keys from config. Known providers: {self.known_providers}")
        logger.debug(f"Config contains keys: {[k for k in self.config.keys() if '_keys_path' in k]}")

        for provider in self.known_providers:
            path_key = f"{provider}_keys_path"

            # Get path from config if available
            key_path = self.config.get(path_key)
            logger.debug(f"For provider {provider}, config path key: {path_key}, path value: {key_path}")

            if key_path and os.path.exists(key_path):
                # logger.info(f"Loading {provider} keys from config path: {key_path}")
                self.load_keys_from_file(provider, key_path)
            else:
                # Fallback to default location
                user_profile = os.path.expanduser("~")
                provider_upper = provider.upper()
                if provider == "gemini":
                    provider_upper = "GOOGLE_GEMINI"

                json_path = os.path.join(user_profile, f"{provider_upper}_API_KEYS.json")
                logger.debug(f"Checking fallback path for {provider}: {json_path}")
                if os.path.exists(json_path):
                    logger.info(f"Loading {provider} keys from fallback path: {json_path}")
                    self.load_keys_from_file(provider, json_path)
                else:
                    logger.debug(f"No key file found for {provider} at {json_path}")

    def load_keys_from_file(self, provider: str, filepath: str) -> bool:
        """
        Load API keys from a JSON file.

        Args:
            provider: The provider name (e.g., "gemini", "openai")
            filepath: Path to the JSON file containing the keys

        Returns:
            True if keys were loaded successfully, False otherwise

        Note:
            The expected JSON format is either:
            1. A list of objects, each with at least "name" and "key" fields
            2. A simple object with an "api_key" field
        """
        try:
            # logger.debug(f"Attempting to load keys from file: {filepath}")
            with open(filepath, 'r') as f:
                key_data = json.load(f)

            # logger.debug(f"Loaded key data type: {type(key_data)}")

            # Case 1: List of key objects
            if isinstance(key_data, list):
                # logger.debug(f"Processing list of keys, count: {len(key_data)}")
                for item in key_data:
                    if "name" in item and "key" in item:
                        metadata = {k: v for k, v in item.items()
                                   if k not in ["name", "key"]}
                        key = APIKey(item["name"], item["key"], provider, **metadata)
                        self.add_key(provider, key)
                return True

            # Case 2: Simple object with api_key field
            elif isinstance(key_data, dict) and "api_key" in key_data:
                logger.debug(f"Processing single key object for {provider}")
                key = APIKey(f"{provider}-default", key_data["api_key"], provider)
                self.add_key(provider, key)
                return True

            else:
                logger.error(f"Invalid key file format for {provider}: {key_data}")
                return False
        except Exception as e:
            logger.error(f"Failed to load keys for {provider} from {filepath}: {e}")
            return False

    def add_key(self, provider: str, key: APIKey) -> None:
        """
        Add a new API key.

        Args:
            provider: The provider name
            key: The APIKey object to add
        """
        if provider not in self.keys:
            self.keys[provider] = []
        self.keys[provider].append(key)

    def get_random_key(self, provider: str) -> Optional[APIKey]:
        """
        Get a random valid API key for the specified provider.

        Args:
            provider: The provider name

        Returns:
            A random valid APIKey, or None if no valid keys are available
        """
        if provider not in self.keys or not self.keys[provider]:
            return None

        # Filter for valid keys
        valid_keys = [k for k in self.keys[provider] if k.is_valid]
        if not valid_keys:
            return None

        selected_key = random.choice(valid_keys)
        selected_key.mark_used()
        return selected_key

    def get_least_used_key(self, provider: str) -> Optional[APIKey]:
        """
        Get the least recently used valid API key.

        Args:
            provider: The provider name

        Returns:
            The least recently used valid APIKey, or None if no valid keys are available
        """
        if provider not in self.keys or not self.keys[provider]:
            return None

        # Filter for valid keys
        valid_keys = [k for k in self.keys[provider] if k.is_valid]
        if not valid_keys:
            return None

        selected_key = min(valid_keys, key=lambda k: k.last_used)
        selected_key.mark_used()
        return selected_key

    def get_key(self, provider: str) -> Optional[str]:
        """
        Get a key string for a provider (using random selection).

        Args:
            provider: The provider name

        Returns:
            The key string, or None if no valid keys are available
        """
        # Check environment variables first
        env_var = f"{provider.upper()}_API_KEY"
        if env_var in os.environ:
            logger.info(f"Using {provider} API key from environment variable")
            return os.environ[env_var]

        # Then try to get a key from our key store
        key_obj = self.get_random_key(provider)
        if key_obj:
            logger.info(f"Using {provider} API key: {key_obj.name}")
            return key_obj.key

        logger.warning(f"No valid API key found for {provider}")
        return None

    def has_valid_key(self, provider: str) -> bool:
        """
        Check if there's a valid key available for the provider.

        Args:
            provider: The provider name

        Returns:
            True if a valid key is available, False otherwise
        """
        # Check environment variables first
        env_var = f"{provider.upper()}_API_KEY"
        if env_var in os.environ:
            return True

        # Check if we have valid keys in our store
        return self.get_valid_key_count(provider) > 0

    def get_valid_key_count(self, provider: str) -> int:
        """
        Get the number of valid keys available for a provider.

        Args:
            provider: The provider name

        Returns:
            The number of valid keys for the provider
        """
        if provider not in self.keys:
            return 0
        return len([k for k in self.keys[provider] if k.is_valid])

    def add_key_from_string(self, provider: str, key_str: str, name: str = None) -> None:
        """
        Add a new API key from a string.

        Args:
            provider: The provider name
            key_str: The key string
            name: Optional name for the key
        """
        if not name:
            name = f"{provider}-{len(self.keys.get(provider, []))+1}"

        key = APIKey(name, key_str, provider)
        self.add_key(provider, key)

    def save_key_to_file(self, provider: str, key_str: str) -> bool:
        """
        Save a single API key to the default file location.

        Args:
            provider: The provider name
            key_str: The key string

        Returns:
            True if key was saved successfully, False otherwise
        """
        try:
            # Use config path if available
            path_key = f"{provider}_keys_path"
            filepath = self.config.get(path_key)

            # Otherwise use default location
            if not filepath:
                user_profile = os.path.expanduser("~")
                provider_upper = provider.upper()
                if provider == "gemini":
                    provider_upper = "GOOGLE_GEMINI"

                filepath = os.path.join(user_profile, f"{provider_upper}_API_KEYS.json")

            # Save as simple format with api_key field
            with open(filepath, 'w') as f:
                json.dump({"api_key": key_str}, f, indent=2)

            # Add to our key store
            self.add_key_from_string(provider, key_str)

            logger.info(f"Saved {provider} API key to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save key for {provider}: {e}")
            return False

    def get_available_providers(self) -> List[str]:
        """
        Get a list of providers with available keys.

        Returns:
            List of provider names
        """
        providers = []

        # Check environment variables
        for provider in self.known_providers:
            env_var = f"{provider.upper()}_API_KEY"
            if env_var in os.environ:
                logger.debug(f"Found environment variable for {provider}: {env_var}")
                providers.append(provider)
                continue

            # Check our key store
            valid_count = self.get_valid_key_count(provider)
            logger.debug(f"Provider {provider} has {valid_count} valid keys")
            if valid_count > 0:
                providers.append(provider)

        logger.info(f"Available providers: {providers}")
        return providers
