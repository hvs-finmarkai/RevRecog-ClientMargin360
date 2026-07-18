import os

from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


def get_llm_provider() -> LLMProvider:
    provider_name = os.environ.get("AI_PROVIDER", "ollama").lower().strip()
    provider_class = PROVIDERS.get(provider_name)
    if provider_class is None:
        available = ", ".join(sorted(PROVIDERS.keys()))
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. Available providers: {available}"
        )
    return provider_class()
