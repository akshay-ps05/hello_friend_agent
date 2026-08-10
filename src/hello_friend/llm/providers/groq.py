"""
Groq LLM provider.

Creates a LangChain ChatGroq model.
"""

from langchain_groq import ChatGroq

from hello_friend.core.config import Settings


def create_groq_model(settings: Settings) -> ChatGroq:
    """
    Create the configured Groq chat model.

    Groq is accessed through LangChain's ChatGroq integration so the
    agent can use the same interface as other providers.
    """

    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is required when LLM_PROVIDER=groq."
        )

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )