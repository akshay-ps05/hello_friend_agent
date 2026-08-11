"""
Text terminal interface.

Only responsible for terminal I/O.
"""

from __future__ import annotations

import asyncio

from hello_friend.interface.unified import (
    UnifiedInputHandler,
)


class TextInterface:

    def __init__(
        self,
        handler: UnifiedInputHandler,
        app_name: str,
    ) -> None:

        self._handler = handler
        self._app_name = app_name

    async def run(
        self,
        shutdown_event: asyncio.Event,
    ) -> None:

        await self._handler.run_text_loop(
            shutdown_event,
            self._app_name,
        )