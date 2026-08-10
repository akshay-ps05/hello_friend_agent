"""
Text interface.

The interface is responsible only for:
    - reading terminal input
    - displaying responses
    - handling exit commands

It does not know about LangChain, LangGraph, tools, memory,
or LLM providers.
"""

import asyncio
import logging

from rich.console import Console

from hello_friend.agent.graph import AgentRunner

logger = logging.getLogger(__name__)

EXIT_COMMANDS = {"exit", "quit", ":q"}


class TextInterface:
    """Terminal interface for Hello Friend."""

    def __init__(
        self,
        agent: AgentRunner,
        app_name: str,
    ) -> None:
        self._agent = agent
        self._app_name = app_name
        self._console = Console()

    async def run(
        self,
        shutdown_event: asyncio.Event,
    ) -> None:
        """Run the terminal input/output loop."""

        self._console.print(
            f"[bold cyan]{self._app_name}[/bold cyan] is running. "
            f"Type a message, or 'exit' to quit.\n"
        )

        while not shutdown_event.is_set():
            try:
                user_input = await asyncio.to_thread(
                    self._console.input,
                    "[green]>[/green] ",
                )
            except (EOFError, KeyboardInterrupt):
                break

            user_input = user_input.strip()

            if not user_input:
                continue

            if user_input.lower() in EXIT_COMMANDS:
                break

            try:
                response = await self._agent.respond(user_input)

                self._console.print(
                    f"[bold cyan]{self._app_name}:[/bold cyan] "
                    f"{response}\n"
                )

            except Exception:
                logger.exception(
                    "Error while generating a response"
                )

                self._console.print(
                    "[red]Something went wrong. "
                    "Check the logs.[/red]"
                )