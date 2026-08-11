"""
Application runtime.

Wires:

configuration
    ↓
NVIDIA LLM
    ↓
tools
    ↓
LangChain agent
    ↓
LangGraph runner
    ↓
UnifiedInputHandler
    ├── text
    └── voice
          ↓
      NVIDIA Whisper
          ↓
         text

Output:
    text only
"""

from __future__ import annotations

import asyncio
import logging

from hello_friend.agent import (
    AgentRunner,
    create_agent,
)

from hello_friend.core.config import (
    get_settings,
)

from hello_friend.core.logging_setup import (
    setup_logging,
)

from hello_friend.interface import (
    TextInterface,
    UnifiedInputHandler,
    VoiceInterface,
)

from hello_friend.llm import (
    create_model,
)

from hello_friend.stt import (
    NVIDIAWhisperSTT,
)

from hello_friend.tools.all import (
    get_tools,
)


logger = logging.getLogger(
    __name__
)


class Application:
    """
    Main Hello Friend application.
    """

    def __init__(self) -> None:

        self._handler: (
            UnifiedInputHandler | None
        ) = None

        self._shutdown_event = (
            asyncio.Event()
        )

    # ==========================================================
    # START
    # ==========================================================

    async def start(self) -> None:
        """
        Start Hello Friend.
        """

        settings = get_settings()

        setup_logging(
            settings.log_level
        )

        logger.info(
            "%s starting up...",
            settings.app_name,
        )

        try:

            # ==================================================
            # VALIDATE
            # ==================================================

            self._validate_settings(
                settings
            )

            # ==================================================
            # LLM
            # ==================================================

            logger.info(
                "Creating LLM provider: %s",
                settings.llm_provider,
            )

            model = create_model(
                settings
            )

            # ==================================================
            # TOOLS
            # ==================================================

            tools = get_tools()

            logger.info(
                "Loaded %d tools.",
                len(tools),
            )

            # ==================================================
            # AGENT
            # ==================================================

            logger.info(
                "Creating LangChain agent..."
            )

            agent = create_agent(
                model=model,
                tools=tools,
            )

            # ==================================================
            # LANGGRAPH RUNNER
            # ==================================================

            runner = AgentRunner(
                agent=agent,
                thread_id="default",
            )

            # ==================================================
            # VOICE
            # ==================================================

            voice_input = None

            if settings.input_mode in {
                "voice",
                "both",
            }:

                logger.info(
                    "Creating NVIDIA Whisper STT..."
                )

                stt = NVIDIAWhisperSTT(
                    api_key=(
                        settings.nvidia_api_key
                    ),
                    function_id=(
                        settings.nvidia_stt_function_id
                    ),
                    server=(
                        settings.nvidia_riva_server
                    ),
                    model=(
                        settings.stt_model
                    ),
                    language=(
                        settings.stt_language
                    ),
                    sample_rate=(
                        settings.sample_rate
                    ),
                )

                voice_input = VoiceInterface(
                    stt=stt,
                    sample_rate=settings.sample_rate,
                    min_record_seconds=(
                        settings.min_record_seconds
                    ),
                    max_record_seconds=(
                        settings.max_record_seconds
                    ),
                    silence_threshold=(
                        settings.silence_threshold
                    ),
                    silence_duration=(
                        settings.silence_duration
                    ),
                    start_timeout=(
                        settings.start_timeout
                    ),
                )

            # ==================================================
            # UNIFIED HANDLER
            # ==================================================

            self._handler = (
                UnifiedInputHandler(
                    agent=runner,
                    voice=voice_input,
                )
            )

            # ==================================================
            # INPUT MODE
            # ==================================================

            if settings.input_mode == "text":

                await self._run_text(
                    settings.app_name
                )

            elif settings.input_mode == "voice":

                await self._run_voice(
                    settings.app_name
                )

            elif settings.input_mode == "both":

                await self._run_both(
                    settings.app_name
                )

            else:

                raise ValueError(
                    "INPUT_MODE must be "
                    "'text', 'voice', or 'both'."
                )

        except Exception:

            logger.exception(
                "Unhandled error in Hello Friend."
            )

        finally:

            await self.shutdown()

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_settings(
        settings,
    ) -> None:
        """
        Validate configuration.
        """

        if settings.llm_provider.lower() == "nvidia":

            if not settings.nvidia_api_key:

                raise RuntimeError(
                    "NVIDIA_API_KEY is required "
                    "for NVIDIA LLM."
                )

        if settings.input_mode in {
            "voice",
            "both",
        }:

            if not settings.nvidia_api_key:

                raise RuntimeError(
                    "NVIDIA_API_KEY is required "
                    "for NVIDIA Whisper STT."
                )

        if settings.output_mode != "text":

            raise ValueError(
                "This version supports "
                "OUTPUT_MODE=text only."
            )

    # ==========================================================
    # TEXT
    # ==========================================================

    async def _run_text(
        self,
        app_name: str,
    ) -> None:

        if self._handler is None:

            raise RuntimeError(
                "Handler not initialized."
            )

        interface = TextInterface(
            handler=self._handler,
            app_name=app_name,
        )

        await interface.run(
            self._shutdown_event
        )

    # ==========================================================
    # VOICE
    # ==========================================================

    async def _run_voice(
        self,
        app_name: str,
    ) -> None:

        if self._handler is None:

            raise RuntimeError(
                "Handler not initialized."
            )

        await self._handler.voice_wake_loop(
            self._shutdown_event,
            app_name,
        )

    # ==========================================================
    # BOTH
    # ==========================================================

    async def _run_both(
        self,
        app_name: str,
    ) -> None:

        if self._handler is None:

            raise RuntimeError(
                "Handler not initialized."
            )

        text_task = asyncio.create_task(
            self._handler.run_text_loop(
                self._shutdown_event,
                app_name,
            )
        )

        voice_task = asyncio.create_task(
            self._handler.voice_wake_loop(
                self._shutdown_event,
                app_name,
            )
        )

        done, pending = await asyncio.wait(
            {
                text_task,
                voice_task,
            },
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:

            task.cancel()

        await asyncio.gather(
            *pending,
            return_exceptions=True,
        )

        for task in done:

            exception = (
                task.exception()
            )

            if exception:

                raise exception

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    async def shutdown(self) -> None:
        """
        Shutdown application cleanly.
        """

        if self._shutdown_event.is_set():

            return

        logger.info(
            "Shutting down..."
        )

        self._shutdown_event.set()


def run() -> None:
    """
    Synchronous entry point.

    Run with:

        python -m hello_friend
    """

    app = Application()

    try:

        asyncio.run(
            app.start()
        )

    except KeyboardInterrupt:

        logger.info(
            "Interrupted by user — exiting."
        )