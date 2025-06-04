"""
Hugging Face API provider implementation.

This module provides integration with Hugging Face Inference API for LLM functionality
using the huggingface_hub library.
"""

from typing import List, Dict, Any, Optional, Callable

from huggingface_hub import AsyncInferenceClient, InferenceTimeoutError

from ..base import LLMProvider, LLMMessage
from ..key_manager import KeyManager
from ..config import get_llm_config, DEFAULT_LLM_CONFIG

class HuggingFaceApiError(Exception):
    """Exception raised for Hugging Face API errors."""


class ModelNotCompatibleError(HuggingFaceApiError):
    """Error raised when a model is not compatible with the requested endpoint."""


class HuggingFaceProvider(LLMProvider):
    """Hugging Face API implementation using huggingface_hub."""

    validModels = [
        "Qwen/Qwen2.5-Coder-32B-Instruct", # https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct
        "Qwen/Qwen2.5-Coder-7B-Instruct", # https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct
        "m-a-p/OpenCodeInterpreter-DS-33B", # https://huggingface.co/m-a-p/OpenCodeInterpreter-DS-33B
        "NTQAI/Nxcode-CQ-7B-orpo", # https://huggingface.co/NTQAI/Nxcode-CQ-7B-orpo
        "mistralai/Codestral-22B-v0.1", # https://huggingface.co/mistralai/Codestral-22B-v0.1
        # https://huggingface.co/deepseek-ai/deepseek-coder-33b-instruct
        "deepseek-ai/DeepSeek-V2.5-1210", # https://huggingface.co/deepseek-ai/DeepSeek-V2.5-1210
        "deepseek-coder-33b-instruct",
        # https://huggingface.co/deepseek-ai/DeepSeek-V2
        # https://huggingface.co/deepseek-ai/DeepSeek-V2.5-1210
        # https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Base
        # https://huggingface.co/deepseek-ai/deepseek-llm-67b-base
        # https://huggingface.co/deepseek-ai/DeepSeek-V2-Chat-0628
        # https://huggingface.co/deepseek-ai/DeepSeek-V3
        # https://huggingface.co/deepseek-ai/DeepSeek-V3-Base

        # https://lmarena.ai/?leaderboard
        "Nexusflow/Athene-V2-Chat", # https://huggingface.co/Nexusflow/Athene-V2-Chat
        # https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard#/
        "MaziyarPanahi/calme-3.2-instruct-78b", # https://huggingface.co/MaziyarPanahi/calme-3.2-instruct-78b
        "dfurman/CalmeRys-78B-Orpo-v0.1", # https://huggingface.co/dfurman/CalmeRys-78B-Orpo-v0.1
    ]

    # https://huggingface.co/models?other=vision
    # https://huggingface.co/spaces/opencompass/open_vlm_leaderboard
    validVisionModels = [
        "OpenGVLab/InternVL2_5-78B", # https://huggingface.co/OpenGVLab/InternVL2_5-78B
        "Qwen/Qwen2-VL-72B-Instruct", # https://huggingface.co/Qwen/Qwen2-VL-72B-Instruct
        "OpenGVLab/InternVL2_5-38B", # https://huggingface.co/OpenGVLab/InternVL2_5-38B
        # https://huggingface.co/OpenGVLab/InternVL2_5-26B
        # https://huggingface.co/01-ai/Yi-VL-34B
    ]

    # https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending
    validImageGenerationModels = [
        "stabilityai/stable-diffusion-2",
        "black-forest-labs/FLUX.1-dev", # https://huggingface.co/black-forest-labs/FLUX.1-dev
    ];


    def __init__(self, key_manager: KeyManager = None):
        """
        Initialize the Hugging Face provider.

        Args:
            key_manager: KeyManager instance for API key management
        """
        self.key_manager = key_manager or KeyManager(get_llm_config())
        self.default_model = self.validModels[0]
        self.timeout = 60  # Default timeout in seconds

    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Gemini supports streaming
        """
        return True

    @property
    def provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            The provider name as a string
        """
        return "huggingface"

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for this provider.

        Returns:
            List of model identifiers
        """
        return self.validModels

    @property
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.

        Returns:
            True as Hugging Face supports streaming
        """
        return True

    async def generate_response(self,
                       messages: List[LLMMessage],
                       model: Optional[str] = None,
                       temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                       max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the Hugging Face API.

        Args:
            messages: List of messages in the conversation
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text response

        Raises:
            ValueError: If no API key is available
            HuggingFaceApiError: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("huggingface")

        if not api_key:
            raise ValueError("No API key available for Hugging Face")

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Initialize the client
            client = AsyncInferenceClient(
                token=api_key.key,
                timeout=self.timeout
            )

            # Set parameters
            parameters = {
                "temperature": temperature,
            }

            if max_tokens:
                parameters["max_new_tokens"] = max_tokens

            # Try the direct chat_completion method first
            try:
                # Use text_generation instead as that's more widely supported
                prompt = self._convert_messages_to_prompt(formatted_messages)
                response = await client.text_generation(
                    prompt,
                    model=model,
                    **parameters
                )

                api_key.mark_used()
                return response

            except Exception as api_err:
                # Fallback to chat_completion if text_generation fails
                try:
                    response = await client.chat_completion(
                        model=model,
                        messages=formatted_messages,
                        **parameters
                    )

                    api_key.mark_used()

                    # Carefully extract generated content from response with null checks
                    if (response is not None and
                        hasattr(response, "choices") and
                        response.choices is not None and
                        len(response.choices) > 0 and
                        response.choices[0] is not None and
                        hasattr(response.choices[0], "message") and
                        response.choices[0].message is not None and
                        hasattr(response.choices[0].message, "content") and
                        response.choices[0].message.content is not None):
                        return response.choices[0].message.content

                    # Fallback in case the response format is different
                    return str(response) if response is not None else "No response received"

                except Exception as chat_err:
                    raise ModelNotCompatibleError(
                        f"Model {model} is not compatible with either text_generation or chat_completion: {str(chat_err)}"
                    ) from chat_err

        except InferenceTimeoutError as exc:
            api_key.mark_error()
            raise HuggingFaceApiError(
                f"Hugging Face API timeout after {self.timeout} seconds"
            ) from exc
        except Exception as e:
            api_key.mark_error()
            raise HuggingFaceApiError(f"Hugging Face API error: {str(e)}") from e

    async def generate_response_streaming(self,
                                 messages: List[LLMMessage],
                                 callback: Callable[[str], None],
                                 model: Optional[str] = None,
                                 temperature: float = DEFAULT_LLM_CONFIG['temperature'],
                                 max_tokens: Optional[int] = None) -> None:
        """
        Generate a streaming response from the Hugging Face API.

        Args:
            messages: List of messages in the conversation
            callback: Function to call for each chunk of the response
            model: Name of the model to use
            temperature: Temperature parameter for generation (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Raises:
            ValueError: If no API key is available
            HuggingFaceApiError: On API errors or other issues
        """
        model = model or self.default_model
        api_key = self.key_manager.get_random_key("huggingface")

        if not api_key:
            raise ValueError("No API key available for Hugging Face")

        # Format messages for API
        formatted_messages = self._format_messages_for_api(messages)

        try:
            # Initialize the client
            client = AsyncInferenceClient(
                token=api_key.key,
                timeout=self.timeout
            )

            # Set parameters
            parameters = {
                "temperature": temperature,
            }

            stream_params = parameters.copy()
            stream_params["stream"] = True

            if max_tokens:
                parameters["max_new_tokens"] = max_tokens
                stream_params["max_new_tokens"] = max_tokens

            # Try text_generation with streaming first (more widely supported)
            try:
                # Convert messages to text prompt
                prompt = self._convert_messages_to_prompt(formatted_messages)

                # Use text generation with streaming
                text_gen = await client.text_generation(
                    prompt,
                    model=model,
                    **stream_params
                )

                api_key.mark_used()
                async for text in text_gen:
                    if text is not None:
                        callback(text)
                return

            except Exception as text_gen_err:
                # Fallback to chat_completion if text_generation fails
                try:
                    stream = await client.chat_completion(
                        model=model,
                        messages=formatted_messages,
                        **stream_params
                    )

                    api_key.mark_used()

                    # Process streaming response with careful null checks
                    async for chunk in stream:
                        if (chunk is not None and
                            hasattr(chunk, "choices") and
                            chunk.choices is not None and
                            len(chunk.choices) > 0 and
                            chunk.choices[0] is not None and
                            hasattr(chunk.choices[0], "delta") and
                            chunk.choices[0].delta is not None and
                            hasattr(chunk.choices[0].delta, "content") and
                            chunk.choices[0].delta.content is not None):
                            content = chunk.choices[0].delta.content
                            if content:
                                callback(content)
                except Exception as chat_err:
                    raise ModelNotCompatibleError(
                        f"Model {model} is not compatible with either text_generation or chat_completion streaming: {str(chat_err)}"
                    ) from chat_err

        except InferenceTimeoutError as exc:
            api_key.mark_error()
            raise HuggingFaceApiError(
                f"Hugging Face API timeout after {self.timeout} seconds"
            ) from exc
        except Exception as e:
            api_key.mark_error()
            raise HuggingFaceApiError(f"Hugging Face API error: {str(e)}") from e

    def _format_messages_for_api(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for the API.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Formatted messages for the API request
        """
        formatted_messages = []
        for msg in messages:
            if msg is not None and hasattr(msg, "role") and hasattr(msg, "content"):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        return formatted_messages

    def _convert_messages_to_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Convert formatted messages to a text prompt for text_generation.

        Args:
            messages: List of formatted message dictionaries

        Returns:
            Text prompt
        """
        prompt = ""
        for msg in messages:
            if msg is None:
                continue

            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                prompt += f"<|system|>\n{content}\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n"

        # Add assistant prefix for the response
        prompt += "<|assistant|>\n"

        return prompt
