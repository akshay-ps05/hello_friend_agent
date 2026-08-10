"""
Open a specific website in the user's default browser.
"""

import logging
import webbrowser

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def open_website(url: str) -> str:
    """
    Open a specific website in the user's default browser.

    Use this when the user explicitly asks to open a particular
    website, such as github.com, reddit.com, or youtube.com.

    Do not use this for general web searches or YouTube searches.
    """
    url = url.strip()

    if not url:
        return "Error: website URL is required."

    # Add HTTPS when the user gives a domain without a scheme.
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        success = webbrowser.open(url)

        if not success:
            return f"Error: could not open website '{url}'."

        return f"Opened {url}"

    except Exception as exc:
        logger.exception("Failed to open website: %s", url)
        return f"Error: could not open '{url}': {exc}"