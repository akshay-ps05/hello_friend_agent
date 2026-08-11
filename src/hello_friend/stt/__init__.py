"""
Speech-to-text providers.
"""

from hello_friend.stt.nvidia import (
    NVIDIAWhisperSTT,
    STTError,
)


__all__ = [
    "NVIDIAWhisperSTT",
    "STTError",
]