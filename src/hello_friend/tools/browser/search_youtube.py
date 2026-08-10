"""
Search YouTube and open the results in the user's default browser.
"""

import logging
import webbrowser
from urllib.parse import quote_plus

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_youtube(query: str) -> str:
    """
    Search YouTube for a song, video, music, channel, or other
    YouTube content and open the results in the user's browser.

    Use this for requests such as:
    - "search YouTube for Python tutorials"
    - "find this song on YouTube"
    - "play relaxing music on YouTube"

    Do not use search_google for the same YouTube request.
    """
    query = query.strip()

    if not query:
        return "Error: YouTube search query is required."

    try:
        url = (
            "https://www.youtube.com/results"
            f"?search_query={quote_plus(query)}"
        )

        success = webbrowser.open(url)

        if not success:
            return f"Error: could not open YouTube search for '{query}'."

        return f"Searched YouTube for '{query}'."

    except Exception as exc:
        logger.exception(
            "Failed to search YouTube for query: %s",
            query,
        )
        return f"Error: could not search YouTube: {exc}"