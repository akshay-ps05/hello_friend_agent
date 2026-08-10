"""
Calculator tool.

Uses LangChain's @tool decorator so the function, description, and
argument schema are automatically exposed to the agent.

numexpr is used for safe mathematical expression evaluation instead
of Python eval().
"""

import numexpr
from langchain.tools import tool


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Use this for arithmetic and mathematical calculations such as
    '12 * (4 + 7)', 'sqrt(16)', '25 / 5', or '2 ** 10'.
    """
    try:
        result = numexpr.evaluate(expression).item()
    except Exception as exc:
        return f"Error: could not evaluate '{expression}': {exc}"

    return str(result)