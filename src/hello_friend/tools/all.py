from hello_friend.tools.browser import (
    open_browser,
    open_website,
    search_google,
    search_youtube,
)

from hello_friend.tools.math import calculator

from hello_friend.tools.system import (
    open_application,
    close_application,
)

from hello_friend.tools.web import (
    web_search,
    fetch_webpage,
    extract_content,
    search_news,
    search_weather,
    search_sports,
)

# Add your date/time tools when created.

ALL_TOOLS = [
    calculator,

    open_browser,
    open_website,
    search_google,
    search_youtube,

    open_application,
    close_application,

    web_search,
    fetch_webpage,
    extract_content,
    search_news,
    search_weather,
    search_sports,
]


def get_tools() -> list:
    """Return all tools available to Hello Friend."""
    return ALL_TOOLS.copy()