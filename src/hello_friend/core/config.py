"""
Application configuration.

Uses pydantic-settings to load and validate environment variables
from the environment and .env file.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------
    # LLM provider
    # ------------------------------------------------------------------

    llm_provider: str = Field(
        default="groq",
        description="LLM provider: groq, ollama, or nvidia",
    )

    # ------------------------------------------------------------------
    # Groq
    # ------------------------------------------------------------------

    groq_api_key: str | None = Field(
        default=None,
        description="API key for Groq",
    )

    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model id used by LangChain ChatGroq",
    )

    # ------------------------------------------------------------------
    # Ollama
    # ------------------------------------------------------------------

    ollama_model: str = Field(
        default="gpt-oss:20b",
        description="Local Ollama model name",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )

    # ------------------------------------------------------------------
    # NVIDIA
    # ------------------------------------------------------------------

    nvidia_api_key: str | None = Field(
        default=None,
        description="API key for NVIDIA NIM",
    )

    nvidia_model: str = Field(
        default="meta/llama-3.1-70b-instruct",
        description="NVIDIA model id",
    )

    # ------------------------------------------------------------------
    # Common LLM settings
    # ------------------------------------------------------------------

    llm_temperature: float = Field(
        default=0.4,
        ge=0.0,
        le=2.0,
    )

    llm_max_tokens: int = Field(
        default=1024,
        gt=0,
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = Field(
        default="Hello Friend",
    )

    log_level: str = Field(
        default="INFO",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Load settings once and reuse the same Settings instance.
    """
    return Settings()