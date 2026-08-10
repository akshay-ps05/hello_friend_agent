"""
LangGraph conversation memory.

Keeps conversation state for the lifetime of the application process.

The same thread_id represents the same conversation.
"""

from langgraph.checkpoint.memory import InMemorySaver


def create_checkpointer() -> InMemorySaver:
    """
    Create the LangGraph checkpointer used by Hello Friend.
    """
    return InMemorySaver()
