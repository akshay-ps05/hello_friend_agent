"""
Ollama LLM provider.

Creates a local LangChain ChatOllama model.
"""

from langchain_ollama import ChatOllama

from hello_friend.core.config import Settings


def create_ollama_model(settings: Settings) -> ChatOllama:
    """
    Create the configured local Ollama chat model.
    """

    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.llm_temperature,
    )