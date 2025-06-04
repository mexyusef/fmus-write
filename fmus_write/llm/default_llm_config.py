from pathlib import Path
# Default configuration for LLM features
DEFAULT_LLM_CONFIG = {
    "enabled": True,

    "default_provider": "gemini",
    "temperature": 0.2,
    "streaming": False,
    "max_context_bytes": 10240,  # 10KB

    "gemini_keys_path": str(Path.home() / "GOOGLE_GEMINI_API_KEYS.json"),
    "groq_keys_path": str(Path.home() / "GROQ_API_KEYS.json"),
    "openai_keys_path": str(Path.home() / "OPENAI_API_KEYS.json"),
    "anthropic_keys_path": str(Path.home() / "ANTHROPIC_API_KEYS.json"),
    "cohere_keys_path": str(Path.home() / "COHERE_API_KEYS.json"),
    "cerebras_keys_path": str(Path.home() / "CEREBRAS_API_KEYS.json"),
    "falai_keys_path": str(Path.home() / "FALAI_API_KEYS.json"),
    "fireworks_keys_path": str(Path.home() / "FIREWORKS_API_KEYS.json"),
    "glhf_keys_path": str(Path.home() / "GLHF_API_KEYS.json"),
    "huggingface_keys_path": str(Path.home() / "HUGGINGFACE_API_KEYS.json"),
    "hyperbolic_keys_path": str(Path.home() / "HYPERBOLIC_API_KEYS.json"),
    "sambanova_keys_path": str(Path.home() / "SAMBANOVA_API_KEYS.json"),
    "together_keys_path": str(Path.home() / "TOGETHER_API_KEYS.json"),

    "system_prompts": {
        "default": "You are a helpful coding assistant. Your responses support Markdown formatting, including code blocks with syntax highlighting, tables, and other formatting elements.",
        "explain": "Explain the following code clearly and concisely. Use Markdown formatting with syntax-highlighted code blocks where appropriate:",
        "fix": "Find and fix issues in the following code. Explain what was wrong and how you fixed it using Markdown formatting:",
        "optimize": "Optimize the following code for better performance. Explain your optimizations using Markdown formatting with code blocks:"
    }
}
