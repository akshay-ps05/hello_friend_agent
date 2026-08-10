"""
LLM model factory.

Selects the configured LangChain chat model.

Supported providers:
    groq
    ollama
    nvidia
"""

from typing import Any

from hello_friend.core.config import Settings
from hello_friend.llm.providers import (
    create_groq_model,
    create_nvidia_model,
    create_ollama_model,
)


def create_model(settings: Settings) -> Any:
    """
    Create the LangChain chat model configured in Settings.
    """

    provider = settings.llm_provider.strip().lower()

    if provider == "groq":
        return create_groq_model(settings)

    if provider == "ollama":
        return create_ollama_model(settings)

    if provider == "nvidia":
        return create_nvidia_model(settings)

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider!r}. "
        "Supported providers: groq, ollama, nvidia."
    )