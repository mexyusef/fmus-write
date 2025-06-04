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

# Map of provider names to their classes
PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "cerebras": CerebrasProvider,
    "hyperbolic": HyperbolicProvider,
    "together": TogetherProvider,
    "sambanova": SambanovaProvider,
    "glhf": GLHFProvider,
    "huggingface": HuggingFaceProvider,
    "cohere": CohereProvider,
    "groq": GroqProvider
}