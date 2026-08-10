"""
Hello Friend agent creation.

Creates the LangChain agent with LangGraph conversation persistence.
"""

from typing import Any

from langchain.agents import create_agent as langchain_create_agent

from hello_friend.agent.prompt import SYSTEM_PROMPT
from hello_friend.memory.checkpointer import create_checkpointer


def create_agent(
    model: Any,
    tools: list[Any],
) -> Any:
    """
    Create the Hello Friend agent.

    The LangGraph checkpointer keeps conversation state for each
    conversation thread.
    """

    checkpointer = create_checkpointer()

    return langchain_create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        name="hello_friend",
        checkpointer=checkpointer,
    )