"""
Wake detector.

Supports:

    hello friend
    friend

and:

    hello friend open youtube
    friend open google
    hello friend search youtube python

The input is always TEXT.

For voice:

    microphone
        ↓
    NVIDIA Whisper
        ↓
    text
        ↓
    this detector
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class WakeResult:
    woken: bool
    task: str = ""
    is_sleep: bool = False
    is_exit: bool = False


class WakeDetector:

    _WAKE_PATTERN = re.compile(
        r"""
        ^\s*
        (?:
            hello\s+friend
            |
            friend
        )
        (?:
            \s*[,.:;!-]\s*
            |
            \s+
            |
            $
        )
        (.*)
        $
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _SLEEP_PHRASES = {
        "go to sleep",
        "sleep",
        "sleep mode",
    }

    _EXIT_PHRASES = {
        "exit",
        "quit",
        ":q",
    }

    def check(
        self,
        text: str,
    ) -> WakeResult:

        text = text.strip()

        if not text:

            return WakeResult(
                woken=False
            )

        normalized = text.lower()

        # ------------------------------------------------------
        # EXIT
        # ------------------------------------------------------

        if normalized in self._EXIT_PHRASES:

            return WakeResult(
                woken=False,
                is_exit=True,
            )

        # ------------------------------------------------------
        # SLEEP
        # ------------------------------------------------------

        if normalized in self._SLEEP_PHRASES:

            return WakeResult(
                woken=False,
                is_sleep=True,
            )

        # ------------------------------------------------------
        # WAKE / WAKE + COMMAND
        # ------------------------------------------------------

        match = self._WAKE_PATTERN.match(
            text
        )

        if not match:

            return WakeResult(
                woken=False
            )

        task = match.group(1).strip()

        return WakeResult(
            woken=True,
            task=task,
        )