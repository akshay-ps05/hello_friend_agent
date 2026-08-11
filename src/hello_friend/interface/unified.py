"""
Unified interaction layer.

Text and voice use exactly the same state machine.

TEXT:

    hello friend
        ↓
    wake

    hello friend open youtube
        ↓
    wake + task
        ↓
    AgentRunner


VOICE:

    microphone
        ↓
    NVIDIA Whisper
        ↓
    "hello friend"
        ↓
    wake

    microphone
        ↓
    NVIDIA Whisper
        ↓
    "open youtube"
        ↓
    AgentRunner

VOICE ONE-LINE:

    microphone
        ↓
    NVIDIA Whisper
        ↓
    "hello friend open youtube"
        ↓
    WakeDetector
        ↓
    task = "open youtube"
        ↓
    AgentRunner

Output is TEXT only.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from hello_friend.agent.graph import AgentRunner
from hello_friend.interface.voice import VoiceInterface
from hello_friend.interface.wake import WakeDetector


logger = logging.getLogger(
    __name__
)


WAKE_MESSAGE = (
    "Yes, I'm listening."
)

SLEEP_MESSAGE = (
    "Going to sleep."
)

SLEEP_HINT = (
    "Say 'hello friend' or 'friend' "
    "to wake me up."
)


@dataclass(frozen=True)
class InputResponse:

    text: str = ""

    should_exit: bool = False

    is_error: bool = False


class UnifiedInputHandler:

    def __init__(
        self,
        agent: AgentRunner,
        voice: VoiceInterface | None = None,
    ) -> None:

        self._agent = agent

        self._voice = voice

        self._wake = WakeDetector()

        self._awake = False

    # ==========================================================
    # COMMON TEXT PROCESSOR
    # ==========================================================

    async def handle(
        self,
        text: str,
        source: str = "text",
    ) -> InputResponse:

        text = text.strip()

        if not text:

            return InputResponse()

        logger.info(
            "Input source=%s text=%r",
            source,
            text,
        )

        wake = self._wake.check(
            text
        )

        # ------------------------------------------------------
        # EXIT
        # ------------------------------------------------------

        if wake.is_exit:

            return InputResponse(
                should_exit=True
            )

        # ======================================================
        # SLEEPING
        # ======================================================

        if not self._awake:

            # --------------------------------------------------
            # Not a wake phrase
            # --------------------------------------------------

            if not wake.woken:

                return InputResponse(
                    text=SLEEP_HINT
                )

            # --------------------------------------------------
            # Wake
            # --------------------------------------------------

            self._awake = True

            logger.info(
                "Assistant woke up."
            )

            # --------------------------------------------------
            # Wake + command
            # --------------------------------------------------

            if wake.task:

                logger.info(
                    "Wake + command: %r",
                    wake.task,
                )

                return await self._run_agent(
                    wake.task
                )

            # --------------------------------------------------
            # Wake only
            # --------------------------------------------------

            return InputResponse(
                text=WAKE_MESSAGE
            )

        # ======================================================
        # AWAKE
        # ======================================================

        # ------------------------------------------------------
        # Sleep
        # ------------------------------------------------------

        if wake.is_sleep:

            self._awake = False

            logger.info(
                "Assistant sleeping."
            )

            return InputResponse(
                text=SLEEP_MESSAGE
            )

        # ------------------------------------------------------
        # Normal command
        # ------------------------------------------------------

        return await self._run_agent(
            text
        )

    # ==========================================================
    # AGENT
    # ==========================================================

    async def _run_agent(
        self,
        command: str,
    ) -> InputResponse:

        command = command.strip()

        if not command:

            return InputResponse()

        logger.info(
            "Agent command=%r",
            command,
        )

        try:

            response = (
                await self._agent.respond(
                    command
                )
            )

            return InputResponse(
                text=response
            )

        except Exception:

            logger.exception(
                "Agent execution failed."
            )

            return InputResponse(
                text=(
                    "Something went wrong. "
                    "Check the logs."
                ),
                is_error=True,
            )

    # ==========================================================
    # TEXT LOOP
    # ==========================================================

    async def run_text_loop(
        self,
        shutdown_event: asyncio.Event,
        app_name: str,
    ) -> None:

        print(
            f"\n{app_name} text mode started."
        )

        print(
            "Wake:"
            " hello friend / friend"
        )

        print(
            "One-line wake + command supported."
        )

        while not shutdown_event.is_set():

            try:

                text = await asyncio.to_thread(
                    input,
                    "\nYou: ",
                )

            except (
                EOFError,
                KeyboardInterrupt,
            ):

                break

            response = await self.handle(
                text,
                source="text",
            )

            if response.text:

                print(
                    f"{app_name}: "
                    f"{response.text}"
                )

            if response.should_exit:

                shutdown_event.set()

                break

    # ==========================================================
    # VOICE LOOP
    # ==========================================================

    async def voice_wake_loop(
        self,
        shutdown_event: asyncio.Event,
        app_name: str,
    ) -> None:

        if self._voice is None:

            raise RuntimeError(
                "Voice input is not configured."
            )

        print(
            f"\n{app_name} voice mode started."
        )

        print(
            "Say:"
        )

        print(
            "  hello friend"
        )

        print(
            "or:"
        )

        print(
            "  hello friend open youtube"
        )

        while not shutdown_event.is_set():

            print(
                "\n🎤 Listening..."
            )

            try:

                transcript = (
                    await asyncio.to_thread(
                        self._voice.listen
                    )
                )

            except Exception:

                logger.exception(
                    "Voice input failed."
                )

                print(
                    "Voice input failed."
                )

                continue

            if not transcript:

                continue

            print(
                f"👂 Heard: {transcript}"
            )

            response = await self.handle(
                transcript,
                source="voice",
            )

            if response.text:

                print(
                    f"{app_name}: "
                    f"{response.text}"
                )

            if response.should_exit:

                shutdown_event.set()

                break