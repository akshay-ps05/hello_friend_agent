"""
Voice input.

Flow:

    microphone
        ↓
    wait for speech
        ↓
    record continuously
        ↓
    detect silence
        ↓
    stop recording
        ↓
    NVIDIA Whisper
        ↓
    text

There is no fixed 5-second recording limit.

A safety MAX_RECORD_SECONDS is used to prevent
an accidentally open microphone from recording forever.
"""

from __future__ import annotations

import logging
import time

import numpy as np

from hello_friend.stt.nvidia import (
    NVIDIAWhisperSTT,
)


logger = logging.getLogger(__name__)


class VoiceInterface:

    def __init__(
        self,
        stt: NVIDIAWhisperSTT,
        sample_rate: int = 16000,
        min_record_seconds: float = 0.8,
        max_record_seconds: float = 30.0,
        silence_threshold: int = 500,
        silence_duration: float = 1.2,
        start_timeout: float = 10.0,
    ) -> None:

        self._stt = stt

        self._sample_rate = sample_rate

        self._min_record_seconds = (
            min_record_seconds
        )

        self._max_record_seconds = (
            max_record_seconds
        )

        self._silence_threshold = (
            silence_threshold
        )

        self._silence_duration = (
            silence_duration
        )

        self._start_timeout = (
            start_timeout
        )

    # ==========================================================
    # RECORD UNTIL SILENCE
    # ==========================================================

    def record(self) -> np.ndarray:
        """
        Record until the user stops speaking.

        Uses simple RMS-based silence detection.

        No fixed 5-second recording.
        """

        try:

            import sounddevice as sd

        except ImportError as exc:

            raise RuntimeError(
                "sounddevice is required.\n"
                "Install with:\n"
                "pip install sounddevice"
            ) from exc

        block_duration = 0.1

        block_size = int(
            self._sample_rate
            * block_duration
        )

        max_blocks = int(
            self._max_record_seconds
            / block_duration
        )

        min_blocks = int(
            self._min_record_seconds
            / block_duration
        )

        silence_blocks_required = max(
            1,
            int(
                self._silence_duration
                / block_duration
            ),
        )

        logger.info(
            "Listening for speech..."
        )

        frames: list[np.ndarray] = []

        speech_started = False

        silence_blocks = 0

        start_time = time.monotonic()

        # ------------------------------------------------------
        # Open microphone stream
        # ------------------------------------------------------

        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype="int16",
            blocksize=block_size,
        ) as stream:

            for block_number in range(
                max_blocks
            ):

                audio_block, _ = (
                    stream.read(
                        block_size
                    )
                )

                audio = (
                    audio_block
                    .reshape(-1)
                    .copy()
                )

                frames.append(audio)

                # --------------------------------------------------
                # RMS volume
                # --------------------------------------------------

                rms = float(
                    np.sqrt(
                        np.mean(
                            audio.astype(
                                np.float32
                            )
                            ** 2
                        )
                    )
                )

                is_speech = (
                    rms
                    >= self._silence_threshold
                )

                # --------------------------------------------------
                # Speech started
                # --------------------------------------------------

                if is_speech:

                    speech_started = True

                    silence_blocks = 0

                    logger.debug(
                        "Speech detected. RMS=%.1f",
                        rms,
                    )

                    continue

                # --------------------------------------------------
                # No speech yet
                # --------------------------------------------------

                if not speech_started:

                    elapsed = (
                        time.monotonic()
                        - start_time
                    )

                    if (
                        elapsed
                        >= self._start_timeout
                    ):

                        logger.info(
                            "No speech detected."
                        )

                        return np.array(
                            [],
                            dtype=np.int16,
                        )

                    continue

                # --------------------------------------------------
                # Speech already started:
                # count silence
                # --------------------------------------------------

                silence_blocks += 1

                total_blocks = (
                    block_number + 1
                )

                # Don't stop too early.
                if (
                    total_blocks
                    < min_blocks
                ):

                    continue

                # --------------------------------------------------
                # User finished speaking
                # --------------------------------------------------

                if (
                    silence_blocks
                    >= silence_blocks_required
                ):

                    logger.info(
                        "Speech ended after "
                        "%.2f seconds.",
                        total_blocks
                        * block_duration,
                    )

                    break

        # ======================================================
        # COMBINE AUDIO
        # ======================================================

        if not frames:

            return np.array(
                [],
                dtype=np.int16,
            )

        audio = np.concatenate(
            frames
        )

        logger.info(
            "Recorded %.2f seconds.",
            len(audio)
            / self._sample_rate,
        )

        return audio

    # ==========================================================
    # LISTEN
    # ==========================================================

    def listen(self) -> str:
        """
        Record speech and send it to NVIDIA Whisper.
        """

        audio = self.record()

        if audio.size == 0:

            return ""

        return self._stt.transcribe(
            audio
        )