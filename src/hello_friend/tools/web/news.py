"""
News research tool.
"""

from langchain.tools import tool

from hello_friend.tools.web.search import _search


@tool
def search_news(query: str) -> str:
    """
    Search the live web for recent news about a topic.

    Use this when the user asks about current events or recent news.
    """
    query = query.strip()

    if not query:
        return "Error: news search query is required."

    try:
        return _search(f"{query} news")
    except Exception as exc:
        return f"Error: news search failed: {exc}"