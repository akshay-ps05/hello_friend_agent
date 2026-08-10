"""
NVIDIA NIM LLM provider.

Creates a LangChain ChatNVIDIA model.
"""

from langchain_nvidia_ai_endpoints import ChatNVIDIA

from hello_friend.core.config import Settings


def create_nvidia_model(settings: Settings) -> ChatNVIDIA:
    """
    Create the configured NVIDIA NIM chat model.
    """

    if not settings.nvidia_api_key:
        raise ValueError(
            "NVIDIA_API_KEY is required when LLM_PROVIDER=nvidia."
        )

    return ChatNVIDIA(
        model=settings.nvidia_model,
        api_key=settings.nvidia_api_key,
        temperature=settings.llm_temperature,
    )