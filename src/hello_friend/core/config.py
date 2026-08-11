"""
Application configuration.

Loads and validates environment variables from:
    - system environment
    - .env

Supports:

LLM:
    groq
    ollama
    nvidia

Input:
    text
    voice
    both

Output:
    text only

STT:
    NVIDIA Whisper Large V3
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # ==========================================================
    # LLM PROVIDER
    # ==========================================================

    llm_provider: str = Field(
        default="nvidia",
        description=(
            "LLM provider: "
            "groq, ollama, or nvidia"
        ),
    )

    # ==========================================================
    # GROQ
    # ==========================================================

    groq_api_key: str | None = Field(
        default=None,
        description="API key for Groq",
    )

    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model",
    )

    # ==========================================================
    # OLLAMA
    # ==========================================================

    ollama_model: str = Field(
        default="gpt-oss:20b",
        description="Local Ollama model",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL",
    )

    # ==========================================================
    # NVIDIA
    # ==========================================================

    nvidia_api_key: str | None = Field(
        default=None,
        description="NVIDIA NIM API key",
    )

    nvidia_model: str = Field(
        default="meta/llama-3.1-70b-instruct",
        description="NVIDIA LLM model",
    )

    # ==========================================================
    # COMMON LLM SETTINGS
    # ==========================================================

    llm_temperature: float = Field(
        default=0.4,
        ge=0.0,
        le=2.0,
    )

    llm_max_tokens: int = Field(
        default=1024,
        gt=0,
    )

    # ==========================================================
    # APPLICATION
    # ==========================================================

    app_name: str = Field(
        default="Hello Friend",
    )

    log_level: str = Field(
        default="INFO",
    )

    # ==========================================================
    # INPUT / OUTPUT
    # ==========================================================

    input_mode: str = Field(
        default="both",
        description=(
            "text, voice, or both"
        ),
    )

    output_mode: str = Field(
        default="text",
        description=(
            "Currently text only"
        ),
    )

    # ==========================================================
    # NVIDIA STT
    # ==========================================================

    stt_provider: str = Field(
        default="nvidia",
        description="Speech-to-text provider",
    )

    stt_model: str = Field(
        default="whisper-large-v3",
        description="NVIDIA Whisper model",
    )

    stt_language: str = Field(
        default="en",
        description=(
            "Language code. "
            "Use multi for automatic multilingual detection."
        ),
    )

    nvidia_stt_function_id: str = Field(
        default=(
            "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"
        ),
        description=(
            "NVIDIA Whisper Large V3 "
            "NVCF function ID"
        ),
    )

    nvidia_riva_server: str = Field(
        default="grpc.nvcf.nvidia.com:443",
        description="NVIDIA Riva server",
    )

    # ==========================================================
    # MICROPHONE
    # ==========================================================

    sample_rate: int = Field(
        default=16000,
        gt=0,
    )

    record_seconds: float = Field(
        default=5.0,
        gt=0,
    )

    # ==========================================================
    # PYDANTIC
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    # ==========================================================
    # MICROPHONE / VAD
    # ==========================================================

    sample_rate: int = Field(
        default=16000,
        gt=0,
    )

    min_record_seconds: float = Field(
        default=0.8,
        gt=0,
    )

    max_record_seconds: float = Field(
        default=30.0,
        gt=0,
    )

    silence_threshold: int = Field(
        default=500,
        ge=0,
    )

    silence_duration: float = Field(
        default=1.2,
        gt=0,
    )

    start_timeout: float = Field(
        default=10.0,
        gt=0,
    )    


@lru_cache
def get_settings() -> Settings:
    """
    Load settings once and reuse them.
    """

    return Settings()