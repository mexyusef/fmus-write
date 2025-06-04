"""
LLM Providers package.

This package contains implementations of various LLM providers.
"""
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .cerebras import CerebrasProvider
from .hyperbolic import HyperbolicProvider
from .together import TogetherProvider
from .sambanova import SambanovaProvider
from .glhf import GLHFProvider
from .huggingface import HuggingFaceProvider
from .cohere import CohereProvider
from .groq import GroqProvider

from .provider_map import PROVIDER_MAP

def get_provider_class(provider_name: str):
    """
    Get the provider class for a given provider name.

    Args:
        provider_name: Name of the provider

    Returns:
        Provider class or None if not found
    """
    return PROVIDER_MAP.get(provider_name.lower())

__all__ = [
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "CerebrasProvider",
    "HyperbolicProvider",
    "TogetherProvider",
    "SambanovaProvider",
    "GLHFProvider",
    "HuggingFaceProvider",
    "CohereProvider",
    "GroqProvider",
    "get_provider_class",
    "PROVIDER_MAP"
]
