"""
Search Google and open the results in the user's default browser.
"""

import logging
import webbrowser
from urllib.parse import quote_plus

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_google(query: str) -> str:
    """
    Search Google for a general web query and open the results
    in the user's default browser.

    Use this for general web searches.

    Do not use this for YouTube/music/video searches. Use
    search_youtube instead.
    """
    query = query.strip()

    if not query:
        return "Error: Google search query is required."

    try:
        url = f"https://www.google.com/search?q={quote_plus(query)}"

        success = webbrowser.open(url)

        if not success:
            return f"Error: could not open Google search for '{query}'."

        return f"Searched Google for '{query}'."

    except Exception as exc:
        logger.exception(
            "Failed to search Google for query: %s",
            query,
        )
        return f"Error: could not search Google: {exc}"