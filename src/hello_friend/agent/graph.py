"""
Hello Friend agent runtime.

Provides a small interface around the LangGraph-backed agent.
"""

from typing import Any


class AgentRunner:
    """
    Runs the Hello Friend agent while preserving conversation memory.
    """

    def __init__(
        self,
        agent: Any,
        thread_id: str = "default",
    ) -> None:
        self._agent = agent
        self._thread_id = thread_id

    async def respond(self, user_input: str) -> str:
        """
        Send a message while preserving the conversation history
        associated with this thread.
        """

        if not user_input.strip():
            return ""

        result = await self._agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": self._thread_id,
                }
            },
        )

        return self._extract_response(result)

    @staticmethod
    def _extract_response(result: dict[str, Any]) -> str:
        """Extract the final assistant response."""

        messages = result.get("messages", [])

        if not messages:
            return ""

        final_message = messages[-1]
        content = getattr(final_message, "content", "")

        if isinstance(content, str):
            return content

        return str(content)