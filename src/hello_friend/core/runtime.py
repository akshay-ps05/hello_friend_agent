"""
Application runtime.

Wires together:

    configuration
        ↓
    LLM provider
        ↓
    tools
        ↓
    LangChain agent
        ↓
    LangGraph runner
        ↓
    terminal interface

The runtime is responsible for application startup and shutdown only.
It does not contain agent logic or tool logic.
"""

import asyncio
import logging

from hello_friend.agent import AgentRunner, create_agent
from hello_friend.core.config import get_settings
from hello_friend.core.logging_setup import setup_logging
from hello_friend.interface.text import TextInterface
from hello_friend.llm import create_model
from hello_friend.tools.all import get_tools

logger = logging.getLogger(__name__)


class Application:
    """Main Hello Friend application."""

    def __init__(self) -> None:
        self._interface: TextInterface | None = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start Hello Friend."""

        settings = get_settings()

        # --------------------------------------------------------------
        # Logging
        # --------------------------------------------------------------

        setup_logging(settings.log_level)

        logger.info("%s starting up...", settings.app_name)

        try:
            # ----------------------------------------------------------
            # LLM
            # ----------------------------------------------------------

            logger.info(
                "Creating LLM provider: %s",
                settings.llm_provider,
            )

            model = create_model(settings)

            # ----------------------------------------------------------
            # Tools
            # ----------------------------------------------------------

            tools = get_tools()

            logger.info(
                "Loaded %d tools.",
                len(tools),
            )

            # ----------------------------------------------------------
            # Agent
            # ----------------------------------------------------------

            agent = create_agent(
                model=model,
                tools=tools,
            )

            # ----------------------------------------------------------
            # Agent runner
            # ----------------------------------------------------------

            runner = AgentRunner(
                agent=agent,
                thread_id="default",
            )

            # ----------------------------------------------------------
            # Terminal interface
            # ----------------------------------------------------------

            self._interface = TextInterface(
                agent=runner,
                app_name=settings.app_name,
            )

            # ----------------------------------------------------------
            # Run application
            # ----------------------------------------------------------

            await self._interface.run(
                self._shutdown_event,
            )

        except Exception:
            logger.exception(
                "Unhandled error in Hello Friend."
            )

        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Shutdown the application cleanly."""

        if self._shutdown_event.is_set():
            return

        logger.info("Shutting down...")

        self._shutdown_event.set()


def run() -> None:
    """
    Synchronous entrypoint used by main.py and __main__.py.
    """

    app = Application()

    try:
        asyncio.run(app.start())

    except KeyboardInterrupt:
        logger.info(
            "Interrupted by user — exiting."
        )