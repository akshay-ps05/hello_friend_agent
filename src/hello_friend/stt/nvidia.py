"""
NVIDIA Whisper Large V3 Speech-to-Text.

Flow:

    microphone
        ↓
    numpy audio
        ↓
    WAV
        ↓
    NVIDIA Riva / NIM
        ↓
    transcript
"""

from __future__ import annotations

import logging
import tempfile
import wave
from pathlib import Path

import numpy as np


logger = logging.getLogger(__name__)


class STTError(RuntimeError):
    """Speech-to-text failure."""


class NVIDIAWhisperSTT:
    """
    NVIDIA Whisper Large V3 client.

    Uses NVIDIA Riva hosted gRPC endpoint.
    """

    def __init__(
        self,
        api_key: str,
        function_id: str,
        server: str = "grpc.nvcf.nvidia.com:443",
        model: str = "whisper-large-v3",
        language: str = "en",
        sample_rate: int = 16000,
    ) -> None:

        if not api_key:
            raise STTError(
                "NVIDIA_API_KEY is missing."
            )

        self._api_key = api_key
        self._function_id = function_id
        self._server = server
        self._model = model
        self._language = language
        self._sample_rate = sample_rate

    # ==========================================================
    # TRANSCRIBE
    # ==========================================================

    def transcribe(
        self,
        audio: np.ndarray,
    ) -> str:
        """
        Transcribe microphone audio using NVIDIA Whisper.
        """

        if audio.size == 0:
            return ""

        wav_path: Path | None = None

        try:

            # ==================================================
            # CREATE TEMP WAV
            # ==================================================

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False,
            ) as tmp:

                wav_path = Path(tmp.name)

            with wave.open(
                str(wav_path),
                "wb",
            ) as wav_file:

                wav_file.setnchannels(1)

                wav_file.setsampwidth(2)

                wav_file.setframerate(
                    self._sample_rate
                )

                wav_file.writeframes(
                    audio.astype(
                        np.int16
                    ).tobytes()
                )

            logger.info(
                "Audio prepared: %s",
                wav_path,
            )

            # ==================================================
            # IMPORT NVIDIA RIVA
            # ==================================================

            try:

                import riva.client

            except ImportError as exc:

                raise STTError(
                    "nvidia-riva-client is not installed.\n"
                    "Run:\n"
                    "pip install -U nvidia-riva-client"
                ) from exc

            # ==================================================
            # NVIDIA AUTH
            # ==================================================

            logger.info(
                "Connecting to NVIDIA Riva: %s",
                self._server,
            )

            auth = riva.client.Auth(
                use_ssl=True,

                uri=self._server,

                metadata_args=[
                    (
                        "function-id",
                        self._function_id,
                    ),
                    (
                        "authorization",
                        f"Bearer {self._api_key}",
                    ),
                ],
            )

            # ==================================================
            # ASR SERVICE
            # ==================================================

            asr_service = (
                riva.client.ASRService(
                    auth
                )
            )

            # ==================================================
            # READ AUDIO
            # ==================================================

            with open(
                wav_path,
                "rb",
            ) as audio_file:

                audio_data = (
                    audio_file.read()
                )

            logger.info(
                "Sending %.2f KB to NVIDIA STT...",
                len(audio_data) / 1024,
            )

            # ==================================================
            # RECOGNITION CONFIG
            # ==================================================

            config = riva.client.RecognitionConfig(
                language_code=self._language,

                max_alternatives=1,

                enable_automatic_punctuation=True,

                verbatim_transcripts=True,
            )

            # ==================================================
            # NVIDIA OFFLINE RECOGNITION
            # ==================================================

            response = (
                asr_service.offline_recognize(
                    audio_data,
                    config,
                )
            )

            # ==================================================
            # EXTRACT TRANSCRIPT
            # ==================================================

            transcripts: list[str] = []

            for result in response.results:

                if not result.alternatives:
                    continue

                transcript = (
                    result
                    .alternatives[0]
                    .transcript
                    .strip()
                )

                if transcript:

                    transcripts.append(
                        transcript
                    )

            text = " ".join(
                transcripts
            ).strip()

            logger.info(
                "NVIDIA transcript: %r",
                text,
            )

            return text

        # ======================================================
        # KNOWN STT ERROR
        # ======================================================

        except STTError:

            raise

        # ======================================================
        # NVIDIA / RIVA ERROR
        # ======================================================

        except Exception as exc:

            logger.exception(
                "NVIDIA STT request failed."
            )

            # IMPORTANT:
            # Don't hide the real exception anymore.

            raise STTError(
                "NVIDIA speech recognition failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        # ======================================================
        # CLEANUP
        # ======================================================

        finally:

            if wav_path is not None:

                wav_path.unlink(
                    missing_ok=True
                )