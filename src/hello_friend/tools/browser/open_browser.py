"""
Open the user's default web browser.

This is a LangChain tool. It opens the browser without performing
a search or opening a specific website.
"""

import logging
import webbrowser

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def open_browser() -> str:
    """
    Open the user's default web browser.

    Use this only when the user explicitly wants to open the browser
    without specifying a website, search, video, or other destination.
    """
    try:
        success = webbrowser.open("https://www.google.com")

        if not success:
            return "Error: could not open the default web browser."

        return "Opened the default web browser."

    except Exception as exc:
        logger.exception("Failed to open the default browser")
        return f"Error: could not open the browser: {exc}"